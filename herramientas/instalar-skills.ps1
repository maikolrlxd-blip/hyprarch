# Reinstala las skills de Claude de Maikol en Windows, con las versiones (commits) fijadas y revisadas el 2026-10-22.
# Uso (PowerShell):  powershell -ExecutionPolicy Bypass -File instalar-skills.ps1
# Sin -Dest instala en las TRES IAs (mismo formato SKILL.md):
#   Claude Code      %USERPROFILE%\.claude\skills
#   Codex / ChatGPT  %USERPROFILE%\.agents\skills              (doc oficial de OpenAI)
#   Antigravity      %USERPROFILE%\.gemini\antigravity\skills  (codelab oficial de Google)
# Requiere Git. Solo clona (sparse) y copia; NO ejecuta nada de lo descargado.
# Excluye scripts\ de impeccable (ese lanzador descarga y ejecuta un binario) y los corpus de prueba.
param([string[]]$Targets = @("$env:USERPROFILE\.claude\skills", "$env:USERPROFILE\.agents\skills", "$env:USERPROFILE\.gemini\antigravity\skills"))
$ErrorActionPreference = "Stop"
$Tmp = Join-Path $env:TEMP ("skills_" + [guid]::NewGuid().ToString("N"))
$Dest = Join-Path $Tmp "out"   # se prepara una vez y luego se copia a cada IA
New-Item -ItemType Directory -Force -Path $Tmp, $Dest | Out-Null

function Get-Repo($repo, $sha, [string[]]$paths) {
    $d = Join-Path $Tmp ($repo -replace '/', '__')
    git clone -q --depth 1 --filter=blob:none --sparse "https://github.com/$repo" $d
    git -C $d sparse-checkout set @paths
    git -C $d fetch -q --depth 1 origin $sha 2>$null
    git -C $d checkout -q $sha 2>$null
    if ($LASTEXITCODE -ne 0) { Write-Host "  aviso: no pude fijar $repo@$($sha.Substring(0,7)); uso la ultima version (revisala)" -ForegroundColor Yellow }
    return $d
}
function Put-Skill($src, $name) {
    if (-not $name) { $name = Split-Path $src -Leaf }
    $target = Join-Path $Dest $name
    if (Test-Path $target) { Remove-Item -Recurse -Force $target }
    Copy-Item -Recurse $src $target
    Get-ChildItem $target -Recurse -Directory -Include node_modules, test-corpus -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "  + $name"
}

Write-Host "Agent Skills (addyosmani)"
$d = Get-Repo "addyosmani/agent-skills" "aeac41d4d005999432bb7312f7ff06383a91d59d" @("skills/debugging-and-error-recovery","skills/source-driven-development","skills/security-and-hardening","skills/code-review-and-quality")
foreach ($s in "debugging-and-error-recovery","source-driven-development","security-and-hardening","code-review-and-quality") { Put-Skill "$d\skills\$s" }

Write-Host "Emil Kowalski"
$d = Get-Repo "emilkowalski/skills" "2d228630ba1446365f614a108cb8252f1feda202" @("skills")
foreach ($s in "emil-design-eng","review-animations","improve-animations","animation-vocabulary","find-animation-opportunities") { Put-Skill "$d\skills\$s" }

Write-Host "taste-skill"
$d = Get-Repo "Leonxlnx/taste-skill" "6010f91a9935f1c167dfc500fb1a475681892e6b" @("skills/taste-skill")
Put-Skill "$d\skills\taste-skill"

Write-Host "impeccable (sin scripts)"
$d = Get-Repo "pbakaus/impeccable" "8644175285360c166e57b1e35ecadfbc85ff5209" @("plugin/skills/impeccable")
Put-Skill "$d\plugin\skills\impeccable"
Remove-Item -Recurse -Force (Join-Path $Dest "impeccable\scripts") -ErrorAction SilentlyContinue

Write-Host "Remotion (12)"
$d = Get-Repo "remotion-dev/skills" "039e8a2fc78b67efc228d5645367838b85818a1c" @("skills")
foreach ($s in Get-ChildItem "$d\skills" -Directory) { Put-Skill $s.FullName }

Write-Host "HyperFrames"
$d = Get-Repo "heygen-com/hyperframes" "4371981b740d92f70e520cfbec34db68a1c93434" @("skills")
foreach ($s in "figma","hyperframes","hyperframes-cli","hyperframes-registry","media-use","remotion-to-hyperframes","slideshow") { Put-Skill "$d\skills\$s" }

$n = (Get-ChildItem $Dest -Directory | Where-Object { Test-Path "$($_.FullName)\SKILL.md" }).Count
foreach ($t in $Targets) {
    New-Item -ItemType Directory -Force -Path $t | Out-Null
    foreach ($s in Get-ChildItem $Dest -Directory) {
        $to = Join-Path $t $s.Name
        if (Test-Path $to) { Remove-Item -Recurse -Force $to }
        Copy-Item -Recurse $s.FullName $to
    }
    Write-Host "Listo: $n skills en $t"
}
Remove-Item -Recurse -Force $Tmp -ErrorAction SilentlyContinue
Write-Host "Reinicia cada IA (Claude Code, Codex, Antigravity) para que las cargue."
Write-Host "PRIVACIDAD: 'media-use' de HyperFrames manda estadisticas de uso a PostHog. Para apagarlo: setx DO_NOT_TRACK 1" -ForegroundColor Cyan
