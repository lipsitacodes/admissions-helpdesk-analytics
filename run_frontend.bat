@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ======================================================
echo           Starting Campus AI - Frontend
echo ======================================================

set "PORT=5173"
echo [1/3] Checking and clearing port %PORT%...

for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":%PORT%" ^| findstr "LISTENING"') do (
    if not "%%p"=="" if not "%%p"=="0" (
        echo [INFO] Port %PORT% is currently occupied by PID %%p. Killing process...
        taskkill /f /pid %%p >nul 2>&1
    )
)

echo [OK] Port %PORT% is free and ready.
echo.

REM Check if Backend server is running on port 5000; if not, auto-launch it
netstat -ano | findstr ":5000" | findstr "LISTENING" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Backend server is not running on port 5000. Auto-starting backend...
    start "Campus AI - Backend" cmd /c "%~dp0run_backend.bat"
    timeout /t 2 /nobreak >nul
) else (
    echo [OK] Backend server is active on port 5000.
)
echo.

cd /d "%~dp0frontend"

REM Resolve npm command path (handles environments where node_modules/npm was in PATH)
if exist "%ProgramFiles%\nodejs\npm.cmd" (
    set "NPM_CMD=%ProgramFiles%\nodejs\npm.cmd"
) else (
    set "NPM_CMD=npm"
)

echo [2/3] Checking dependencies in frontend...
if not exist "node_modules" (
    echo [INFO] node_modules not found. Installing packages...
    call "!NPM_CMD!" install
    if errorlevel 1 (
        echo [ERROR] npm install failed. Please check your Node/npm setup.
        pause
        exit /b 1
    )
) else (
    echo [OK] Dependencies are already installed.
)
echo.

echo [3/3] Launching Vite dev server and opening in Chrome...
echo URL: http://localhost:%PORT%/
echo Press Ctrl+C in this terminal to stop the frontend server.
echo ======================================================
echo.

REM Detect Google Chrome binary
set "CHROME_BIN="
if exist "%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe" set "CHROME_BIN=%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"
if not defined CHROME_BIN if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" set "CHROME_BIN=%ProgramFiles%\Google\Chrome\Application\chrome.exe"
if not defined CHROME_BIN if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" set "CHROME_BIN=%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"

if defined CHROME_BIN (
    echo [INFO] Opening Google Chrome: http://localhost:%PORT%/
    start "" "!CHROME_BIN!" "http://localhost:%PORT%/"
) else (
    echo [INFO] Opening default browser: http://localhost:%PORT%/
    start "" "http://localhost:%PORT%/"
)

if exist "node_modules\.bin\vite.cmd" (
    call "node_modules\.bin\vite.cmd" --port %PORT%
) else (
    call "!NPM_CMD!" run dev
)

if errorlevel 1 (
    echo.
    echo [ERROR] Frontend server stopped with an error code.
    pause
)

endlocal
