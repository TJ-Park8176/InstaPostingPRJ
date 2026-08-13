@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ==================================================
echo 💻 InstaPostingPRJ Windows 1-Click Installer
echo ==================================================

python install_wizard.py

if %errorlevel% equ 0 (
    echo.
    echo 🚀 Setup finished! Launching Web App...
    call start_win.bat
) else (
    echo ❌ Setup encountered an issue. Please check messages above.
    pause
)
