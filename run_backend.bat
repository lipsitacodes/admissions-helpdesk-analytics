@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

title FEESABILITY - Backend Server

echo ======================================================================
echo    FEESABILITY - Admissions Helpdesk AI Backend (CUTM)
echo ======================================================================

set "PORT=5000"
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":%PORT%" ^| findstr "LISTENING"') do (
    if not "%%p"=="" if not "%%p"=="0" (
        echo [*] Freeing port %PORT% - PID %%p...
        taskkill /f /pid %%p >nul 2>&1
    )
)

set "PYTHON_CMD="
if exist "C:\Python313\python.exe" set "PYTHON_CMD=C:\Python313\python.exe"
if not defined PYTHON_CMD if exist .venv\Scripts\python.exe set "PYTHON_CMD=%CD%\.venv\Scripts\python.exe"
if not defined PYTHON_CMD if exist backend\.venv\Scripts\python.exe set "PYTHON_CMD=%CD%\backend\.venv\Scripts\python.exe"
if not defined PYTHON_CMD (
    where python >nul 2>nul
    if not errorlevel 1 set "PYTHON_CMD=python"
)
if not defined PYTHON_CMD (
    where py >nul 2>nul
    if not errorlevel 1 set "PYTHON_CMD=py"
)

if not defined PYTHON_CMD (
    echo [ERROR] Python was not found on your system.
    pause
    exit /b 1
)

echo [*] Using Python: !PYTHON_CMD!
echo [*] Starting Flask backend on http://127.0.0.1:%PORT%...
echo ======================================================================
echo.

cd /d "%~dp0backend"
"!PYTHON_CMD!" main.py

echo.
echo ======================================================================
echo Backend server stopped.
echo ======================================================================
pause
endlocal
