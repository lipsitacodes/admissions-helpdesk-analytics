@echo off
SETLOCAL
cd /d "%~dp0"

if not exist "requirements.txt" (
    echo ERROR: requirements.txt was not found in the project root.
    echo Expected file: %CD%\requirements.txt
    echo.
    pause
    exit /b 1
)

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
echo Installing project requirements from requirements.txt...
echo Project root: %CD%
echo.
echo Running command: %PYTHON_CMD% -m pip install -r requirements.txt
echo ======================================================

%PYTHON_CMD% -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo Package installation failed.
    echo Please check the pip output above and fix the issue.
    echo.
    pause
)

ENDLOCAL
