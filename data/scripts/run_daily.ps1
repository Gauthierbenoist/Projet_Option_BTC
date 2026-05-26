# Wrapper PowerShell pour exécution planifiée (Task Scheduler / cron manuel)
$ErrorActionPreference = "Stop"

$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
Set-Location $ProjectRoot

$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    $pyCmd = Get-Command py -ErrorAction SilentlyContinue
    if ($pyCmd) { $Python = "py" }
    else {
        $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
        if (-not $pythonCmd) {
            throw "Python introuvable. Créez un venv : python -m venv .venv"
        }
        $Python = "python"
    }
}

$LogDir = Join-Path $ProjectRoot "data\logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$LogFile = Join-Path $LogDir "scheduler.log"

$Args = @("data\scripts\run_daily_pipeline.py", "--scheduled")
$Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

Add-Content -Path $LogFile -Value "[$Timestamp] Démarrage pipeline Deribit"
& $Python @Args 2>&1 | Tee-Object -FilePath $LogFile -Append
$Code = $LASTEXITCODE

if ($Code -ne 0) {
    Add-Content -Path $LogFile -Value "[$Timestamp] ERREUR code=$Code"
    exit $Code
}

Add-Content -Path $LogFile -Value "[$Timestamp] Terminé OK"
exit 0
