@echo off
REM Instalación inicial (una vez por máquina)
cd /d "%~dp0.."
if not exist "config\local.yaml" copy "config\default.yaml" "config\local.yaml" >nul
if exist "requirements.txt" python -m pip install -r requirements.txt
echo Setup OK.
