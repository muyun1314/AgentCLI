@echo off
cd /d "%~dp0"

:: Find Python (WorkBuddy bundled or PATH)
set "PY="
for /d %%d in ("%USERPROFILE%\.workbuddy\binaries\python\versions\3.*") do (
    if exist "%%d\python.exe" set "PY=%%d\python.exe"
)
if "%PY%"=="" (
    where python >nul 2>&1 && set "PY=python.exe"
)
if "%PY%"=="" (
    echo Cannot find Python. Please install Python or run from WorkBuddy terminal.
    timeout /t 5
    exit /b 1
)

echo ===== Environment Check =====
echo Python: %PY%
"%PY%" --version
echo.

echo ===== Test pywebview =====
"%PY%" -c "import webview; print('pywebview OK')" 2>&1
if %errorlevel% neq 0 (
    echo pywebview not found. Installing...
    "%PY%" -m pip install pywebview
    "%PY%" -c "import webview; print('pywebview OK')" 2>&1
    if %errorlevel% neq 0 (
        echo FAILED: pywebview import failed!
        timeout /t 5
        exit /b 1
    )
)
echo.

echo ===== Test App Import =====
"%PY%" -c "import ast; ast.parse(open('app.pyw','r',encoding='utf-8').read()); print('app.pyw syntax OK')" 2>&1
if %errorlevel% neq 0 (
    echo FAILED: App syntax check failed!
    timeout /t 5
    exit /b 1
)

echo ===== Check web/index.html =====
if exist "web\index.html" (
    echo web/index.html found.
) else (
    echo WARNING: web/index.html missing!
)
echo.

echo ===== Launching App =====
start "" "%PY%" app.pyw
timeout /t 2 >nul
echo App launched!
echo.
echo (Window stays open for 10 seconds)
timeout /t 10
