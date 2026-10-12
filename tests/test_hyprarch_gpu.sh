#!/usr/bin/env bash
# Uso: bash test_hyprarch_gpu.sh ./hyprarch-gpu
# Solo lectura; no necesita root ni GPU real.
# shellcheck disable=SC2034,SC2329 # Usados indirectamente por eval.
set -uo pipefail

GPU=${1:-./hyprarch-gpu}
[[ -r $GPU ]] || { printf 'No se puede leer %s\n' "$GPU" >&2; exit 2; }
SOURCE=$(<"$GPU")

# Aislar exclusivamente el estado instalado del host.
MARK='driver_installed() {'
[[ $SOURCE == *"$MARK"* ]] || {
    echo 'Actualizar mock driver_installed' >&2
    exit 2
}
SOURCE=${SOURCE/"$MARK"/'driver_installed() { (( TEST_DRIVER )); return; '}
PASS=0 FAIL=0

run() (
    set +e
    TEST_DRIVER=$2
    HYPRARCH_LSPCI=/__hyprarch_test__/lspci.txt

    # lspci_out sigue leyendo HYPRARCH_LSPCI mediante cat.
    cat() {
        if [[ ${1:-} == "$HYPRARCH_LSPCI" ]]; then
            printf '%s\n' "$SAMPLE"
        else
            command cat "$@"
        fi
    }

    readlink() {
        case ${!#} in
            /sys/bus/pci/devices/*/driver) (( TEST_DRIVER )) && printf '/sys/bus/pci/drivers/nvidia
' || return 1 ;;
            *pci-0000:00:02.0-card) printf '/dev/dri/card0\n' ;;
            *pci-0000:01:00.0-card) printf '/dev/dri/card1\n' ;;
            *pci-0000:02:00.0-card) printf '/dev/dri/card2\n' ;;
            *) return 1 ;;
        esac
    }

    # $1 selecciona solamente un subcomando de consulta.
    eval "$SOURCE"
)

check() {
    local sub=$1 installed=$2 expected=$3 actual rc=0
    actual=$(run "$sub" "$installed") || rc=$?
    if [[ $rc == 0 && $actual == "$expected" ]]; then
        ((PASS+=1))
    else
        ((FAIL+=1))
        printf 'FAIL %s/%s driver=%s rc=%s\n  esperado=%q\n  obtenido=%q\n' \
            "$NAME" "$sub" "$installed" "$rc" "$expected" "$actual"
    fi
}

intel='00:02.0 VGA compatible controller [0300]: Intel Corporation HD Graphics 530 [8086:1912] (rev 06)'
amd='00:02.0 VGA compatible controller [0300]: Advanced Micro Devices, Inc. [AMD/ATI] Navi 23 [Radeon RX 6600] [1002:73ff] (rev c7)'
rtx='01:00.0 VGA compatible controller [0300]: NVIDIA Corporation GA104 [GeForce RTX 3070] [10de:2484] (rev a1)'
old='01:00.0 VGA compatible controller [0300]: NVIDIA Corporation GP104 [GeForce GTX 1080] [10de:1b80] (rev a1)'

nvpkgs='nvidia-open nvidia-utils nvidia-settings libva-nvidia-driver'
nvmods='nvidia nvidia_modeset nvidia_uvm nvidia_drm'
nvcmd='nvidia_drm.modeset=1 nvidia_drm.fbdev=1'
nvenv=$'LIBVA_DRIVER_NAME=nvidia\nNVD_BACKEND=direct\nGBM_BACKEND=nvidia-drm\n__GLX_VENDOR_LIBRARY_NAME=nvidia'

for NAME in rtx3070 rtx5080 gtx1080 gtx1660 rx6600 hd530 \
            intel_rtx vbox dos_amd amd_rtx t1000 intel_gtx1080; do
    packages='' modules='' cmdline='' live='' installed=''
    modern=0 hybrid=0

    case $NAME in
        rtx3070)
            SAMPLE=$rtx
            modern=1; label='NVIDIA moderna' ;;
        rtx5080)
            SAMPLE='01:00.0 VGA compatible controller [0300]: NVIDIA Corporation GB203 [GeForce RTX 5080] [10de:2c02] (rev a1)'
            modern=1; label='NVIDIA moderna' ;;
        gtx1080)
            SAMPLE=$old; label='NVIDIA antigua' ;;
        gtx1660)
            SAMPLE='01:00.0 VGA compatible controller [0300]: NVIDIA Corporation TU116 [GeForce GTX 1660] [10de:2184] (rev a1)'
            modern=1; label='NVIDIA moderna' ;;
        rx6600)
            SAMPLE=$amd
            live='LIBVA_DRIVER_NAME=radeonsi'; label='AMD:' ;;
        hd530)
            SAMPLE=$intel
            live=''; label='Intel:' ;;
        intel_rtx)
            SAMPLE="$intel"$'\n'"${rtx/'VGA compatible controller [0300]'/'3D controller [0302]'}"
            modern=1; hybrid=1; label='NVIDIA moderna'
            live='AQ_DRM_DEVICES=/dev/dri/card0:/dev/dri/card1' ;;
        vbox)
            SAMPLE='00:02.0 VGA compatible controller [0300]: InnoTek Systemberatung GmbH VirtualBox Graphics Adapter [80ee:beef]'
            label='No detecto' ;;
        dos_amd)
            SAMPLE="$amd"$'\n'"${amd/00:02.0/02:00.0}"
            live='LIBVA_DRIVER_NAME=radeonsi'; label='AMD:' ;;
        amd_rtx)
            SAMPLE="$amd"$'\n'"$rtx"
            modern=1; hybrid=1; label='NVIDIA moderna'
            live=$'AQ_DRM_DEVICES=/dev/dri/card0:/dev/dri/card1\nLIBVA_DRIVER_NAME=radeonsi' ;;
        t1000)
            SAMPLE='01:00.0 VGA compatible controller [0300]: NVIDIA Corporation TU117GL [T1000] [10de:1fb9] (rev a1)'
            modern=1; label='NVIDIA moderna' ;;
        intel_gtx1080)
            SAMPLE="$intel"$'\n'"$old"
            label='NVIDIA antigua'
            live='AQ_DRM_DEVICES=/dev/dri/card0:/dev/dri/card1' ;;
    esac

    installed=$live
    if (( modern )); then
        packages=$nvpkgs modules=$nvmods cmdline=$nvcmd
        if (( hybrid )); then
            packages+=$'\n''nvidia-prime'
        else
            installed=$nvenv
        fi
    fi

    check packages 0 "$packages"
    check modules 0 "$modules"
    check cmdline 0 "$cmdline"
    check env 0 "$live"
    check env 1 "$installed"

    rc=0
    actual=$(run status 0) || rc=$?
    count=$(printf '%s\n' "$actual" |
        awk '$2 ~ /^(intel|amd|nvidia|otro)$/ { n++ } END { print n+0 }')
    expected_count=$(printf '%s\n' "$SAMPLE" | awk 'END { print NR }')

    if [[ $rc == 0 && $actual == *"$label"* && $count == "$expected_count" ]]; then
        ((PASS+=1))
    else
        ((FAIL+=1))
        printf 'FAIL %s/status rc=%s tarjetas=%s/%s etiqueta=%s\n' \
            "$NAME" "$rc" "$count" "$expected_count" "$label"
    fi
done

printf 'Resultado: %d OK; %d FAIL\n' "$PASS" "$FAIL"
(( FAIL == 0 ))
