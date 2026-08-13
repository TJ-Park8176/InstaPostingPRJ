@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ==================================================
echo 🚀 InstaPostingPRJ 카드뉴스 웹 서비스를 시작합니다...
echo ==================================================

:: Open Web Browser Automatically after 2 seconds
start "" /b cmd /c "timeout /t 2 /nobreak > nul && start http://localhost:8000"

:: Run FastAPI Web Server
python main.py
pause
