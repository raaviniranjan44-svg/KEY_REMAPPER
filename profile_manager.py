"""
Profile Manager for Loading & Saving Keyboard Remap Presets (JSON)
"""

import json
import os
from key_codes import get_key_name, get_vk_code

PROFILES_DIR = os.path.join(os.path.dirname(__file__), "profiles")

class ProfileManager:
    def __init__(self):
        if not os.path.exists(PROFILES_DIR):
            os.makedirs(PROFILES_DIR)
        self.current_profile_name = "default"
        self.mappings = {} # {source_vk: target_vk}

    def get_available_profiles(self) -> list:
        """Returns list of saved profile names."""
        profiles = []
        for file in os.listdir(PROFILES_DIR):
            if file.endswith(".json"):
                profiles.append(file[:-5])
        if "default" not in profiles:
            profiles.insert(0, "default")
        return sorted(list(set(profiles)))

    def load_profile(self, name: str = "default") -> dict:
        """Load profile by name. Returns dict {source_vk: target_vk}."""
        filepath = os.path.join(PROFILES_DIR, f"{name}.json")
        self.current_profile_name = name
        self.mappings = {}
        
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data.get("mappings", []):
                        src_vk = item.get("src_vk")
                        tgt_vk = item.get("tgt_vk")
                        if src_vk and tgt_vk:
                            self.mappings[int(src_vk)] = int(tgt_vk)
            except Exception as e:
                print(f"Error loading profile {name}: {e}")
        return self.mappings

    def save_profile(self, name: str, mappings: dict):
        """Save profile to JSON file."""
        filepath = os.path.join(PROFILES_DIR, f"{name}.json")
        self.current_profile_name = name
        self.mappings = {int(k): int(v) for k, v in mappings.items()}
        
        export_list = []
        for src_vk, tgt_vk in self.mappings.items():
            export_list.append({
                "src_vk": src_vk,
                "src_name": get_key_name(src_vk),
                "tgt_vk": tgt_vk,
                "tgt_name": get_key_name(tgt_vk)
            })
            
        data = {
            "profile_name": name,
            "mappings": export_list
        }
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def delete_profile(self, name: str):
        """Delete profile file."""
        if name == "default":
            return
        filepath = os.path.join(PROFILES_DIR, f"{name}.json")
        if os.path.exists(filepath):
            os.remove(filepath)
