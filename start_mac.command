#!/bin/bash

# InstaPostingPRJ macOS 1-Click Auto Launcher
cd "$(dirname "$0")"

echo "=================================================="
echo "🚀 InstaPostingPRJ 카드뉴스 웹 서비스를 시작합니다..."
echo "=================================================="

# Check venv
if [ ! -d "venv" ]; then
    echo "⚠️ 가상환경(venv)이 구성되지 않았습니다."
    echo "👉 터미널에서 './setup_mac.sh'를 먼저 실행해 주세요."
    read -p "엔터를 누르면 종료합니다..."
    exit 1
fi

# Activate Virtual Environment
source venv/bin/activate

# Open Web Browser Automatically after 1.5 seconds in background
(sleep 1.5 && open "http://localhost:8000") &

# Run FastAPI Web Server
python3 main.py
