# Enregistre une tâche Windows quotidienne pour la pipeline Deribit BTC options
# Usage (PowerShell en admin NON requis pour tâche utilisateur) :
#   .\data\scripts\install_windows_scheduler.ps1
#   .\data\scripts\install_windows_scheduler.ps1 -Time "00:15" -Uninstall

param(
    [string]$Time = "",
    [switch]$Uninstall
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$TaskName = if ($env:PIPELINE_TASK_NAME) { $env:PIPELINE_TASK_NAME } else { "DeribitBTCOptionsDaily" }

if (-not $Time) {
    $Time = if ($env:PIPELINE_SCHEDULE_TIME) { $env:PIPELINE_SCHEDULE_TIME } else { "00:15" }
}

if ($Uninstall) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "Tâche supprimée : $TaskName"
    exit 0
}

$BatPath = Join-Path $ProjectRoot "data\scripts\run_daily.bat"
if (-not (Test-Path $BatPath)) {
    throw "Fichier introuvable : $BatPath"
}

$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    Write-Warning "venv absent. Exécutez d'abord : .\data\scripts\setup_environment.ps1"
}

$Existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($Existing) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

$Action = New-ScheduledTaskAction -Execute $BatPath -WorkingDirectory $ProjectRoot
$Trigger = New-ScheduledTaskTrigger -Daily -At $Time
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 2)

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Description "ETL quotidien options BTC Deribit (raw JSON + CSV + PostgreSQL)" `
    -RunLevel Limited | Out-Null

Write-Host ""
Write-Host "Tâche planifiée créée : $TaskName"
Write-Host "  Horaire  : chaque jour à $Time (heure locale Windows)"
Write-Host "  Script   : $BatPath"
Write-Host "  Logs     : $ProjectRoot\data\logs\scheduler.log"
Write-Host "  Statut   : $ProjectRoot\data\logs\last_run.json"
Write-Host ""
Write-Host "Vérifier : Get-ScheduledTask -TaskName $TaskName"
Write-Host "Test manuel : Start-ScheduledTask -TaskName $TaskName"
Write-Host "Désinstaller : .\data\scripts\install_windows_scheduler.ps1 -Uninstall"
