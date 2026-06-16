@echo off
cd /d "%~dp0"

:: Find Python (WorkBuddy bundled -> PATH)
set "PY="
for /d %%d in ("%USERPROFILE%\.workbuddy\binaries\python\versions\3.*") do (
    if exist "%%d\pythonw.exe" set "PY=%%d\pythonw.exe"
)
if "%PY%"=="" (
    where pythonw >nul 2>&1 && set "PY=pythonw.exe"
)
if "%PY%"=="" (
    where python  >nul 2>&1 && set "PY=python.exe"
)
if "%PY%"=="" (
    echo Python not found in WorkBuddy or PATH.
    pause
    exit /b 1
)

:: Check pywebview
"%PY%" -c "import webview" >nul 2>&1
if errorlevel 1 (
    echo pywebview not installed. Installing...
    "%PY%" -m pip install pywebview
    if errorlevel 1 (
        echo Failed to install pywebview.
        pause
        exit /b 1
    )
)

:: Launch
start "" "%PY%" app.pyw
exit /b
