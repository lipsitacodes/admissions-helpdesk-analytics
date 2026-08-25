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
echo Starting the interactive manual query tester...
echo Project root: %CD%
echo.
echo Running command: %PYTHON_CMD% tools\manual_test.py
echo ======================================================

%PYTHON_CMD% tools\manual_test.py

if errorlevel 1 (
    echo.
    echo The manual tester stopped with an error.
    echo Please check the Python error message above.
    echo.
    pause
)

ENDLOCAL
