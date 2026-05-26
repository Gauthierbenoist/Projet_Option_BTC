@echo off
REM Lance la pipeline en mode planifié (utilisé par le Planificateur de tâches Windows)
cd /d "%~dp0..\.."
powershell -NoProfile -ExecutionPolicy Bypass -File "data\scripts\run_daily.ps1"
exit /b %ERRORLEVEL%
