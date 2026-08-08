"""
Modern Desktop GUI for Keyboard Key Remapper Application (Tkinter)
Features Clean Light & Dark Themes with Interactive Visual QWERTY Layout
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from key_codes import VK_CODE_TO_NAME, NAME_TO_VK_CODE, get_key_name, get_vk_code
from profile_manager import ProfileManager
from remapper_engine import KeyRemapperEngine

# Clean Light Theme Palette (Default)
THEME_LIGHT = {
    "name": "light",
    "bg_main": "#f8fafc",         # Clean Slate Light
    "bg_card": "#ffffff",         # Pure White Card
    "bg_card_hover": "#f1f5f9",   # Soft Cool Grey Hover
    "text_primary": "#0f172a",     # Dark Slate Text
    "text_secondary": "#64748b",   # Muted Slate Text
    "accent_blue": "#2563eb",     # Royal Blue Accent
    "accent_green": "#059669",    # Emerald Green
    "accent_red": "#dc2626",      # Rose Red
    "accent_amber": "#d97706",    # Amber Warning
    "border_color": "#e2e8f0",    # Light Card Border
    "key_normal_bg": "#e2e8f0",   # Keycap Normal
    "key_remapped_bg": "#8b5cf6", # Vibrant Purple Remapped
    "key_text": "#0f172a",        # Keycap Text
    "entry_bg": "#ffffff"
}

# Dark Theme Palette
THEME_DARK = {
    "name": "dark",
    "bg_main": "#0f172a",
    "bg_card": "#1e293b",
    "bg_card_hover": "#334155",
    "text_primary": "#f8fafc",
    "text_secondary": "#94a3b8",
    "accent_blue": "#3b82f6",
    "accent_green": "#10b981",
    "accent_red": "#ef4444",
    "accent_amber": "#f59e0b",
    "border_color": "#334155",
    "key_normal_bg": "#334155",
    "key_remapped_bg": "#7c3aed",
    "key_text": "#f8fafc",
    "entry_bg": "#0f172a"
}


class KeyRemapperApp:
    def __init__(self, root: tk.Tk, start_minimized: bool = False):
        self.root = root
        self.start_minimized = start_minimized
        self.root.title("KeyMapper Pro — Universal Keyboard Remapper")
        self.root.geometry("1020x840")
        self.root.minsize(980, 760)
        
        # Active Theme (Default: Clean Light Theme)
        self.theme = THEME_LIGHT
        self.root.configure(bg=self.theme["bg_main"])
        
        # Core Engine & Profile Manager
        self.engine = KeyRemapperEngine()
        self.profile_mgr = ProfileManager()
        
        # UI Element Tracking for Dynamic Theme Switching
        self.track_frames = []
        self.track_cards = []
        self.track_labels = []
        self.track_sublabels = []
        self.track_buttons = []
        self.key_buttons = {}      # {vk_code: [Button, ...]}
        
        # Active state
        self.detected_src_vk = None
        self.detected_tgt_vk = None
        self.detecting_for = None
        
        # Setup Custom Styles & Build UI
        self._setup_styles()
        self._build_header()
        self._build_profile_bar()
        self._build_add_mapping_card()
        self._build_visual_keyboard()
        self._build_mappings_table()
        self._build_tester_and_footer()
        
        # Load default profile and start engine
        self._load_current_profile()
        self.engine.start()
        
        # If launched from Windows startup, start minimized in background
        if self.start_minimized:
            self.root.iconify()
            
        # Clean shutdown on window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _setup_styles(self):
        """Configure Tkinter TTK styling theme."""
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self._apply_ttk_styles()

    def _apply_ttk_styles(self):
        """Apply active theme colors to TTK widgets."""
        t = self.theme
        self.style.configure("TFrame", background=t["bg_main"])
        self.style.configure("Card.TFrame", background=t["bg_card"], relief="flat", borderwidth=1)
        self.style.configure("TLabel", background=t["bg_main"], foreground=t["text_primary"], font=("Segoe UI", 10))
        self.style.configure("Card.TLabel", background=t["bg_card"], foreground=t["text_primary"], font=("Segoe UI", 10))
        self.style.configure("SubText.TLabel", background=t["bg_card"], foreground=t["text_secondary"], font=("Segoe UI", 9))
        
        self.style.configure("TCombobox", 
                        fieldbackground=t["bg_card"], 
                        background=t["bg_card_hover"], 
                        foreground=t["text_primary"],
                        bordercolor=t["border_color"],
                        arrowcolor=t["text_primary"],
                        font=("Segoe UI", 10))
        self.style.map("TCombobox", fieldbackground=[("readonly", t["bg_card"])], foreground=[("readonly", t["text_primary"])])
        
        self.style.configure("Treeview", 
                        background=t["bg_card"], 
                        foreground=t["text_primary"], 
                        fieldbackground=t["bg_card"], 
                        rowheight=32,
                        font=("Segoe UI", 9))
        self.style.configure("Treeview.Heading", 
                        background=t["bg_main"], 
                        foreground=t["text_secondary"], 
                        font=("Segoe UI", 9, "bold"),
                        bordercolor=t["border_color"])
        self.style.map("Treeview", background=[("selected", t["accent_blue"])], foreground=[("selected", "#ffffff")])

    def _build_header(self):
        """Build top app title bar, theme switch, and Master Power Switch."""
        self.header_frame = tk.Frame(self.root, bg=self.theme["bg_main"], pady=12, padx=20)
        self.header_frame.pack(fill="x", padx=20)
        self.track_frames.append(self.header_frame)
        
        title_box = tk.Frame(self.header_frame, bg=self.theme["bg_main"])
        title_box.pack(side="left")
        self.track_frames.append(title_box)
        
        self.lbl_title = tk.Label(title_box, text="⚡ KeyMapper Pro", font=("Segoe UI", 18, "bold"), bg=self.theme["bg_main"], fg=self.theme["text_primary"])
        self.lbl_title.pack(anchor="w")
        self.track_labels.append(self.lbl_title)
        
        self.lbl_sub = tk.Label(title_box, text="System-Wide Real-Time Keyboard Key Remapper", font=("Segoe UI", 9), bg=self.theme["bg_main"], fg=self.theme["text_secondary"])
        self.lbl_sub.pack(anchor="w")
        self.track_sublabels.append(self.lbl_sub)
        
        controls_box = tk.Frame(self.header_frame, bg=self.theme["bg_main"])
        controls_box.pack(side="right")
        self.track_frames.append(controls_box)
        
        # Theme Switcher Button
        self.btn_theme = tk.Button(
            controls_box,
            text="☀️ Light Mode",
            font=("Segoe UI", 9, "bold"),
            bg=self.theme["bg_card_hover"],
            fg=self.theme["text_primary"],
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2",
            command=self._toggle_theme
        )
        self.btn_theme.pack(side="left", padx=(0, 12))
        
        # Power Switch Button
        self.btn_power = tk.Button(
            controls_box,
            text="🟢 REMAPPING ENABLED",
            font=("Segoe UI", 10, "bold"),
            bg=self.theme["accent_green"],
            fg="#ffffff",
            activebackground="#059669",
            activeforeground="#ffffff",
            bd=0,
            padx=16,
            pady=7,
            cursor="hand2",
            command=self._toggle_power
        )
        self.btn_power.pack(side="left")

    def _build_profile_bar(self):
        """Build Profile Selector and Save/New buttons."""
        self.bar_card = tk.Frame(self.root, bg=self.theme["bg_card"], padx=15, pady=10, highlightbackground=self.theme["border_color"], highlightthickness=1)
        self.bar_card.pack(fill="x", padx=20, pady=(0, 10))
        self.track_cards.append(self.bar_card)
        
        lbl_prof = tk.Label(self.bar_card, text="Active Profile:", font=("Segoe UI", 10, "bold"), bg=self.theme["bg_card"], fg=self.theme["text_primary"])
        lbl_prof.pack(side="left", padx=(0, 10))
        self.track_labels.append(lbl_prof)
        
        self.combo_profile = ttk.Combobox(self.bar_card, state="readonly", width=18)
        self.combo_profile.pack(side="left", padx=(0, 12))
        self.combo_profile.bind("<<ComboboxSelected>>", self._on_profile_selected)
        
        btn_save = tk.Button(self.bar_card, text="💾 Save Profile", font=("Segoe UI", 9, "bold"), bg=self.theme["bg_card_hover"], fg=self.theme["text_primary"], bd=0, padx=12, pady=5, cursor="hand2", command=self._save_current_profile)
        btn_save.pack(side="left", padx=(0, 8))
        self.track_buttons.append(btn_save)
        
        btn_new = tk.Button(self.bar_card, text="➕ New Profile", font=("Segoe UI", 9, "bold"), bg=self.theme["bg_card_hover"], fg=self.theme["text_primary"], bd=0, padx=12, pady=5, cursor="hand2", command=self._create_new_profile)
        btn_new.pack(side="left", padx=(0, 8))
        self.track_buttons.append(btn_new)
        
        btn_del = tk.Button(self.bar_card, text="🗑️ Delete Profile", font=("Segoe UI", 9), bg=self.theme["bg_card_hover"], fg=self.theme["accent_red"], bd=0, padx=12, pady=5, cursor="hand2", command=self._delete_current_profile)
        btn_del.pack(side="left", padx=(0, 8))
        
        btn_unlock = tk.Button(self.bar_card, text="🔓 Unlock Fn F7 ➔ /", font=("Segoe UI", 9, "bold"), bg=self.theme["accent_blue"], fg="#ffffff", bd=0, padx=12, pady=5, cursor="hand2", command=self._unlock_fn_f7)
        btn_unlock.pack(side="left", padx=(0, 8))

        btn_perm = tk.Button(self.bar_card, text="⚡ Kernel Map (No App Needed)", font=("Segoe UI", 9, "bold"), bg=self.theme["bg_card_hover"], fg=self.theme["text_primary"], bd=0, padx=12, pady=5, cursor="hand2", command=self._apply_permanent_kernel_map)
        btn_perm.pack(side="left", padx=(0, 12))
        self.track_buttons.append(btn_perm)

        # Auto-Start Checkbox
        self.var_autostart = tk.BooleanVar(value=self._check_autostart())
        self.chk_auto = tk.Checkbutton(self.bar_card, text="🚀 Run on Windows Startup", variable=self.var_autostart, font=("Segoe UI", 9), bg=self.theme["bg_card"], fg=self.theme["text_primary"], selectcolor=self.theme["bg_card"], activebackground=self.theme["bg_card"], activeforeground=self.theme["text_primary"], command=self._toggle_autostart)
        self.chk_auto.pack(side="right")

    def _unlock_fn_f7(self):
        """Map all laptop Fn & Action scancodes for F7 to / (Slash) automatically."""
        fn_codes = [0x76, 179, 176, 173, 174, 175, 182, 183]
        for vk in fn_codes:
            self.profile_mgr.mappings[vk] = 0xBF # '/'
        self.engine.set_remap_table(self.profile_mgr.mappings)
        self._save_current_profile()
        self._refresh_mappings_table()
        self.lbl_status.config(text="Unlocked F7 (All Fn & Action key scancodes now print /)!", fg=self.theme["accent_green"])

    def _apply_permanent_kernel_map(self):
        """Write permanent Scancode Map to Windows Registry (No App Needed Running)."""
        import registry_remapper
        if not self.profile_mgr.mappings:
            messagebox.showwarning("Empty Mappings", "Please add at least one key mapping rule before applying permanent kernel map.")
            return
            
        success = registry_remapper.write_registry_scancode_map(self.profile_mgr.mappings)
        if success:
            messagebox.showinfo("Permanent Kernel Map Active", "Permanent Windows Kernel Scancode Map written successfully!\n\nWindows Kernel will handle your key mappings natively on boot without needing any app running in background.\n\nNote: Requires a PC restart to take full effect.")
            self.lbl_status.config(text="Permanent Kernel Scancode Map active! (PC restart required)", fg=self.theme["accent_green"])
        else:
            messagebox.showerror("Permission Error", "Failed to write to HKEY_LOCAL_MACHINE Registry.\nPlease right-click run.bat and select 'Run as Administrator'.")

    def _check_autostart(self) -> bool:
        """Check if app is registered in Windows Startup Registry."""
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ)
            winreg.QueryValueEx(key, "KeyMapperPro")
            winreg.CloseKey(key)
            return True
        except Exception:
            return False

    def _toggle_autostart(self):
        """Enable or disable Windows startup registry entry."""
        import winreg, sys, os
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            if self.var_autostart.get():
                if getattr(sys, 'frozen', False):
                    exe_path = os.path.abspath(sys.executable)
                    cmd = f'"{exe_path}" --minimized'
                else:
                    main_py = os.path.abspath(os.path.join(os.path.dirname(__file__), "main.py"))
                    cmd = f'"{sys.executable}" "{main_py}" --minimized'
                winreg.SetValueEx(key, "KeyMapperPro", 0, winreg.REG_SZ, cmd)
                self.lbl_status.config(text="Added KeyMapper Pro to Windows Startup (launches minimized)!", fg=self.theme["accent_green"])
            else:
                try:
                    winreg.DeleteValue(key, "KeyMapperPro")
                except FileNotFoundError:
                    pass
                self.lbl_status.config(text="Removed KeyMapper Pro from Windows Startup.", fg=self.theme["text_secondary"])
            winreg.CloseKey(key)
        except Exception as e:
            messagebox.showerror("Registry Error", f"Failed to update startup setting: {e}")

    def _build_add_mapping_card(self):
        """Build section to add new key remapping rules."""
        self.add_card = tk.Frame(self.root, bg=self.theme["bg_card"], padx=15, pady=12, highlightbackground=self.theme["border_color"], highlightthickness=1)
        self.add_card.pack(fill="x", padx=20, pady=(0, 10))
        self.track_cards.append(self.add_card)
        
        card_title = tk.Label(self.add_card, text="Add New Remap Rule", font=("Segoe UI", 11, "bold"), bg=self.theme["bg_card"], fg=self.theme["text_primary"])
        card_title.pack(anchor="w", pady=(0, 8))
        self.track_labels.append(card_title)
        
        inputs_frame = tk.Frame(self.add_card, bg=self.theme["bg_card"])
        inputs_frame.pack(fill="x")
        self.track_cards.append(inputs_frame)
        
        # Source Key Column
        src_col = tk.Frame(inputs_frame, bg=self.theme["bg_card"])
        src_col.pack(side="left", expand=True, fill="x", padx=(0, 10))
        self.track_cards.append(src_col)
        
        lbl_src = tk.Label(src_col, text="Physical Key (Source):", font=("Segoe UI", 9), bg=self.theme["bg_card"], fg=self.theme["text_secondary"])
        lbl_src.pack(anchor="w")
        self.track_sublabels.append(lbl_src)
        
        src_row = tk.Frame(src_col, bg=self.theme["bg_card"])
        src_row.pack(fill="x", pady=(4, 0))
        self.track_cards.append(src_row)
        
        self.combo_src_key = ttk.Combobox(src_row, values=list(NAME_TO_VK_CODE.keys()), state="normal")
        self.combo_src_key.pack(side="left", expand=True, fill="x", padx=(0, 5))
        
        self.btn_detect_src = tk.Button(src_row, text="🎯 Detect Key", font=("Segoe UI", 9, "bold"), bg=self.theme["accent_blue"], fg="#ffffff", bd=0, padx=10, pady=4, cursor="hand2", command=lambda: self._start_key_detection("src"))
        self.btn_detect_src.pack(side="left")
        
        # Arrow Separator
        self.lbl_arrow = tk.Label(inputs_frame, text="➡️", font=("Segoe UI", 14), bg=self.theme["bg_card"], fg=self.theme["accent_blue"])
        self.lbl_arrow.pack(side="left", padx=10, pady=(12, 0))
        self.track_labels.append(self.lbl_arrow)
        
        # Target Key Column
        tgt_col = tk.Frame(inputs_frame, bg=self.theme["bg_card"])
        tgt_col.pack(side="left", expand=True, fill="x", padx=(10, 10))
        self.track_cards.append(tgt_col)
        
        lbl_tgt = tk.Label(tgt_col, text="Remap To (Target):", font=("Segoe UI", 9), bg=self.theme["bg_card"], fg=self.theme["text_secondary"])
        lbl_tgt.pack(anchor="w")
        self.track_sublabels.append(lbl_tgt)
        
        tgt_row = tk.Frame(tgt_col, bg=self.theme["bg_card"])
        tgt_row.pack(fill="x", pady=(4, 0))
        self.track_cards.append(tgt_row)
        
        self.combo_tgt_key = ttk.Combobox(tgt_row, values=list(NAME_TO_VK_CODE.keys()), state="normal")
        self.combo_tgt_key.pack(side="left", expand=True, fill="x", padx=(0, 5))
        
        self.btn_detect_tgt = tk.Button(tgt_row, text="🎯 Detect Key", font=("Segoe UI", 9, "bold"), bg=self.theme["accent_blue"], fg="#ffffff", bd=0, padx=10, pady=4, cursor="hand2", command=lambda: self._start_key_detection("tgt"))
        self.btn_detect_tgt.pack(side="left")
        
        # Add Button
        btn_add = tk.Button(inputs_frame, text="➕ Add Rule", font=("Segoe UI", 10, "bold"), bg=self.theme["accent_green"], fg="#ffffff", bd=0, padx=16, pady=5, cursor="hand2", command=self._add_mapping_rule)
        btn_add.pack(side="left", padx=(10, 0), pady=(12, 0))

    def _build_visual_keyboard(self):
        """Build Interactive Visual QWERTY Keyboard Grid UI."""
        self.kb_card = tk.Frame(self.root, bg=self.theme["bg_card"], padx=12, pady=10, highlightbackground=self.theme["border_color"], highlightthickness=1)
        self.kb_card.pack(fill="x", padx=20, pady=(0, 10))
        self.track_cards.append(self.kb_card)
        
        kb_header = tk.Frame(self.kb_card, bg=self.theme["bg_card"])
        kb_header.pack(fill="x", pady=(0, 6))
        self.track_cards.append(kb_header)
        
        lbl_kb_title = tk.Label(kb_header, text="⌨️ Visual Interactive Keyboard Layout", font=("Segoe UI", 10, "bold"), bg=self.theme["bg_card"], fg=self.theme["text_primary"])
        lbl_kb_title.pack(side="left")
        self.track_labels.append(lbl_kb_title)
        
        lbl_kb_sub = tk.Label(kb_header, text="Click any key to select it • Purple = Active Remap", font=("Segoe UI", 8), bg=self.theme["bg_card"], fg=self.theme["text_secondary"])
        lbl_kb_sub.pack(side="right")
        self.track_sublabels.append(lbl_kb_sub)
        
        self.kb_grid = tk.Frame(self.kb_card, bg=self.theme["bg_card"])
        self.kb_grid.pack(fill="x")
        self.track_cards.append(self.kb_grid)
        
        layout_rows = [
            [("Esc", 0x1B, 1), ("F1", 0x70, 1), ("F2", 0x71, 1), ("F3", 0x72, 1), ("F4", 0x73, 1), 
             ("F5", 0x74, 1), ("F6", 0x75, 1), ("F7", 0x76, 1), ("F8", 0x77, 1), ("F9", 0x78, 1), 
             ("F10", 0x79, 1), ("F11", 0x7A, 1), ("F12", 0x7B, 1), ("PrtSc", 0x2C, 1), ("Del", 0x2E, 1)],
            
            [("`", 0xC0, 1), ("1", 0x31, 1), ("2", 0x32, 1), ("3", 0x33, 1), ("4", 0x34, 1), ("5", 0x35, 1), 
             ("6", 0x36, 1), ("7", 0x37, 1), ("8", 0x38, 1), ("9", 0x39, 1), ("0", 0x30, 1), ("-", 0xBD, 1), 
             ("=", 0xBB, 1), ("Backspace", 0x08, 2)],
            
            [("Tab", 0x09, 1.5), ("Q", 0x51, 1), ("W", 0x57, 1), ("E", 0x45, 1), ("R", 0x52, 1), ("T", 0x54, 1), 
             ("Y", 0x59, 1), ("U", 0x55, 1), ("I", 0x49, 1), ("O", 0x4F, 1), ("P", 0x50, 1), ("[", 0xDB, 1), 
             ("]", 0xDD, 1), ("\\", 0xDC, 1)],
            
            [("Caps Lock", 0x14, 1.8), ("A", 0x41, 1), ("S", 0x53, 1), ("D", 0x44, 1), ("F", 0x46, 1), ("G", 0x47, 1), 
             ("H", 0x48, 1), ("J", 0x4A, 1), ("K", 0x4B, 1), ("L", 0x4C, 1), (";", 0xBA, 1), ("'", 0xDE, 1), 
             ("Enter", 0x0D, 2.2)],
            
            [("Shift", 0xA0, 2.2), ("Z", 0x5A, 1), ("X", 0x58, 1), ("C", 0x43, 1), ("V", 0x56, 1), ("B", 0x42, 1), 
             ("N", 0x4E, 1), ("M", 0x4D, 1), (",", 0xBC, 1), (".", 0xBE, 1), ("/", 0xBF, 1), ("Shift", 0xA1, 2.8)],
            
            [("Ctrl", 0xA2, 1.5), ("Win", 0x5B, 1.2), ("Alt", 0xA4, 1.3), ("Space", 0x20, 6.5), 
             ("Alt", 0xA5, 1.3), ("Win", 0x5C, 1.2), ("Menu", 0x5D, 1.2), ("Ctrl", 0xA3, 1.5)]
        ]
        
        for r_idx, row_keys in enumerate(layout_rows):
            row_frame = tk.Frame(self.kb_grid, bg=self.theme["bg_card"])
            row_frame.pack(fill="x", pady=2)
            self.track_cards.append(row_frame)
            
            for label, vk_code, weight in row_keys:
                btn = tk.Button(
                    row_frame,
                    text=label,
                    font=("Segoe UI", 8, "bold"),
                    bg=self.theme["key_normal_bg"],
                    fg=self.theme["key_text"],
                    activebackground=self.theme["accent_blue"],
                    activeforeground="#ffffff",
                    bd=0,
                    relief="flat",
                    height=1,
                    cursor="hand2",
                    command=lambda code=vk_code, lbl=label: self._on_visual_key_click(code, lbl)
                )
                btn.pack(side="left", fill="both", expand=True, padx=2)
                
                if vk_code not in self.key_buttons:
                    self.key_buttons[vk_code] = []
                self.key_buttons[vk_code].append(btn)

    def _on_visual_key_click(self, vk_code: int, key_label: str):
        """Action when user clicks any key button on visual keyboard."""
        key_name = get_key_name(vk_code)
        if not self.combo_src_key.get():
            self.combo_src_key.set(key_name)
            self.lbl_status.config(text=f"Selected Source Key: {key_name}", fg=self.theme["accent_blue"])
        else:
            self.combo_tgt_key.set(key_name)
            self.lbl_status.config(text=f"Selected Target Key: {key_name}", fg=self.theme["accent_blue"])

    def _build_mappings_table(self):
        """Build table displaying active remap rules."""
        self.table_card = tk.Frame(self.root, bg=self.theme["bg_card"], padx=15, pady=10, highlightbackground=self.theme["border_color"], highlightthickness=1)
        self.table_card.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        self.track_cards.append(self.table_card)
        
        table_header = tk.Frame(self.table_card, bg=self.theme["bg_card"])
        table_header.pack(fill="x", pady=(0, 6))
        self.track_cards.append(table_header)
        
        lbl_tbl_title = tk.Label(table_header, text="Active Key Mappings", font=("Segoe UI", 10, "bold"), bg=self.theme["bg_card"], fg=self.theme["text_primary"])
        lbl_tbl_title.pack(side="left")
        self.track_labels.append(lbl_tbl_title)
        
        btn_clear = tk.Button(table_header, text="Remove Selected Rule", font=("Segoe UI", 8), bg=self.theme["bg_card_hover"], fg=self.theme["accent_red"], bd=0, padx=10, pady=3, cursor="hand2", command=self._remove_selected_rule)
        btn_clear.pack(side="right")
        
        columns = ("src_name", "src_code", "tgt_name", "tgt_code")
        self.tree = ttk.Treeview(self.table_card, columns=columns, show="headings", selectmode="browse")
        
        self.tree.heading("src_name", text="Original Key Pressed")
        self.tree.heading("src_code", text="Source VK Code")
        self.tree.heading("tgt_name", text="Action / Key Output")
        self.tree.heading("tgt_code", text="Target VK Code")
        
        self.tree.column("src_name", anchor="center", width=220)
        self.tree.column("src_code", anchor="center", width=120)
        self.tree.column("tgt_name", anchor="center", width=220)
        self.tree.column("tgt_code", anchor="center", width=120)
        
        scrollbar = ttk.Scrollbar(self.table_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _build_tester_and_footer(self):
        """Build live keypress test area and status bar."""
        self.test_card = tk.Frame(self.root, bg=self.theme["bg_card"], padx=15, pady=8, highlightbackground=self.theme["border_color"], highlightthickness=1)
        self.test_card.pack(fill="x", padx=20, pady=(0, 10))
        self.track_cards.append(self.test_card)
        
        lbl_test = tk.Label(self.test_card, text="🧪 Live Key Tester:", font=("Segoe UI", 9, "bold"), bg=self.theme["bg_card"], fg=self.theme["text_primary"])
        lbl_test.pack(side="left", padx=(0, 10))
        self.track_labels.append(lbl_test)
        
        self.entry_test = tk.Entry(self.test_card, font=("Consolas", 10), bg=self.theme["entry_bg"], fg=self.theme["text_primary"], insertbackground=self.theme["text_primary"], bd=1, relief="solid")
        self.entry_test.pack(side="left", expand=True, fill="x", padx=(0, 10))
        
        btn_clear_test = tk.Button(self.test_card, text="Clear Box", font=("Segoe UI", 8), bg=self.theme["bg_card_hover"], fg=self.theme["text_secondary"], bd=0, padx=8, pady=3, command=lambda: self.entry_test.delete(0, tk.END))
        btn_clear_test.pack(side="right")
        self.track_buttons.append(btn_clear_test)
        
        self.lbl_status = tk.Label(self.root, text="Ready. Remapper is ACTIVE system-wide.", font=("Segoe UI", 9), bg=self.theme["bg_main"], fg=self.theme["accent_green"])
        self.lbl_status.pack(pady=(0, 8))

    def _toggle_theme(self):
        """Toggle between Clean Light Mode and Dark Mode."""
        if self.theme["name"] == "light":
            self.theme = THEME_DARK
            self.btn_theme.config(text="🌙 Dark Mode")
        else:
            self.theme = THEME_LIGHT
            self.btn_theme.config(text="☀️ Light Mode")
            
        t = self.theme
        self.root.configure(bg=t["bg_main"])
        
        # Apply TTK Theme Styles
        self._apply_ttk_styles()
        
        # Update tracked containers & frames
        for f in self.track_frames:
            f.config(bg=t["bg_main"])
            
        for c in self.track_cards:
            c.config(bg=t["bg_card"])
            if hasattr(c, "config") and "highlightbackground" in c.keys():
                c.config(highlightbackground=t["border_color"])
                
        for l in self.track_labels:
            l.config(bg=t["bg_card"] if l.master != self.header_frame and l.master.master != self.header_frame else t["bg_main"], fg=t["text_primary"])
            
        for sl in self.track_sublabels:
            sl.config(bg=t["bg_card"] if sl.master != self.header_frame and sl.master.master != self.header_frame else t["bg_main"], fg=t["text_secondary"])
            
        for b in self.track_buttons:
            b.config(bg=t["bg_card_hover"], fg=t["text_primary"])
            
        self.btn_theme.config(bg=t["bg_card_hover"], fg=t["text_primary"])
        self.chk_auto.config(bg=t["bg_card"], fg=t["text_primary"], selectcolor=t["bg_card"], activebackground=t["bg_card"], activeforeground=t["text_primary"])
        self.entry_test.config(bg=t["entry_bg"], fg=t["text_primary"], insertbackground=t["text_primary"])
        
        self._refresh_mappings_table()

    def _toggle_power(self):
        """Toggle remapper engine ON / OFF."""
        is_enabled = self.engine.toggle_enabled()
        t = self.theme
        if is_enabled:
            self.btn_power.config(text="🟢 REMAPPING ENABLED", bg=t["accent_green"])
            self.lbl_status.config(text="Ready. Remapper is ACTIVE system-wide.", fg=t["accent_green"])
        else:
            self.btn_power.config(text="🔴 REMAPPING DISABLED", bg=t["accent_red"])
            self.lbl_status.config(text="Remapper is PAUSED. Keys function normally.", fg=t["accent_red"])

    def _start_key_detection(self, target_input: str):
        """Listen for next physical keypress to auto-detect key."""
        self.detecting_for = target_input
        btn = self.btn_detect_src if target_input == "src" else self.btn_detect_tgt
        btn.config(text="⌨️ Press Any Key...", bg=self.theme["accent_amber"])
        self.lbl_status.config(text=f"Listening for physical keypress for {target_input.upper()} key...", fg=self.theme["accent_amber"])
        self.engine.enable_detection(self._on_key_detected)

    def _on_key_detected(self, vk_code: int):
        """Callback invoked when physical key is detected."""
        key_name = get_key_name(vk_code)
        
        def update_ui():
            if self.detecting_for == "src":
                self.combo_src_key.set(key_name)
                self.btn_detect_src.config(text="🎯 Detect Key", bg=self.theme["accent_blue"])
            elif self.detecting_for == "tgt":
                self.combo_tgt_key.set(key_name)
                self.btn_detect_tgt.config(text="🎯 Detect Key", bg=self.theme["accent_blue"])
                
            self.lbl_status.config(text=f"Detected key: {key_name} (Code: 0x{vk_code:02X})", fg=self.theme["accent_green"])
            self.detecting_for = None
            
        self.root.after(0, update_ui)

    def _add_mapping_rule(self):
        """Add key remapping entry to active table."""
        src_str = self.combo_src_key.get().strip()
        tgt_str = self.combo_tgt_key.get().strip()
        
        if not src_str or not tgt_str:
            messagebox.showwarning("Missing Key", "Please select or detect both Source and Target keys.")
            return
            
        src_vk = get_vk_code(src_str)
        if src_vk is None:
            try:
                src_vk = int(src_str, 0)
            except ValueError:
                messagebox.showerror("Invalid Key", f"Unknown source key: {src_str}")
                return

        tgt_vk = get_vk_code(tgt_str)
        if tgt_vk is None:
            try:
                tgt_vk = int(tgt_str, 0)
            except ValueError:
                messagebox.showerror("Invalid Key", f"Unknown target key: {tgt_str}")
                return
                
        if src_vk == tgt_vk:
            messagebox.showwarning("Same Key", "Source key and Target key cannot be identical.")
            return

        is_update = src_vk in self.profile_mgr.mappings
        prev_tgt = self.profile_mgr.mappings.get(src_vk)
        
        if is_update and prev_tgt == tgt_vk:
            messagebox.showinfo("Duplicate Rule", f"The rule '{get_key_name(src_vk)} ➡️ {get_key_name(tgt_vk)}' is already active in your table.")
            return

        self.profile_mgr.mappings[src_vk] = tgt_vk
        self.engine.set_remap_table(self.profile_mgr.mappings)
        self._save_current_profile()
        self._refresh_mappings_table()
        
        if is_update:
            self.lbl_status.config(text=f"Updated rule: {get_key_name(src_vk)} ➡️ {get_key_name(tgt_vk)}", fg=self.theme["accent_green"])
        else:
            self.lbl_status.config(text=f"Added rule: {get_key_name(src_vk)} ➡️ {get_key_name(tgt_vk)}", fg=self.theme["accent_green"])

    def _remove_selected_rule(self):
        """Delete selected remap rule from table."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Selection Required", "Please select a rule from the table to remove.")
            return
            
        item = self.tree.item(selected[0])
        src_vk = int(item["values"][1], 16)
        
        if src_vk in self.profile_mgr.mappings:
            del self.profile_mgr.mappings[src_vk]
            self.engine.set_remap_table(self.profile_mgr.mappings)
            self._save_current_profile()
            self._refresh_mappings_table()
            self.lbl_status.config(text="Removed key remapping rule.", fg=self.theme["text_secondary"])

    def _refresh_mappings_table(self):
        """Redraw rows in treeview table and update visual keyboard key colors."""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        t = self.theme
        # Reset all visual keys to active theme key color
        for vk_code, btn_list in self.key_buttons.items():
            for btn in btn_list:
                btn.config(bg=t["key_normal_bg"], fg=t["key_text"])

        # Highlight remapped keys on visual keyboard
        for src_vk, tgt_vk in self.profile_mgr.mappings.items():
            self.tree.insert("", "end", values=(
                get_key_name(src_vk),
                f"0x{src_vk:02X}",
                get_key_name(tgt_vk),
                f"0x{tgt_vk:02X}"
            ))
            
            if src_vk in self.key_buttons:
                for btn in self.key_buttons[src_vk]:
                    btn.config(bg=t["key_remapped_bg"], fg="#ffffff")

    def _update_profile_dropdown(self):
        """Update profile combobox choices."""
        profiles = self.profile_mgr.get_available_profiles()
        self.combo_profile["values"] = profiles
        if self.profile_mgr.current_profile_name in profiles:
            self.combo_profile.set(self.profile_mgr.current_profile_name)

    def _load_current_profile(self):
        """Load mappings from active profile into engine and table."""
        self._update_profile_dropdown()
        mappings = self.profile_mgr.load_profile(self.combo_profile.get() or "default")
        self.engine.set_remap_table(mappings)
        self._refresh_mappings_table()

    def _on_profile_selected(self, event):
        """Handle profile dropdown switch."""
        name = self.combo_profile.get()
        mappings = self.profile_mgr.load_profile(name)
        self.engine.set_remap_table(mappings)
        self._refresh_mappings_table()
        self.lbl_status.config(text=f"Loaded profile: {name}", fg=self.theme["accent_green"])

    def _save_current_profile(self):
        """Save active mappings to disk."""
        name = self.combo_profile.get() or "default"
        self.profile_mgr.save_profile(name, self.profile_mgr.mappings)
        self.lbl_status.config(text=f"Saved profile '{name}' to disk.", fg=self.theme["accent_green"])

    def _create_new_profile(self):
        """Prompt user for new profile name."""
        name = simpledialog.askstring("New Profile", "Enter profile name (e.g. Gaming, Work):", parent=self.root)
        if name:
            name = name.strip().lower().replace(" ", "_")
            self.profile_mgr.save_profile(name, {})
            self._update_profile_dropdown()
            self.combo_profile.set(name)
            self._on_profile_selected(None)

    def _delete_current_profile(self):
        """Delete active profile."""
        name = self.combo_profile.get()
        if name == "default":
            messagebox.showwarning("Default Profile", "Cannot delete the 'default' profile.")
            return
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete profile '{name}'?"):
            self.profile_mgr.delete_profile(name)
            self._update_profile_dropdown()
            self.combo_profile.set("default")
            self._on_profile_selected(None)

    def on_close(self):
        """Clean application shutdown."""
        self.engine.stop()
        self.root.destroy()
