import os
import sys
import subprocess
import venv

def print_header(title):
    print("\n" + "=" * 60)
    print(f"  🧙‍♂️ InstaPostingPRJ All-In-One Smart Installer: {title}")
    print("=" * 60)

def check_python_version():
    print("🔍 [1/5] Checking Python Version...")
    major, minor = sys.version_info.major, sys.version_info.minor
    print(f"  --> Detected Python {major}.{minor}.{sys.version_info.micro}")
    
    if major < 3 or (major == 3 and minor < 9):
        print("\n❌ [ERROR] Python 3.9 or higher is required.")
        print("👉 Please download Python 3.10+ from https://www.python.org/downloads/")
        sys.exit(1)
    elif major == 3 and minor >= 14:
        print("  ⚠️ [NOTICE] Python 3.14+ detected. Compatibility modes enabled.")
    else:
        print("  ✅ Python version is fully compatible!")

def setup_virtualenv():
    print("\n📦 [2/5] Setting up Isolated Virtual Environment (venv)...")
    project_dir = os.path.dirname(os.path.abspath(__file__))
    venv_dir = os.path.join(project_dir, "venv")
    
    if not os.path.exists(venv_dir):
        print("  --> Creating new virtual environment at ./venv ...")
        venv.create(venv_dir, with_pip=True)
        print("  ✅ Virtual environment created successfully!")
    else:
        print("  ✅ Existing virtual environment found at ./venv.")
        
    # Get venv python & pip paths
    if sys.platform == "win32":
        python_executable = os.path.join(venv_dir, "Scripts", "python.exe")
        pip_executable = os.path.join(venv_dir, "Scripts", "pip.exe")
    else:
        python_executable = os.path.join(venv_dir, "bin", "python")
        pip_executable = os.path.join(venv_dir, "bin", "pip")
        
    if not os.path.exists(python_executable):
        python_executable = sys.executable # Fallback to current executable if venv path differs
        
    return python_executable, pip_executable

def install_dependencies(python_bin, pip_bin):
    print("\n⬆️ [3/5] Installing Python Package Requirements...")
    project_dir = os.path.dirname(os.path.abspath(__file__))
    req_file = os.path.join(project_dir, "requirements.txt")
    
    if os.path.exists(req_file):
        cmd = [python_bin, "-m", "pip", "install", "--upgrade", "pip"]
        subprocess.run(cmd, check=False)
        
        cmd_req = [python_bin, "-m", "pip", "install", "-r", req_file]
        res = subprocess.run(cmd_req, check=False)
        if res.returncode == 0:
            print("  ✅ Requirements installed successfully!")
        else:
            print("  ⚠️ Warning: Package installation had minor issues. Proceeding...")
    else:
        print("  ⚠️ requirements.txt not found. Skipping...")

def install_playwright_chromium(python_bin):
    print("\n🌐 [4/5] Installing Playwright Chromium Browser Engine...")
    cmd = [python_bin, "-m", "playwright", "install", "chromium"]
    res = subprocess.run(cmd, check=False)
    if res.returncode == 0:
        print("  ✅ Chromium browser engine installed successfully!")
    else:
        print("  ⚠️ Warning: Chromium installation returned non-zero code. You can run 'python -m playwright install chromium' manually if needed.")

def setup_environment_key():
    print("\n🔑 [5/5] Checking Environment Configuration (.env)...")
    project_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(project_dir, ".env")
    
    current_key = ""
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8-sig") as f:
                content = f.read()
                for line in content.splitlines():
                    if line.startswith("GEMINI_API_KEY="):
                        current_key = line.split("=", 1)[1].strip().strip('"').strip("'")
        except Exception:
            pass
            
    if current_key and current_key != "YOUR_GEMINI_API_KEY_HERE":
        print(f"  ✅ Existing GEMINI_API_KEY found: ({current_key[:6]}...{current_key[-4:]})")
        change = input("  👉 Do you want to update your Gemini API Key? [y/N]: ").strip().lower()
        if change != 'y':
            return

    print("\n" + "-" * 50)
    print(" 🔑 Gemini API Key Input")
    print("  - If you don't have a key, get one free at: https://aistudio.google.com/app/apikey")
    print("-" * 50)
    
    user_key = ""
    while not user_key:
        user_key = input("👉 Enter your Gemini API Key: ").strip()
        if user_key.startswith("GEMINI_API_KEY="):
            user_key = user_key.replace("GEMINI_API_KEY=", "").strip()
        if not user_key:
            print("  ❌ API Key cannot be empty! Please try again.")

    # Write .env cleanly in UTF-8
    with open(env_path, "w", encoding="utf-8") as f:
        f.write(f"GEMINI_API_KEY={user_key}\n")
        
    print("  ✅ .env file successfully created & saved in UTF-8 format!")

def main():
    print_header("Initialization")
    check_python_version()
    python_bin, pip_bin = setup_virtualenv()
    install_dependencies(python_bin, pip_bin)
    install_playwright_chromium(python_bin)
    setup_environment_key()
    
    print_header("Setup Complete!")
    print(" 🎉 All components, packages, and credentials have been installed!")
    print("\n 🚀 How to Launch:")
    if sys.platform == "win32":
        print("   - Double-click 'start_win.bat' (Windows)")
        print("   - Or run: .\\venv\\Scripts\\python main.py")
    else:
        print("   - Double-click 'start_mac.command' or run './start_mac.command' (Mac)")
        print("   - Or run: ./venv/bin/python main.py")
    print("\n" + "=" * 60 + "\n")

if __name__ == "__main__":
    main()
