@echo off
REM ----------------------------------------
REM Script para activar entorno y lanzar app
REM ----------------------------------------
cd /d "%~dp0"

REM Activar entorno virtual si existe
if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
) else (
    echo Entorno virtual no encontrado; usando Python global.
)

REM Ejecutar la app con Streamlit
streamlit run pipping_joamercu_app_streamlit.py

pause
