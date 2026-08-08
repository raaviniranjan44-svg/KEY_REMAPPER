"""
Virtual Key Codes (VK) & Key Name Mappings for Windows OS
Supports Full Names, Raw Characters, and Case-Insensitive Aliases.
"""

# Windows Virtual Key Codes dictionary
VK_CODE_TO_NAME = {
    0x08: "Backspace",
    0x09: "Tab",
    0x0C: "Clear",
    0x0D: "Enter",
    0x10: "Shift",
    0x11: "Ctrl",
    0x12: "Alt",
    0x13: "Pause",
    0x14: "Caps Lock",
    0x1B: "Escape",
    0x20: "Space",
    0x21: "Page Up",
    0x22: "Page Down",
    0x23: "End",
    0x24: "Home",
    0x25: "Left Arrow",
    0x26: "Up Arrow",
    0x27: "Right Arrow",
    0x28: "Down Arrow",
    0x2C: "Print Screen",
    0x2D: "Insert",
    0x2E: "Delete",
    
    # Numbers 0-9
    0x30: "0", 0x31: "1", 0x32: "2", 0x33: "3", 0x34: "4",
    0x35: "5", 0x36: "6", 0x37: "7", 0x38: "8", 0x39: "9",
    
    # Letters A-Z
    0x41: "A", 0x42: "B", 0x43: "C", 0x44: "D", 0x45: "E", 0x46: "F",
    0x47: "G", 0x48: "H", 0x49: "I", 0x4A: "J", 0x4B: "K", 0x4C: "L",
    0x4D: "M", 0x4E: "N", 0x4F: "O", 0x50: "P", 0x51: "Q", 0x52: "R",
    0x53: "S", 0x54: "T", 0x55: "U", 0x56: "V", 0x57: "W", 0x58: "X",
    0x59: "Y", 0x5A: "Z",
    
    # Left / Right Modifiers
    0x5B: "Left Win",
    0x5C: "Right Win",
    0x5D: "Apps / Menu",
    
    # Numpad
    0x60: "Numpad 0", 0x61: "Numpad 1", 0x62: "Numpad 2", 0x63: "Numpad 3",
    0x64: "Numpad 4", 0x65: "Numpad 5", 0x66: "Numpad 6", 0x67: "Numpad 7",
    0x68: "Numpad 8", 0x69: "Numpad 9", 0x6A: "Numpad *", 0x6B: "Numpad +",
    0x6D: "Numpad -", 0x6E: "Numpad .", 0x6F: "Numpad /",
    
    # Function Keys F1-F12
    0x70: "F1", 0x71: "F2", 0x72: "F3", 0x73: "F4", 0x74: "F5", 0x75: "F6",
    0x76: "F7", 0x77: "F8", 0x78: "F9", 0x79: "F10", 0x7A: "F11", 0x7B: "F12",
    
    # Lock Keys & Volume / Media
    0x90: "Num Lock",
    0x91: "Scroll Lock",
    0xA0: "Left Shift",
    0xA1: "Right Shift",
    0xA2: "Left Ctrl",
    0xA3: "Right Ctrl",
    0xA4: "Left Alt",
    0xA5: "Right Alt",
    
    0xAD: "Mute Volume",
    0xAE: "Volume Down",
    0xAF: "Volume Up",
    0xB0: "Media Next",
    0xB1: "Media Prev",
    0xB2: "Media Stop",
    0xB3: "Media Play/Pause",
    
    # Punctuation & Symbols
    0xBA: "; (Semicolon)",
    0xBB: "= (Equal)",
    0xBC: ", (Comma)",
    0xBD: "- (Minus)",
    0xBE: ". (Period)",
    0xBF: "/ (Slash)",
    0xC0: "` (Grave Accent / Tilde)",
    0xDB: "[ (Left Bracket)",
    0xDC: "\\ (Backslash)",
    0xDD: "] (Right Bracket)",
    0xDE: "' (Single Quote)"
}

# Reverse lookup dictionary building (Case-Insensitive)
NAME_TO_VK_CODE = {}

# 1. Populate standard descriptive names
for code, name in VK_CODE_TO_NAME.items():
    NAME_TO_VK_CODE[name] = code
    NAME_TO_VK_CODE[name.lower()] = code

# 2. Add raw character symbol mappings
SYMBOL_DIRECT_MAP = {
    "/": 0xBF,
    ";": 0xBA,
    "=": 0xBB,
    ",": 0xBC,
    "-": 0xBD,
    ".": 0xBE,
    "`": 0xC0,
    "[": 0xDB,
    "\\": 0xDC,
    "]": 0xDD,
    "'": 0xDE,
    "slash": 0xBF,
    "semicolon": 0xBA,
    "equal": 0xBB,
    "comma": 0xBC,
    "minus": 0xBD,
    "period": 0xBE,
    "tilde": 0xC0,
    "bracketleft": 0xDB,
    "backslash": 0xDC,
    "bracketright": 0xDD,
    "quote": 0xDE,
    "esc": 0x1B,
    "caps": 0x14,
    "del": 0x2E,
    "ins": 0x2D
}

for char_str, code in SYMBOL_DIRECT_MAP.items():
    NAME_TO_VK_CODE[char_str] = code
    NAME_TO_VK_CODE[char_str.lower()] = code

# 3. Add lowercase letter aliases a-z -> A-Z (0x41-0x5A)
for char_code in range(0x41, 0x5A + 1):
    char_str = chr(char_code).lower()
    NAME_TO_VK_CODE[char_str] = char_code


def get_key_name(vk_code: int) -> str:
    """Returns human readable key name from virtual key code."""
    if vk_code in VK_CODE_TO_NAME:
        return VK_CODE_TO_NAME[vk_code]
    return f"Key (0x{vk_code:02X})"


def get_vk_code(key_name: str) -> int:
    """Returns virtual key code from key name or raw character symbol."""
    if not key_name:
        return None
    key_clean = key_name.strip()
    
    # Try exact or lowercase lookup
    if key_clean in NAME_TO_VK_CODE:
        return NAME_TO_VK_CODE[key_clean]
    if key_clean.lower() in NAME_TO_VK_CODE:
        return NAME_TO_VK_CODE[key_clean.lower()]
        
    # Try hex parsing (e.g. 0xBF or 191)
    try:
        val = int(key_clean, 0)
        if 0 <= val <= 255:
            return val
    except ValueError:
        pass
        
    return None
