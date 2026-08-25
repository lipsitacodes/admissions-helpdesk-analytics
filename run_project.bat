@echo off
SETLOCAL
cd /d "%~dp0"

REM Prefer the project's existing virtual environment if it exists.
if exist ".venv\Scripts\python.exe" (
    set "PYTHON_CMD=.venv\Scripts\python.exe"
) else (
    where python >nul 2>nul
    if %ERRORLEVEL% NEQ 0 (
        where py >nul 2>nul
        if %ERRORLEVEL% NEQ 0 (
            echo ERROR: Python was not found on this computer.
            echo Please install Python, then run this file again.
            echo.
            pause
            exit /b 1
        )
        set "PYTHON_CMD=py"
    ) else (
        set "PYTHON_CMD=python"
    )
)

echo ======================================================
echo Starting Query_Help_Desk_AI backend application...
echo Project root: %CD%
echo.
echo Running command: %PYTHON_CMD% backend\main.py
echo ======================================================

%PYTHON_CMD% backend\main.py

if errorlevel 1 (
    echo.
    echo The backend stopped with an error.
    echo Please check the Python error message above.
    echo.
    pause
)

ENDLOCAL
