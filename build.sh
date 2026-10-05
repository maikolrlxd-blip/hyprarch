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

# Edición:  personal = la del dueño (Claude Code preinstalado, "Claudito").
#           public   = para compartir: NINGUNA IA incluida; cada persona elige la suya con hyprarch-ai.
EDITION="${HYPRARCH_EDITION:-personal}"
case "$EDITION" in
  personal|public) ;;
  *) echo "ERROR: HYPRARCH_EDITION debe ser 'personal' o 'public' (llegó '$EDITION')"; exit 1 ;;
esac
echo "==> Edición: $EDITION"

REPO="$PWD"
# Directorio temporal PRIVADO (nombres fijos en /tmp permitirían enlaces simbólicos
# preparados por otro usuario y chocan entre compilaciones simultáneas).
TMPD=$(mktemp -d /tmp/hyprarch.XXXXXXXX)
trap 'rm -rf "$TMPD"' EXIT
PROFILE="$TMPD/profile"
WORK="$TMPD/work"
OUT="$REPO/out"
AIR="$PROFILE/airootfs"

# Algunos contenedores no soportan el sandbox (landlock) de pacman >= 7.
SANDBOX_OFF=()
if pacman --help 2>&1 | grep -q -- '--disable-sandbox'; then
  SANDBOX_OFF=(--disable-sandbox)
  grep -q '^DisableSandbox' /etc/pacman.conf || sed -i '/^\[options\]/a DisableSandbox' /etc/pacman.conf
fi

echo "==> Instalando herramientas de compilación"
pacman -Syu --noconfirm --needed "${SANDBOX_OFF[@]}" archiso nodejs npm

