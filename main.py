"""
KeyMapper Pro — Main Entry Point
Universal PC Keyboard Key Remapper for Windows
"""

import sys
import tkinter as tk
from gui import KeyRemapperApp

def main():
    # Check if launched with --minimized or -m flag (e.g. from Windows Startup)
    start_minimized = "--minimized" in sys.argv or "-m" in sys.argv
    
    root = tk.Tk()
    app = KeyRemapperApp(root, start_minimized=start_minimized)
    root.mainloop()

if __name__ == "__main__":
    main()
