"""
Build script to generate a standalone KeyMapperPro.exe binary for Windows
"""
import subprocess
import sys

def build():
    print("Installing PyInstaller if needed...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    
    print("Building standalone KeyMapperPro.exe...")
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconsole",
        "--onefile",
        "--name=KeyMapperPro",
        "main.py"
    ]
    subprocess.run(cmd, check=True)
    print("\n[SUCCESS] KeyMapperPro.exe created in dist/ folder!")

if __name__ == "__main__":
    build()
