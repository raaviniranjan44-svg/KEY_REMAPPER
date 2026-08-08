"""
Win32 Low-Level Keyboard Hook Engine for Real-Time Key Remapping
"""

import ctypes
from ctypes import wintypes
import threading
import time

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# Win32 Hook Constants
WH_KEYBOARD_LL = 13
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_SYSKEYDOWN = 0x0104
WM_SYSKEYUP = 0x0105
LLKHF_INJECTED = 0x10
LLKHF_EXTENDED = 0x01

INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_SCANCODE = 0x0008

MAGIC_EXTRA_INFO = 0x99999999

# Win32 Structures
class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("vkCode", wintypes.DWORD),
        ("scanCode", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_size_t),
    ]

class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_size_t),
    ]

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD),
    ]

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_size_t),
    ]

class _INPUTunion(ctypes.Union):
    _fields_ = [
        ("mi", MOUSEINPUT),
        ("ki", KEYBDINPUT),
        ("hi", HARDWAREINPUT),
    ]

class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", wintypes.DWORD),
        ("union", _INPUTunion),
    ]

HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_ssize_t, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)

# Explicit Win32 Function Signatures (Required for 64-bit Windows pointers)
user32.CallNextHookEx.argtypes = [wintypes.HHOOK, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM]
user32.CallNextHookEx.restype = ctypes.c_ssize_t

user32.SetWindowsHookExW.argtypes = [ctypes.c_int, HOOKPROC, wintypes.HINSTANCE, wintypes.DWORD]
user32.SetWindowsHookExW.restype = wintypes.HHOOK

user32.UnhookWindowsHookEx.argtypes = [wintypes.HHOOK]
user32.UnhookWindowsHookEx.restype = wintypes.BOOL

user32.SendInput.argtypes = [wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int]
user32.SendInput.restype = wintypes.UINT

user32.MapVirtualKeyW.argtypes = [wintypes.UINT, wintypes.UINT]
user32.MapVirtualKeyW.restype = wintypes.UINT


# Set of Virtual Keys that require the KEYEVENTF_EXTENDEDKEY flag
EXTENDED_VK_SET = {
    0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28,  # PageUp, PageDown, End, Home, Left, Up, Right, Down
    0x2C, 0x2D, 0x2E,                                # PrtSc, Insert, Delete
    0x6F,                                            # Numpad /
    0x90, 0x91,                                      # Num Lock, Scroll Lock
    0xA3, 0xA5,                                      # Right Ctrl, Right Alt
    0x5B, 0x5C, 0x5D,                                # Left Win, Right Win, Apps
    0xAD, 0xAE, 0xAF, 0xB0, 0xB1, 0xB2, 0xB3          # Volume & Media Keys
}


def inject_key_event(vk_code: int, is_keyup: bool, is_extended: bool = None):
    """Synthesize virtual key event using Win32 SendInput."""
    if is_extended is None:
        is_extended = vk_code in EXTENDED_VK_SET

    flags = 0
    if is_keyup:
        flags |= KEYEVENTF_KEYUP
    if is_extended:
        flags |= KEYEVENTF_EXTENDEDKEY
        
    scan_code = user32.MapVirtualKeyW(vk_code, 0)
    
    inp = INPUT()
    inp.type = INPUT_KEYBOARD
    inp.union.ki = KEYBDINPUT(
        wVk=vk_code,
        wScan=scan_code,
        dwFlags=flags,
        time=0,
        dwExtraInfo=MAGIC_EXTRA_INFO
    )
    
    user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))


class KeyRemapperEngine:
    def __init__(self):
        self.remap_table = {}  # {source_vk: target_vk}
        self.enabled = True
        self.detect_mode = False
        self.detect_callback = None
        self.hook_handle = None
        self.hook_thread = None
        self._hook_proc_ref = None
        self._running = False
        
    def set_remap_table(self, new_table: dict):
        """Update active key remapping dictionary."""
        self.remap_table = {int(k): int(v) for k, v in new_table.items()}

    def toggle_enabled(self) -> bool:
        """Toggle active state of remapping."""
        self.enabled = not self.enabled
        return self.enabled

    def enable_detection(self, callback):
        """Enable temporary key detection mode for UI setup."""
        self.detect_callback = callback
        self.detect_mode = True

    def disable_detection(self):
        """Disable key detection mode."""
        self.detect_mode = False
        self.detect_callback = None

    def start(self):
        """Start the keyboard hook in a background thread."""
        if self._running:
            return
            
        self._running = True
        self.hook_thread = threading.Thread(target=self._run_hook_loop, daemon=True)
        self.hook_thread.start()

    def stop(self):
        """Stop the keyboard hook."""
        self._running = False
        if self.hook_handle:
            user32.UnhookWindowsHookEx(self.hook_handle)
            self.hook_handle = None

    def _run_hook_loop(self):
        """Win32 Message loop for Low-Level Keyboard Hook."""
        def low_level_keyboard_proc(nCode, wParam, lParam):
            if nCode >= 0:
                kbd = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
                vk_code = kbd.vkCode
                flags = kbd.flags
                is_injected = ((flags & LLKHF_INJECTED) != 0) or (kbd.dwExtraInfo == MAGIC_EXTRA_INFO)
                is_keyup = (wParam == WM_KEYUP or wParam == WM_SYSKEYUP)
                
                # Check Key Detection Mode
                if self.detect_mode and not is_keyup:
                    if self.detect_callback:
                        # Schedule callback on main UI thread
                        self.detect_callback(vk_code)
                    self.detect_mode = False
                    return 1  # Suppress key during detection mode
                
                # Process active key remappings
                if not is_injected and self.enabled:
                    if vk_code in self.remap_table:
                        target_vk = self.remap_table[vk_code]
                        
                        # Inject replacement target key
                        inject_key_event(target_vk, is_keyup)
                        
                        # Suppress original physical keypress
                        return 1
                        
            return user32.CallNextHookEx(self.hook_handle, nCode, wParam, lParam)

        self._hook_proc_ref = HOOKPROC(low_level_keyboard_proc)
        
        self.hook_handle = user32.SetWindowsHookExW(
            WH_KEYBOARD_LL,
            self._hook_proc_ref,
            None,
            0
        )
        
        if not self.hook_handle:
            print(f"Failed to install keyboard hook. Error: {kernel32.GetLastError()}")
            self._running = False
            return
            
        # Win32 Message Loop
        msg = wintypes.MSG()
        while self._running:
            b_ret = user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
            if b_ret <= 0:
                break
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))

        if self.hook_handle:
            user32.UnhookWindowsHookEx(self.hook_handle)
            self.hook_handle = None
