@echo off
cd /d "%~dp0"
echo [1/4] Checking PyInstaller...
pip show pyinstaller >nul 2>&1 || (
    echo Installing PyInstaller...
    pip install pyinstaller
)
echo [2/4] Checking pywebview...
pip show pywebview >nul 2>&1 || (
    echo Installing pywebview...
    pip install pywebview
)
echo [3/4] Building...
pyinstaller --onefile --windowed --name "AgentCLI" ^
    --icon "logo\logo.ico" ^
    --add-data "web\index.html;web" ^
    --add-data "web\logo.png;web" ^
    --add-data "logo\logo.ico;logo" ^
    --hidden-import pythonnet ^
    --hidden-import clr_loader ^
    --hidden-import proxy_tools ^
    app.pyw
if %errorlevel% neq 0 (
    echo Build FAILED! Check errors above.
    pause
    exit /b 1
)
echo [4/4] Build complete! Output: dist\AgentCLI.exe
pause
