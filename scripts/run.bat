@echo off
REM Uso diario
cd /d "%~dp0.."
py -3.11 -m pytest tests/ || exit /b 1
if not exist outputs\proyectos.parquet (
  echo Falta el modelo curado: construyendolo...
  py -3.11 scripts\construir-modelo.py || exit /b 1
)
py -3.11 -m streamlit run src\tablero\app.py