echo "==> Copiando perfil base releng"
rm -rf "$PROFILE" "$WORK"
cp -r /usr/share/archiso/configs/releng "$PROFILE"
if [[ ${#SANDBOX_OFF[@]} -gt 0 ]]; then
  grep -q '^DisableSandbox' "$PROFILE/pacman.conf" || sed -i '/^\[options\]/a DisableSandbox' "$PROFILE/pacman.conf"
fi

echo "==> Identidad de la ISO"
sed -i \
  -e "s|^iso_name=.*|iso_name=\"$ISO_NAME-$EDITION\"|" \
  -e "s|^iso_application=.*|iso_application=\"Hyprland live USB\"|" \
  -e "s|^iso_publisher=.*|iso_publisher=\"Custom build\"|" \
  "$PROFILE/profiledef.sh"

echo "==> Menú de arranque"
# Títulos propios (en ASCII: syslinux no maneja bien Unicode)
grep -rlE 'Arch Linux install medium' "$PROFILE/efiboot" "$PROFILE/syslinux" "$PROFILE/grub" 2>/dev/null \
  | xargs -r sed -i 's/Arch Linux install medium/hyprarch - Hyprland live/g'
# UEFI (systemd-boot): arranque rápido, sin pitido, sin entradas de accesibilidad ni memtest
sed -i -e 's/^timeout .*/timeout 4/' -e '/^beep/d' "$PROFILE/efiboot/loader/loader.conf"
rm -f "$PROFILE"/efiboot/loader/entries/02-* "$PROFILE"/efiboot/loader/entries/03-*
ENTRY="$PROFILE/efiboot/loader/entries/01-archiso-linux.conf"
# Entrada alternativa "detallada" (muestra los mensajes de arranque) para diagnosticar fallos
sed -e 's/^title .*/title    hyprarch - modo detallado (UEFI)/' -e 's/^sort-key.*/sort-key 02/' "$ENTRY" \
  > "$PROFILE/efiboot/loader/entries/02-hyprarch-verbose.conf"
# La entrada normal arranca en silencio
sed -i 's/^options  \(.*\)$/options  \1 quiet loglevel=3 systemd.show_status=0/' "$ENTRY"
# Espacio de escritura en RAM del sistema live: 256 MB (por defecto) no alcanza para instalar una IA
# (Claude Code pesa ~250 MB). El tope pasa a la MITAD de la RAM de cada equipo (4 GB -> 2 GB,
# 32 GB -> 16 GB); la RAM solo se usa a medida que hace falta, no se reserva.
for e in "$ENTRY" "$PROFILE/efiboot/loader/entries/02-hyprarch-verbose.conf"; do
  sed -i 's/^options  \(.*\)$/options  \1 cow_spacesize=50%/' "$e"
done
echo "--- entrada principal:"; cat "$ENTRY"

echo "==> Paquetes"
grep -vE '^\s*(#|$)' packages.extra >> "$PROFILE/packages.x86_64"

echo "==> Aplicando airootfs (configuración, dotfiles, scripts)"
# Quitar finales de línea CRLF por si el repo se editó en Windows, sin alterar imágenes.
find airootfs -type f ! -name '*.jpg' ! -name '*.png' -exec sed -i 's/\r$//' {} +
chmod +x airootfs/usr/local/bin/* airootfs/etc/skel/.config/hypr/scripts/*
cp -a airootfs/. "$AIR/"

echo "==> Archivos propios de la edición '$EDITION'"
if [[ -d "editions/$EDITION/airootfs" ]]; then
  find "editions/$EDITION/airootfs" -type f ! -name '*.jpg' ! -name '*.png' -exec sed -i 's/\r$//' {} +
  cp -a "editions/$EDITION/airootfs/." "$AIR/"
  rm -f "$AIR/.gitkeep"
fi

if [[ "$EDITION" == "personal" ]]; then
  echo "==> Claude Code (paquete oficial de npm, instalado dentro de la ISO personal)"
  # El usuario inicia sesión él mismo la primera vez (no se guarda ninguna credencial).
  npm install -g --prefix "$AIR/usr/local" --no-fund --no-audit @anthropic-ai/claude-code
  # El postinstall de npm no corre en este contexto y deja un stub en bin/claude.exe:
  # se apunta (enlace simbólico, sin duplicar 240 MB) al binario nativo ya descargado.
  CC="$AIR/usr/local/lib/node_modules/@anthropic-ai/claude-code"
  NATIVE="$CC/node_modules/@anthropic-ai/claude-code-linux-x64/claude"
  [[ -x "$NATIVE" ]] || { echo "ERROR: falta el binario nativo de Claude Code ($NATIVE)"; exit 1; }
  ln -sfn "../node_modules/@anthropic-ai/claude-code-linux-x64/claude" "$CC/bin/claude.exe"
else
  echo "==> Edición pública: no se incluye ninguna IA (se instala la elegida al primer uso con hyprarch-ai)"
  # Salvaguarda: la edición pública nunca debe llevar software propietario de IA ni credenciales.
  if find "$AIR" \( -name '@anthropic-ai' -o -path '*/@anthropic-ai/*' -o -name '.claude' -o -name '.credentials*' \) -print -quit | grep -q .; then
    echo "ERROR: la edición pública contiene archivos de una IA/credenciales"; exit 1
  fi
fi
ls -l "$AIR/usr/local/bin/" | head -20

echo "==> Ocultando del lanzador las entradas inútiles"
mkdir -p "$AIR/etc/skel/.local/share/applications"
for app in avahi-discover bssh bvnc blueman-adapters lftp qv4l2 qvidcap stoken-gui stoken-gui-small \
           thunar-bulk-rename thunar-settings xfce4-about xgps xgpsspeed vim; do
  printf '[Desktop Entry]\nType=Application\nName=%s\nHidden=true\n' "$app" \
    > "$AIR/etc/skel/.local/share/applications/$app.desktop"
done

echo "==> Ajustes del sistema"
echo "$HOSTNAME_" > "$AIR/etc/hostname"
printf 'LANG=%s\n' "$LOCALE" > "$AIR/etc/locale.conf"
printf 'KEYMAP=%s\n' "$CONSOLE_KEYMAP" > "$AIR/etc/vconsole.conf"
printf 'en_US.UTF-8 UTF-8\n%s UTF-8\n' "$LOCALE" > "$AIR/etc/locale.gen"
ln -sf "/usr/share/zoneinfo/$TIMEZONE" "$AIR/etc/localtime"
ln -sf /run/systemd/resolve/stub-resolv.conf "$AIR/etc/resolv.conf"

# NetworkManager sustituye a iwd/systemd-networkd; sshd no hace falta en un live.
find "$AIR/etc/systemd/system" \( -name 'iwd.service' -o -name 'systemd-networkd*' -o -name 'sshd.service' \) -prune -exec rm -rf {} +

# Arranque más rápido y liviano (pensado también para equipos modestos): se quitan del camino los servicios del live
# que no hacen falta para usar el escritorio. pacman-init (13 s) solo se necesita al instalar: lo hace hyprarch-install.
find "$AIR/etc/systemd/system" \( -name 'livecd-talk.service' -o -name 'pacman-init.service' -o -name 'choose-mirror.service' \) -prune -exec rm -rf {} +
ln -sf /dev/null "$AIR/etc/systemd/system/systemd-time-wait-sync.service"      # esperaba la hora de internet (9 s)
# SquashFS con zstd: descomprime mucho más rápido que xz en procesadores lentos (tamaño parecido).
sed -i "s|^airootfs_image_tool_options=.*|airootfs_image_tool_options=('-comp' 'zstd' '-Xcompression-level' '19' '-b' '1M')|" "$PROFILE/profiledef.sh"

enable() { # enable <ruta-de-la-unidad> <target>
  local unit="$1" target="$2"
  mkdir -p "$AIR/etc/systemd/system/$target.wants"
  ln -sf "$unit" "$AIR/etc/systemd/system/$target.wants/$(basename "$unit")"
}
enable /etc/systemd/system/live-setup.service      multi-user.target
enable /usr/lib/systemd/system/NetworkManager.service multi-user.target
enable /usr/lib/systemd/system/systemd-resolved.service multi-user.target
enable /usr/lib/systemd/system/bluetooth.service   multi-user.target

# Modo DESARROLLO (solo cuando se pide con HYPRARCH_DEV=1): SSH con llave para
# controlar la ISO desde una máquina virtual. NO se usa en la ISO normal.
if [[ "${HYPRARCH_DEV:-0}" == "1" ]]; then
  echo "==> Modo DESARROLLO: SSH habilitado (solo con llave)"
  sed -i "s|^iso_name=.*|iso_name=\"$ISO_NAME-$EDITION-dev\"|" "$PROFILE/profiledef.sh"
  mkdir -p "$AIR/etc/skel/.ssh"
  cp "$REPO/dev/authorized_keys" "$AIR/etc/skel/.ssh/authorized_keys"
  chmod 700 "$AIR/etc/skel/.ssh"
  chmod 600 "$AIR/etc/skel/.ssh/authorized_keys"
  enable /usr/lib/systemd/system/sshd.service multi-user.target
  mkdir -p "$AIR/etc/ssh/sshd_config.d"
  printf 'PasswordAuthentication no\nPermitRootLogin no\nPubkeyAuthentication yes\n' > "$AIR/etc/ssh/sshd_config.d/20-hyprarch-dev.conf"
fi

# PipeWire para todos los usuarios
mkdir -p "$AIR/etc/systemd/user/sockets.target.wants" "$AIR/etc/systemd/user/default.target.wants"
ln -sf /usr/lib/systemd/user/pipewire.socket       "$AIR/etc/systemd/user/sockets.target.wants/pipewire.socket"
ln -sf /usr/lib/systemd/user/pipewire-pulse.socket "$AIR/etc/systemd/user/sockets.target.wants/pipewire-pulse.socket"
ln -sf /usr/lib/systemd/user/wireplumber.service   "$AIR/etc/systemd/user/default.target.wants/wireplumber.service"

echo "==> Fondos de pantalla (ya vienen en airootfs/usr/share/backgrounds; los genera tools/make_wallpaper.py)"
ls -l "$AIR/usr/share/backgrounds/"

echo "==> Generando la paleta inicial (verde) en /etc/skel"
HOME="$AIR/etc/skel" HYPRARCH_NO_RELOAD=1 HYPRARCH_THEMES="$REPO/airootfs/usr/share/hyprarch/themes" \
  bash "$REPO/airootfs/usr/local/bin/hyprarch-theme" verde

echo "==> Permisos (mkarchiso NO conserva el bit de ejecución: hay que declararlo)"
PERMS="$TMPD/perms.txt"
{
  echo '  ["/etc/sudoers.d/g_wheel"]="0:0:0440"'
  for f in "$REPO"/airootfs/usr/local/bin/* "$REPO"/airootfs/etc/skel/.config/hypr/scripts/*; do
    echo "  [\"/${f#"$REPO/airootfs/"}\"]=\"0:0:0755\""
  done
  # Ejecutables instalados por npm (Claude Code): mkarchiso tampoco conserva su bit +x
  if [[ -d "$AIR/usr/local/lib/node_modules" ]]; then
    while IFS= read -r f; do
      echo "  [\"${f#"$AIR"}\"]=\"0:0:0755\""
    done < <(find "$AIR/usr/local/lib/node_modules" -type f -perm -u+x)
  fi
  if [[ "${HYPRARCH_DEV:-0}" == "1" ]]; then
    echo '  ["/etc/skel/.ssh"]="0:0:0700"'
    echo '  ["/etc/skel/.ssh/authorized_keys"]="0:0:0600"'
  fi
} > "$PERMS"
sed -i "/^file_permissions=(/r $PERMS" "$PROFILE/profiledef.sh"
echo "--- file_permissions añadidos:"; cat "$PERMS"

echo "==> Compilando ISO (tarda unos minutos)"
mkdir -p "$OUT"
mkarchiso -v -w "$WORK" -o "$OUT" "$PROFILE"

rm -rf "$WORK"
ls -lh "$OUT"
