@echo off
chcp 65001 > nul
echo ==================================================
echo InstaPostingPRJ Windows Auto Installer
echo ==================================================

cd /d "%~dp0"

echo [1/4] Checking Python environment...
python --version
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    pause
    exit /b 1
)

echo.
echo [2/4] Installing Python requirements...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo [3/4] Installing Playwright Chromium browser...
python -m playwright install chromium

echo.
echo [4/4] Checking .env configuration...
if exist ".env" goto ENV_EXISTS

echo .env file not found. Creating default .env file...
echo GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE > .env
echo [NOTICE] Default .env created! Please edit .env with your real GEMINI_API_KEY.
goto FINISH

:ENV_EXISTS
echo [OK] .env file already exists.

:FINISH
echo ==================================================
echo Setup completed successfully!
echo Double-click 'start_win.bat' or run 'python main.py' to launch!
echo ==================================================
pause
