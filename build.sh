#!/usr/bin/env bash
# Construye la ISO "hyprarch" a partir del perfil oficial `releng` de archiso.
# Se ejecuta como root dentro de Arch Linux (contenedor, VM o equipo real).
set -euo pipefail
cd "$(dirname "$(readlink -f "$0")")"

# ---- Ajustes personales (editables) ---------------------------------------
ISO_NAME="hyprarch"
HOSTNAME_="hyprarch"
TIMEZONE="America/Argentina/Buenos_Aires"
LOCALE="es_AR.UTF-8"
CONSOLE_KEYMAP="la-latin1"
# ---------------------------------------------------------------------------

REPO="$PWD"
PROFILE=/tmp/hyprarch-profile
WORK=/tmp/hyprarch-work
OUT="$REPO/out"
AIR="$PROFILE/airootfs"

# Algunos contenedores no soportan el sandbox (landlock) de pacman >= 7.
SANDBOX_OFF=()
if pacman --help 2>&1 | grep -q -- '--disable-sandbox'; then
  SANDBOX_OFF=(--disable-sandbox)
  grep -q '^DisableSandbox' /etc/pacman.conf || sed -i '/^\[options\]/a DisableSandbox' /etc/pacman.conf
fi

echo "==> Instalando herramientas de compilación"
pacman -Syu --noconfirm --needed "${SANDBOX_OFF[@]}" archiso imagemagick

echo "==> Copiando perfil base releng"
rm -rf "$PROFILE" "$WORK"
cp -r /usr/share/archiso/configs/releng "$PROFILE"
if [[ ${#SANDBOX_OFF[@]} -gt 0 ]]; then
  grep -q '^DisableSandbox' "$PROFILE/pacman.conf" || sed -i '/^\[options\]/a DisableSandbox' "$PROFILE/pacman.conf"
fi

echo "==> Identidad de la ISO"
sed -i \
  -e "s|^iso_name=.*|iso_name=\"$ISO_NAME\"|" \
  -e "s|^iso_application=.*|iso_application=\"Hyprland live USB\"|" \
  -e "s|^iso_publisher=.*|iso_publisher=\"Custom build\"|" \
  "$PROFILE/profiledef.sh"

echo "==> Paquetes"
grep -vE '^\s*(#|$)' packages.extra >> "$PROFILE/packages.x86_64"

echo "==> Aplicando airootfs (configuración, dotfiles, scripts)"
# Quitar finales de línea CRLF por si el repo se editó en Windows.
find airootfs -type f -exec sed -i 's/\r$//' {} +
chmod +x airootfs/usr/local/bin/* airootfs/etc/skel/.config/hypr/scripts/*
cp -a airootfs/. "$AIR/"

echo "==> Ajustes del sistema"
echo "$HOSTNAME_" > "$AIR/etc/hostname"
printf 'LANG=%s\n' "$LOCALE" > "$AIR/etc/locale.conf"
printf 'KEYMAP=%s\n' "$CONSOLE_KEYMAP" > "$AIR/etc/vconsole.conf"
printf 'en_US.UTF-8 UTF-8\n%s UTF-8\n' "$LOCALE" > "$AIR/etc/locale.gen"
ln -sf "/usr/share/zoneinfo/$TIMEZONE" "$AIR/etc/localtime"
ln -sf /run/systemd/resolve/stub-resolv.conf "$AIR/etc/resolv.conf"

# NetworkManager sustituye a iwd/systemd-networkd; sshd no hace falta en un live.
find "$AIR/etc/systemd/system" \( -name 'iwd.service' -o -name 'systemd-networkd*' -o -name 'sshd.service' \) -delete

enable() { # enable <ruta-de-la-unidad> <target>
  local unit="$1" target="$2"
  mkdir -p "$AIR/etc/systemd/system/$target.wants"
  ln -sf "$unit" "$AIR/etc/systemd/system/$target.wants/$(basename "$unit")"
}
enable /etc/systemd/system/live-setup.service      multi-user.target
enable /usr/lib/systemd/system/NetworkManager.service multi-user.target
enable /usr/lib/systemd/system/systemd-resolved.service multi-user.target
enable /usr/lib/systemd/system/bluetooth.service   multi-user.target
# PipeWire para todos los usuarios
mkdir -p "$AIR/etc/systemd/user/sockets.target.wants" "$AIR/etc/systemd/user/default.target.wants"
ln -sf /usr/lib/systemd/user/pipewire.socket       "$AIR/etc/systemd/user/sockets.target.wants/pipewire.socket"
ln -sf /usr/lib/systemd/user/pipewire-pulse.socket "$AIR/etc/systemd/user/sockets.target.wants/pipewire-pulse.socket"
ln -sf /usr/lib/systemd/user/wireplumber.service   "$AIR/etc/systemd/user/default.target.wants/wireplumber.service"

echo "==> Fondo de pantalla"
mkdir -p "$AIR/usr/share/backgrounds"
magick -size 2560x1440 radial-gradient:'#2a2b3c-#11111b' "$AIR/usr/share/backgrounds/hyprarch.png"

echo "==> Permisos"
sed -i '/^file_permissions=(/a\
  ["/etc/sudoers.d/g_wheel"]="0:0:0440"\
  ["/usr/local/bin/live-setup"]="0:0:0755"' "$PROFILE/profiledef.sh"

echo "==> Compilando ISO (tarda unos minutos)"
mkdir -p "$OUT"
mkarchiso -v -w "$WORK" -o "$OUT" "$PROFILE"

rm -rf "$WORK"
ls -lh "$OUT"
