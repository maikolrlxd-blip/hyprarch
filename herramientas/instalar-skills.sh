#!/usr/bin/env bash
# Reinstala las skills de Claude de Maikol, con las versiones (commits) fijadas y revisadas el 2026-10-22.
# Uso: ./instalar-skills.sh [carpeta_destino]
#   Sin argumento instala en las TRES IAs (mismo formato SKILL.md):
#     Claude Code        ~/.claude/skills
#     Codex / ChatGPT    ~/.agents/skills                  (doc oficial de OpenAI)
#     Antigravity        ~/.gemini/antigravity/skills      (codelab oficial de Google)
# Solo clona (sparse) y copia; NO ejecuta nada de lo descargado. Excluye scripts/ de impeccable
# (ese lanzador descarga y ejecuta un binario) y los corpus de prueba.
set -euo pipefail
if [ $# -ge 1 ]; then TARGETS=("$1"); else
  TARGETS=("$HOME/.claude/skills" "$HOME/.agents/skills" "$HOME/.gemini/antigravity/skills"); fi
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
DEST="$TMP/out"; mkdir -p "$DEST"   # se prepara una vez y luego se copia a cada IA

# repo | commit fijado | rutas (sparse) | origen -> se copia cada carpeta nombrada
get() {  # get <repo> <sha> <ruta_sparse...>
  local repo=$1 sha=$2; shift 2
  local d="$TMP/${repo//\//__}"
  git clone -q --depth 1 --filter=blob:none --sparse "https://github.com/$repo" "$d"
  git -C "$d" sparse-checkout set "$@"
  if git -C "$d" fetch -q --depth 1 origin "$sha" 2>/dev/null && git -C "$d" checkout -q "$sha" 2>/dev/null; then :; else
    echo "  aviso: no pude fijar $repo@${sha:0:7}; uso la ultima version (revisala)" >&2; fi
  echo "$d"
}
put() {  # put <carpeta_origen> [nombre]
  local src=$1 name=${2:-$(basename "$1")}
  rm -rf "$DEST/$name"; cp -r "$src" "$DEST/$name"
  find "$DEST/$name" -name node_modules -prune -exec rm -rf {} + 2>/dev/null || true
  find "$DEST/$name" -type d -name test-corpus -prune -exec rm -rf {} + 2>/dev/null || true
  echo "  + $name"
}

echo "Agent Skills (addyosmani)"
d=$(get addyosmani/agent-skills aeac41d4d005999432bb7312f7ff06383a91d59d skills/debugging-and-error-recovery skills/source-driven-development skills/security-and-hardening skills/code-review-and-quality)
for s in debugging-and-error-recovery source-driven-development security-and-hardening code-review-and-quality; do put "$d/skills/$s"; done

echo "Emil Kowalski"
d=$(get emilkowalski/skills 2d228630ba1446365f614a108cb8252f1feda202 skills)
for s in emil-design-eng review-animations improve-animations animation-vocabulary find-animation-opportunities; do put "$d/skills/$s"; done

echo "taste-skill"
d=$(get Leonxlnx/taste-skill 6010f91a9935f1c167dfc500fb1a475681892e6b skills/taste-skill)
put "$d/skills/taste-skill"

echo "impeccable (sin scripts/)"
d=$(get pbakaus/impeccable 8644175285360c166e57b1e35ecadfbc85ff5209 plugin/skills/impeccable)
put "$d/plugin/skills/impeccable"; rm -rf "$DEST/impeccable/scripts"

echo "Remotion (12)"
d=$(get remotion-dev/skills 039e8a2fc78b67efc228d5645367838b85818a1c skills)
for s in "$d"/skills/*/; do put "${s%/}"; done

echo "HyperFrames"
d=$(get heygen-com/hyperframes 4371981b740d92f70e520cfbec34db68a1c93434 skills)
for s in figma hyperframes hyperframes-cli hyperframes-registry media-use remotion-to-hyperframes slideshow; do put "$d/skills/$s"; done

echo
N=$(find "$DEST" -maxdepth 2 -name SKILL.md | wc -l)
for t in "${TARGETS[@]}"; do
  mkdir -p "$t"
  for s in "$DEST"/*/; do n=$(basename "$s"); rm -rf "$t/$n"; cp -r "$s" "$t/$n"; done
  echo "Listo: $N skills en $t"
done
echo "Reinicia cada IA (Claude Code, Codex, Antigravity) para que las cargue."
echo "PRIVACIDAD: 'media-use' de HyperFrames manda estadisticas de uso a PostHog. Para apagarlo: DO_NOT_TRACK=1 (o HYPERFRAMES_NO_TELEMETRY=1)."
