#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "=================================================="
echo "🍎 InstaPostingPRJ macOS All-In-One Installer"
echo "=================================================="

python3 install_wizard.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🚀 Setup finished! Starting Web App..."
    chmod +x start_mac.command
    ./start_mac.command
fi
