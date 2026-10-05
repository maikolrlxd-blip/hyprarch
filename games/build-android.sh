#!/usr/bin/env bash
# Genera un proyecto Android (WebView) a partir de un juego HTML5.
# Uso: ./build-android.sh <juego> [--apk]
#   Crea ./build/<juego>-android/ listo para abrir en Android Studio.
#   Con --apk además ejecuta gradle assembleDebug (requiere Android SDK + ANDROID_HOME).
set -euo pipefail
cd "$(dirname "$0")"
game="${1:?Uso: $0 <void-survivors|stack-tower|gravity-flip|space-blaster> [--apk]}"
[[ -f "$game/index.html" ]] || { echo "No existe $game/index.html" >&2; exit 1; }
case "$game" in
  stack-tower)   name="Stack Tower";   color="#1E3A8A"; orient="portrait";;
  gravity-flip)  name="Gravity Flip";  color="#5B21B6"; orient="portrait";;
  space-blaster) name="Space Blaster"; color="#0F172A"; orient="portrait";;
  void-survivors) name="Void Survivors"; color="#1B1464"; orient="portrait";;
  *) name="$game"; color="#222222"; orient="portrait";;
esac
appid="com.hyprarch.games.$(echo "$game" | tr -d '-')"
out="build/$game-android"
rm -rf "$out"; mkdir -p build; cp -r android-template "$out"
# Copia el juego completo (index.html + js/ + css/ ...) sin las herramientas ni los materiales de la tienda.
mkdir -p "$out/app/src/main/assets"; cp -r "$game"/. "$out/app/src/main/assets/"
rm -rf "$out/app/src/main/assets"/{store,tools,node_modules}
find "$out" -type f \( -name '*.gradle' -o -name '*.xml' \) -exec sed -i \
  -e "s|__APP_ID__|$appid|g" -e "s|__APP_NAME__|$name|g" -e "s|__COLOR__|$color|g" -e "s|__ORIENTATION__|$orient|g" {} +
echo "Proyecto generado en $out ($appid)"
if [[ "${2:-}" == "--apk" ]]; then
  command -v gradle >/dev/null || { echo "Falta gradle" >&2; exit 1; }
  (cd "$out" && gradle --no-daemon assembleDebug) && echo "APK: $out/app/build/outputs/apk/debug/"
fi
