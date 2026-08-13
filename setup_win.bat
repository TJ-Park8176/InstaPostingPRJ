@echo off
chcp 65001 > nul
echo ==================================================
echo 💻 InstaPostingPRJ 윈도우 환경 자동 설치를 시작합니다...
echo ==================================================

cd /d "%~dp0"

:: 1. Check Python
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ [오류] 파이썬(Python)이 설치되어 있지 않습니다.
    echo 👉 python.org에서 Python 3.10 이상을 설치해 주세요. (PATH 추가 옵션 체크 필수)
    pause
    exit /b 1
)

echo ✅ 파이썬 설치 확인 완료.

:: 2. Install Requirements
echo ⬆️ 필수 라이브러리를 설치합니다...
pip install --upgrade pip
pip install -r requirements.txt

:: 3. Install Playwright Chromium
echo 🌐 Playwright 크로미엄 브라우저를 설치합니다...
python -m playwright install chromium

:: 4. Environment File (.env) Check
if not exist ".env" (
    echo 🔑 .env 환경 설정 파일이 없습니다.
    echo GEMINI_API_KEY 입력 안내:
    set /p USER_KEY="👉 Gemini API Key를 입력해 주세요: "
    if "%USER_KEY%"=="" set USER_KEY=YOUR_GEMINI_API_KEY_HERE
    echo GEMINI_API_KEY=%USER_KEY% > .env
    echo ✅ .env 파일이 성공적으로 생성되었습니다.
) else (
    echo ✅ .env 파일이 준비되어 있습니다.
)

echo ==================================================
echo 🎉 윈도우 환경 자동 설치가 완료되었습니다!
echo 👉 이제 'start_win.bat' 파일을 더블 클릭하면 웹 서비스가 자동 실행됩니다!
echo ==================================================
pause
