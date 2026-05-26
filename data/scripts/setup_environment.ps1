# Prépare l'environnement avant la première exécution planifiée
$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
Set-Location $ProjectRoot

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    py -3 -m venv .venv
}

.\.venv\Scripts\pip.exe install -r requirements.txt
Write-Host "Environnement prêt. Installez la tâche planifiée :"
Write-Host "  .\data\scripts\install_windows_scheduler.ps1"
