"""
Windows Kernel Registry Scancode Map Manager
Permanently remaps keys at Windows Kernel level (no background app required).
"""

import winreg
import struct
import ctypes

user32 = ctypes.windll.user32

REG_KEY_PATH = r"SYSTEM\CurrentControlSet\Control\Keyboard Layout"
VALUE_NAME = "Scancode Map"

def build_scancode_map_binary(remap_dict: dict) -> bytes:
    """
    Build Windows Registry Scancode Map binary data layout:
    - 4 bytes Version (0x00000000)
    - 4 bytes Flags (0x00000000)
    - 4 bytes Count of entries (including 1 null terminator)
    - N * 4 bytes Mapping Entries [Target Scancode (2B), Source Scancode (2B)]
    - 4 bytes Null Terminator (0x00000000)
    """
    entries = []
    for src_vk, tgt_vk in remap_dict.items():
        src_scan = user32.MapVirtualKeyW(int(src_vk), 0)
        tgt_scan = user32.MapVirtualKeyW(int(tgt_vk), 0)
        if src_scan != 0 and tgt_scan != 0:
            entries.append(struct.pack("<HH", tgt_scan, src_scan))
            
    count = len(entries) + 1  # Includes null terminator
    header = struct.pack("<III", 0, 0, count)
    footer = struct.pack("<I", 0)
    return header + b"".join(entries) + footer


def write_registry_scancode_map(remap_dict: dict) -> bool:
    """
    Write permanent key mappings to HKEY_LOCAL_MACHINE Registry.
    Requires Admin privileges.
    """
    try:
        binary_data = build_scancode_map_binary(remap_dict)
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, REG_KEY_PATH, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, VALUE_NAME, 0, winreg.REG_BINARY, binary_data)
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"Error writing Registry Scancode Map: {e}")
        return False


def remove_registry_scancode_map() -> bool:
    """Remove permanent HKLM Registry Scancode Map."""
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, REG_KEY_PATH, 0, winreg.KEY_SET_VALUE)
        try:
            winreg.DeleteValue(key, VALUE_NAME)
        except FileNotFoundError:
            pass
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"Error removing Registry Scancode Map: {e}")
        return False


def is_registry_map_active() -> bool:
    """Check if HKLM Registry Scancode Map exists."""
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, REG_KEY_PATH, 0, winreg.KEY_READ)
        winreg.QueryValueEx(key, VALUE_NAME)
        winreg.CloseKey(key)
        return True
    except Exception:
        return False
