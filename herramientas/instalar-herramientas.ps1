# Reinstala los programas que Maikol tenia antes del reinicio de fabrica (lista de la base de conocimiento).
# Uso (PowerShell, como usuario normal; algunos instaladores pedirán permiso de administrador):
#   powershell -ExecutionPolicy Bypass -File instalar-herramientas.ps1
# Cada programa es independiente: si uno falla, sigue con los demas y al final dice cuales fallaron.
$items = @(
  @{ n="Python 3.12";            id="Python.Python.3.12" },
  @{ n="Git";                    id="Git.Git" },
  @{ n="GitHub CLI";             id="GitHub.cli" },
  @{ n="Node.js LTS";            id="OpenJS.NodeJS.LTS" },
  @{ n="Visual Studio Code";     id="Microsoft.VisualStudioCode" },
  @{ n="Obsidian";               id="Obsidian.Obsidian" },
  @{ n="Blender";                id="BlenderFoundation.Blender" },
  @{ n="shellcheck";             id="koalaman.shellcheck" },
  @{ n="Lua 5.4";                id="DEVCOM.Lua" },
  @{ n="Rufus (grabar USB)";     id="Rufus.Rufus" },
  @{ n="VirtualBox (solo hyprarch)"; id="Oracle.VirtualBox" }
)
$fallos = @()
foreach ($i in $items) {
  Write-Host "`n== $($i.n)" -ForegroundColor Cyan
  winget install -e --id $i.id --accept-package-agreements --accept-source-agreements
  if ($LASTEXITCODE -ne 0) { $fallos += $i.n }
}
Write-Host "`n== Herramientas de Python y npm (necesitan que Python y Node ya esten en el PATH: cierra y abre la terminal si fallan)" -ForegroundColor Cyan
try { python -m pip install --user ruff } catch { $fallos += "ruff" }
try { npm install -g "@openai/codex" } catch { $fallos += "Codex CLI" }
Write-Host "`nClaude Code: curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd  (y agrega %USERPROFILE%\.local\bin al PATH)"
Write-Host "Skills de Claude: powershell -ExecutionPolicy Bypass -File instalar-skills.ps1"
if ($fallos.Count) { Write-Host "`nNo se pudieron instalar: $($fallos -join ', '). Reintenta esos a mano." -ForegroundColor Yellow } else { Write-Host "`nTodo instalado." -ForegroundColor Green }
