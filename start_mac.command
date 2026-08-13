#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "=================================================="
echo "🚀 InstaPostingPRJ 카드뉴스 웹 서비스를 시작합니다..."
echo "=================================================="

# Open Browser after 2 seconds
(sleep 2 && open http://localhost:8000) &

# Run FastAPI Web Server via venv python
if [ -f "venv/bin/python" ]; then
    venv/bin/python main.py
else
    python3 main.py
fi
