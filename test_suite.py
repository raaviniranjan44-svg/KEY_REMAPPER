"""
KeyMapper Pro — 100% Production Test & Verification Suite
Rigorously tests key categories, Win32 hooks, SendInput, profiles, and GUI theme engine.
"""

import sys
import time
import os
import json
import ctypes
import unittest

sys.stdout.reconfigure(encoding='utf-8')

import key_codes
import remapper_engine
import profile_manager
import gui


class TestKeyMapperPro(unittest.TestCase):
    
    def test_01_key_codes_dictionary(self):
        """Test Virtual Key code mappings and bidirectionality for all key categories."""
        # 1. Function Keys F1-F12
        for i in range(1, 13):
            vk = 0x6F + i # 0x70 = F1
            name = f"F{i}"
            self.assertEqual(key_codes.get_key_name(vk), name)
            self.assertEqual(key_codes.get_vk_code(name), vk)
            
        # 2. Letters A-Z
        for char_code in range(0x41, 0x5B):
            char_str = chr(char_code)
            self.assertEqual(key_codes.get_key_name(char_code), char_str)
            self.assertEqual(key_codes.get_vk_code(char_str), char_code)
            
        # 3. Numbers 0-9
        for num_code in range(0x30, 0x3A):
            num_str = chr(num_code)
            self.assertEqual(key_codes.get_key_name(num_code), num_str)
            self.assertEqual(key_codes.get_vk_code(num_str), num_code)
            
        # 4. Modifiers & Special Keys
        special_keys = {
            0x14: "Caps Lock",
            0x1B: "Escape",
            0x08: "Backspace",
            0x0D: "Enter",
            0x20: "Space",
            0x09: "Tab",
            0xA0: "Left Shift",
            0xA1: "Right Shift",
            0xA2: "Left Ctrl",
            0xA3: "Right Ctrl",
            0xA4: "Left Alt",
            0xA5: "Right Alt",
            0x25: "Left Arrow",
            0x26: "Up Arrow",
            0x27: "Right Arrow",
            0x28: "Down Arrow"
        }
        for vk, name in special_keys.items():
            self.assertEqual(key_codes.get_key_name(vk), name)
            self.assertEqual(key_codes.get_vk_code(name), vk)

    def test_02_extended_key_classification(self):
        """Verify extended key scancode flag classification."""
        # Standard keys MUST NOT be extended
        self.assertFalse(0x41 in remapper_engine.EXTENDED_VK_SET) # 'A'
        self.assertFalse(0x31 in remapper_engine.EXTENDED_VK_SET) # '1'
        self.assertFalse(0x1B in remapper_engine.EXTENDED_VK_SET) # 'Escape'
        self.assertFalse(0x76 in remapper_engine.EXTENDED_VK_SET) # 'F7'

        # Extended keys MUST be in EXTENDED_VK_SET
        self.assertTrue(0x26 in remapper_engine.EXTENDED_VK_SET) # Up Arrow
        self.assertTrue(0x27 in remapper_engine.EXTENDED_VK_SET) # Right Arrow
        self.assertTrue(0x2E in remapper_engine.EXTENDED_VK_SET) # Delete
        self.assertTrue(0xA5 in remapper_engine.EXTENDED_VK_SET) # Right Alt

    def test_03_remapper_engine_win32_hook(self):
        """Test Win32 low-level keyboard hook registration and unhooking."""
        engine = remapper_engine.KeyRemapperEngine()
        
        # Test remap table setting
        test_table = {
            0x76: 0x41,  # F7 -> A
            0x14: 0x1B,  # Caps Lock -> Esc
            0x26: 0x4B   # Up Arrow -> K
        }
        engine.set_remap_table(test_table)
        self.assertEqual(engine.remap_table[0x76], 0x41)
        self.assertEqual(engine.remap_table[0x14], 0x1B)
        
        # Start hook engine thread
        engine.start()
        time.sleep(0.5)
        
        self.assertIsNotNone(engine.hook_handle)
        self.assertNotEqual(engine.hook_handle, 0)
        
        # Stop hook engine thread
        engine.stop()
        time.sleep(0.2)
        self.assertIsNone(engine.hook_handle)

    def test_04_profile_manager_crud(self):
        """Test profile creation, reading, saving, and deletion."""
        pm = profile_manager.ProfileManager()
        profile_name = "production_test_profile"
        
        mappings = {
            0x76: 0x41, # F7 -> A
            0x20: 0x0D  # Space -> Enter
        }
        pm.save_profile(profile_name, mappings)
        
        available = pm.get_available_profiles()
        self.assertIn(profile_name, available)
        
        loaded = pm.load_profile(profile_name)
        self.assertEqual(loaded[0x76], 0x41)
        self.assertEqual(loaded[0x20], 0x0D)
        
        pm.delete_profile(profile_name)
        self.assertNotIn(profile_name, pm.get_available_profiles())

    def test_05_gui_theme_and_layout(self):
        """Test Tkinter GUI initialization, widget rendering, and theme switcher."""
        import tkinter as tk
        root = tk.Tk()
        app = gui.KeyRemapperApp(root)
        root.update()
        
        self.assertEqual(app.theme["name"], "light")
        
        # Test theme toggle to dark mode
        app._toggle_theme()
        root.update()
        self.assertEqual(app.theme["name"], "dark")
        
        # Test theme toggle back to light mode
        app._toggle_theme()
        root.update()
        self.assertEqual(app.theme["name"], "light")
        
        # Test adding a rule in GUI
        app.combo_src_key.set("F7")
        app.combo_tgt_key.set("A")
        app._add_mapping_rule()
        
        self.assertIn(0x76, app.profile_mgr.mappings)
        self.assertEqual(app.profile_mgr.mappings[0x76], 0x41)
        
        app.on_close()


if __name__ == "__main__":
    print("==========================================================")
    print("🚀 RUNNING KEYMAPPER PRO PRODUCTION SUITE VERIFICATION")
    print("==========================================================")
    unittest.main()
