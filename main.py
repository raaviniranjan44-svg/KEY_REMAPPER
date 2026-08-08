"""
KeyMapper Pro — Main Entry Point
Universal PC Keyboard Key Remapper for Windows
"""

import sys
import tkinter as tk
from gui import KeyRemapperApp

def main():
    # Launch Tkinter GUI
    root = tk.Tk()
    app = KeyRemapperApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
