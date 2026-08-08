"""
KeyMapper Pro — Production Executable & Installer Builder
Packages the project into a standalone single-file Windows executable (dist/KeyMapperPro.exe)
"""

import os
import sys
import shutil
import subprocess

sys.stdout.reconfigure(encoding='utf-8')

def build_installer():
    print("==========================================================")
    print("[+] BUILDING STANDALONE EXECUTABLE & INSTALLER BUNDLE")
    print("==========================================================")
    
    # 1. Install PyInstaller if missing
    print("\n[Step 1/3] Ensuring PyInstaller is installed...")
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller via pip...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)

    # 2. Build PyInstaller Command
    print("\n[Step 2/3] Compiling KeyMapperPro into single standalone binary...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(script_dir, "main.py")
    profiles_dir = os.path.join(script_dir, "profiles")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconsole",
        "--onefile",
        "--name=KeyMapperPro",
        f"--add-data={profiles_dir}{os.path.pathsep}profiles",
        "--clean",
        main_script
    ]
    
    subprocess.run(cmd, check=True, cwd=script_dir)

    # 3. Verify Output Executable
    exe_path = os.path.join(script_dir, "dist", "KeyMapperPro.exe")
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print("\n==========================================================")
        print("[SUCCESS] INSTALLER BUILD COMPLETED SUCCESSFULLY!")
        print(f"Output Binary : {exe_path}")
        print(f"Binary Size   : {size_mb:.2f} MB")
        print("==========================================================")
    else:
        print("\n[ERROR] Build finished, but output file was not found.")

if __name__ == "__main__":
    build_installer()
