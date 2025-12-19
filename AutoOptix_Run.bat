@echo off
setlocal enabledelayedexpansion
echo ========================================
echo Starting AutoOptix...
echo ========================================
cd /d %~dp0

REM Check if venv exists
if not exist ".venv" (
    echo Virtual environment not found. Installing now...
    echo.
    call AutoOptix_Install.bat
    if !errorlevel! neq 0 (
        echo Installation failed. Please check the error messages above.
        pause
        exit /b 1
    )
)

REM Activate venv
call .venv\Scripts\activate.bat

REM Launch Streamlit (let Streamlit open the browser itself)
python -m streamlit run "AutoOptix_Overview.py"
