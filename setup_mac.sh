#!/bin/bash

# InstaPostingPRJ macOS Auto Installer Script
echo "=================================================="
echo "🍎 InstaPostingPRJ macOS 환경 자동 설치를 시작합니다..."
echo "=================================================="

# Move to current script directory
cd "$(dirname "$0")"

# 1. Check Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ [오류] python3가 설치되어 있지 않습니다."
    echo "👉 Homebrew를 통해 파이썬을 먼저 설치해 주세요: brew install python"
    exit 1
fi

echo "✅ Python 3 버전 확인: $(python3 --version)"

# 2. Create Virtual Environment (venv)
if [ ! -d "venv" ]; then
    echo "📦 파이썬 가상환경(venv)을 생성합니다..."
    python3 -m venv venv
else
    echo "📦 기존 파이썬 가상환경(venv)을 활용합니다."
fi

# 3. Activate venv and install dependencies
source venv/bin/activate
echo "⬆️ pip 및 필수 라이브러리를 설치/업데이트합니다..."
pip install --upgrade pip
pip install -r requirements.txt

# 4. Install Playwright Chromium for macOS
echo "🌐 macOS용 Playwright 헤드리스 크로미엄 브라우저를 설치합니다..."
playwright install chromium

# 5. Environment File (.env) Setup
if [ ! -f ".env" ]; then
    echo "🔑 .env 환경 설정 파일이 없습니다."
    echo "GEMINI_API_KEY 입력 안내:"
    read -p "👉 Gemini API Key를 입력해 주세요 (엔터 입력 시 기본 예시 설정): " user_api_key
    if [ -z "$user_api_key" ]; then
        user_api_key="YOUR_GEMINI_API_KEY_HERE"
    fi
    echo "GEMINI_API_KEY=$user_api_key" > .env
    echo "✅ .env 파일이 성공적으로 생성되었습니다!"
else
    echo "✅ .env 파일이 준비되어 있습니다."
fi

# 6. Set Executable Permissions for start_mac.command
chmod +x setup_mac.sh start_mac.command

echo "=================================================="
echo "🎉 맥북 환경 자동 설치가 성공적으로 완료되었습니다!"
echo "👉 이제 'start_mac.command' 아이콘을 더블 클릭하면 웹 서비스가 자동 실행됩니다!"
echo "=================================================="
