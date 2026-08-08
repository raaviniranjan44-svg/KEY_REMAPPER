"""
Real-Time Keyboard Hardware Diagnostic Logger
Intercepts and prints exact Virtual Key codes (VK) emitted by physical keypresses.
"""

import ctypes
from ctypes import wintypes
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

WH_KEYBOARD_LL = 13
WM_KEYDOWN = 0x0100
WM_SYSKEYDOWN = 0x0104

class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("vkCode", wintypes.DWORD),
        ("scanCode", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_size_t),
    ]

HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_ssize_t, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)

user32.CallNextHookEx.argtypes = [wintypes.HHOOK, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM]
user32.CallNextHookEx.restype = ctypes.c_ssize_t
user32.SetWindowsHookExW.argtypes = [ctypes.c_int, HOOKPROC, wintypes.HINSTANCE, wintypes.DWORD]
user32.SetWindowsHookExW.restype = wintypes.HHOOK

# Known VK Code names
VK_NAMES = {
    0x70: "F1", 0x71: "F2", 0x72: "F3", 0x73: "F4", 0x74: "F5", 0x75: "F6",
    0x76: "F7", 0x77: "F8", 0x78: "F9", 0x79: "F10", 0x7A: "F11", 0x7B: "F12",
    0x41: "A", 0x42: "B", 0x43: "C", 0x14: "Caps Lock", 0x1B: "Escape",
    0xAD: "Mute Volume", 0xAE: "Volume Down", 0xAF: "Volume Up",
    0xB0: "Media Next", 0xB1: "Media Prev", 0xB2: "Media Stop", 0xB3: "Media Play/Pause"
}

def log_keyboard_events():
    print("=================================================================")
    print("🔍 REAL-TIME HARDWARE KEYBOARD DIAGNOSTIC LOGGER")
    print("Press ANY physical key on your keyboard to test scancodes...")
    print("Press Ctrl+C to exit debug mode.")
    print("=================================================================\n")

    def hook_proc(nCode, wParam, lParam):
        if nCode >= 0 and (wParam == WM_KEYDOWN or wParam == WM_SYSKEYDOWN):
            kbd = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
            vk = kbd.vkCode
            scan = kbd.scanCode
            name = VK_NAMES.get(vk, f"Key_0x{vk:02X}")
            print(f"👉 [KEY PRESS DETECTED] Name: '{name}' | VK Code: 0x{vk:02X} ({vk}) | ScanCode: {scan} | Flags: {kbd.flags}")
        return user32.CallNextHookEx(None, nCode, wParam, lParam)

    callback = HOOKPROC(hook_proc)
    hook_handle = user32.SetWindowsHookExW(WH_KEYBOARD_LL, callback, None, 0)

    if not hook_handle:
        print(f"❌ ERROR: Failed to install hook. Error code: {kernel32.GetLastError()}")
        return

    print(f"✅ Hardware Key Hook Active! (HHOOK: {hook_handle})\n")
    
    msg = wintypes.MSG()
    try:
        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))
    except KeyboardInterrupt:
        pass
    finally:
        user32.UnhookWindowsHookEx(hook_handle)
        print("\nDiagnostic mode closed.")

if __name__ == "__main__":
    log_keyboard_events()
