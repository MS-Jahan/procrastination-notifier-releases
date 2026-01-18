#!/usr/bin/env python3
"""
Focus Warden - AI-Powered Procrastination Detector
Uses Google Gemini 2.5 Flash to analyze your screen and determine if you're working or slacking.
"""

import threading
import time
import os
import io
import json
import base64
import subprocess
import logging
from datetime import datetime
from pathlib import Path

# Setup logging - both file and console
LOG_FILE = Path(__file__).parent / "focus_warden.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

try:
    import pyautogui
except ImportError:
    print("Installing pyautogui...")
    os.system("pip install pyautogui")
    import pyautogui

try:
    from PIL import Image
except ImportError:
    print("Installing Pillow...")
    os.system("pip install Pillow")
    from PIL import Image

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("Installing google-genai...")
    os.system("pip install google-genai")
    from google import genai
    from google.genai import types

try:
    import customtkinter as ctk
except ImportError:
    print("Installing customtkinter...")
    os.system("pip install customtkinter")
    import customtkinter as ctk

# --- CONFIGURATION ---
# Set your API key as environment variable GEMINI_API_KEY or replace below
API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")
DEFAULT_CHECK_INTERVAL = 60  # Check every 60 seconds by default

# Model selection - Using Gemini 2.0 Flash (stable, fast, cheap, free tier available)
# Free tier: 15 RPM, 1,500 daily requests, 1M token context
MODEL_NAME = "gemini-2.0-flash"
# Config file path (stored in same directory as script)
CONFIG_FILE = Path(__file__).parent / "focus_warden_config.json"
HISTORY_FILE = Path(__file__).parent / "focus_warden_history.json"

# Available Gemini models (will be updated from API if possible)
DEFAULT_MODELS = [
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite", 
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b",
    "gemini-1.5-pro",
]


class FocusApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("🎯 Focus Warden AI")
        self.geometry("900x550")
        self.resizable(True, True)
        self.is_running = False
        self.client = None
        self.check_interval = DEFAULT_CHECK_INTERVAL
        self.notifications_enabled = True
        self.selected_model = MODEL_NAME
        self.available_models = DEFAULT_MODELS.copy()
        self._save_timer = None  # For debounced auto-save
        
        # Color scheme
        self.colors = {
            "accent": "#6366f1",       # Indigo
            "success": "#22c55e",      # Green
            "warning": "#f59e0b",      # Amber
            "danger": "#ef4444",       # Red
            "bg_dark": "#0f172a",      # Slate 900
            "bg_card": "#1e293b",      # Slate 800
            "text": "#f8fafc",         # Slate 50
            "text_muted": "#94a3b8",   # Slate 400
        }
        
        self.configure(fg_color=self.colors["bg_dark"])
        
        # Load saved settings
        self._load_config()
        
        self._setup_ui()
        
        # Save settings on close
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _bind_select_all(self, widget):
        """Bind Ctrl+A to select all text in the widget"""
        if isinstance(widget, ctk.CTkEntry):
            def select_all_entry(event):
                widget.select_range(0, 'end')
                return "break"
            widget.bind("<Control-a>", select_all_entry)
        elif isinstance(widget, ctk.CTkTextbox):
            def select_all_textbox(event):
                widget.tag_add('sel', '1.0', 'end')
                return "break"
            widget.bind("<Control-a>", select_all_textbox)
    
    def _obfuscate(self, text: str) -> str:
        """Simple obfuscation for API key (not cryptographically secure, but better than plain text)"""
        if not text:
            return ""
        # XOR with a key and base64 encode
        key = "FocusWarden2025"
        result = []
        for i, char in enumerate(text):
            result.append(chr(ord(char) ^ ord(key[i % len(key)])))
        return base64.b64encode(''.join(result).encode('utf-8')).decode('utf-8')
    
    def _deobfuscate(self, encoded: str) -> str:
        """Reverse obfuscation for API key"""
        if not encoded:
            return ""
        try:
            decoded = base64.b64decode(encoded.encode('utf-8')).decode('utf-8')
            key = "FocusWarden2025"
            result = []
            for i, char in enumerate(decoded):
                result.append(chr(ord(char) ^ ord(key[i % len(key)])))
            return ''.join(result)
        except Exception:
            return ""
        
    def _load_config(self):
        """Load saved settings from config file"""
        self.saved_config = {
            "api_key_obf": "",
            "project": "",
            "task": "",
            "interval": DEFAULT_CHECK_INTERVAL,
            "notifications": True,
            "geometry": None,
            "model": MODEL_NAME
        }
        
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, 'r') as f:
                    loaded = json.load(f)
                    self.saved_config.update(loaded)
                    
                # Decode the obfuscated API key
                if self.saved_config.get("api_key_obf"):
                    self.saved_config["api_key"] = self._deobfuscate(self.saved_config["api_key_obf"])
                else:
                    self.saved_config["api_key"] = ""
                    
                # Apply loaded settings
                self.check_interval = self.saved_config.get("interval", DEFAULT_CHECK_INTERVAL)
                self.notifications_enabled = self.saved_config.get("notifications", True)
                self.selected_model = self.saved_config.get("model", MODEL_NAME)
                
                # Apply window geometry if saved
                if self.saved_config.get("geometry"):
                    self.geometry(self.saved_config["geometry"])
        except (json.JSONDecodeError, IOError):
            # If config is corrupted, use defaults
            pass
    
    def _queue_save(self, *args):
        """Queue a config save with debouncing (waits 500ms after last change)"""
        # Cancel any pending save
        if self._save_timer is not None:
            self.after_cancel(self._save_timer)
        # Schedule new save
        self._save_timer = self.after(500, self._save_config)
    
    def _save_config(self):
        """Save current settings to config file"""
        self._save_timer = None  # Clear timer reference
        
        # Get current window geometry
        try:
            self.update_idletasks()  # Ensure geometry is up to date
            geometry = self.geometry()
        except:
            geometry = self.saved_config.get("geometry", "500x650")
        
        # Get model from dropdown if it exists
        try:
            model = self.model_var.get() if hasattr(self, 'model_var') else self.selected_model
        except:
            model = self.selected_model
        
        config = {
            "api_key_obf": self._obfuscate(self.entry_api.get().strip()) if hasattr(self, 'entry_api') else "",
            "project": self.entry_proj.get().strip() if hasattr(self, 'entry_proj') else "",
            "task": self.entry_task.get("0.0", "end").strip() if hasattr(self, 'entry_task') else "",
            "interval": int(self.interval_var.get()) if hasattr(self, 'interval_var') and self.interval_var.get().isdigit() else DEFAULT_CHECK_INTERVAL,
            "notifications": self.notif_var.get() if hasattr(self, 'notif_var') else True,
            "geometry": geometry,
            "model": model
        }
        
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
        except IOError:
            pass  # Silently fail if we can't write config
    
    def _on_close(self):
        """Handle window close - save config and exit"""
        # Cancel pending timer and save immediately
        if self._save_timer is not None:
            self.after_cancel(self._save_timer)
        self._save_config()
        self.is_running = False
        self.destroy()

    def _load_history(self):
        """Load history from file"""
        try:
            if HISTORY_FILE.exists():
                with open(HISTORY_FILE, 'r') as f:
                    history = json.load(f)
                    # Keep only last 50 entries
                    return history[-50:] if len(history) > 50 else history
        except Exception as e:
            logger.error(f"Error loading history: {e}")
        return []

    def _save_history_entry(self):
        """Save current project/task to history"""
        project = self.entry_proj.get().strip()
        task = self.entry_task.get("0.0", "end").strip()
        
        if not project and not task:
            return  # Don't save empty entries
        
        try:
            history = self._load_history()
            
            # Check if entry with same project and task already exists
            existing_index = None
            for i, entry in enumerate(history):
                if entry.get("project") == project and entry.get("task") == task:
                    existing_index = i
                    break
            
            if existing_index is not None:
                # Update existing entry's timestamps
                history[existing_index]["timestamp"] = datetime.now().isoformat()
                history[existing_index]["start_time"] = datetime.now().isoformat()
                logger.info(f"Updated history entry: {project}")
            else:
                # Create new entry
                entry = {
                    "project": project,
                    "task": task,
                    "timestamp": datetime.now().isoformat(),
                    "start_time": datetime.now().isoformat()
                }
                history.append(entry)
                logger.info(f"Saved history entry: {project}")
            
            # Keep only last 50 entries
            history = history[-50:]
            
            with open(HISTORY_FILE, 'w') as f:
                json.dump(history, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving history: {e}")

    def _show_history_dialog(self):
        """Show history selection dialog"""
        history = self._load_history()
        
        if not history:
            self.log_message("📜 No history found")
            return
        
        # Create dialog window
        dialog = ctk.CTkToplevel(self)
        dialog.title("📜 Project History")
        dialog.geometry("700x500")
        dialog.configure(fg_color=self.colors["bg_dark"])
        
        # Make it modal
        dialog.transient(self)
        dialog.update()  # Force window to render
        dialog.grab_set()
        
        # Header
        header = ctk.CTkLabel(
            dialog,
            text="📜 Project History",
            font=("Helvetica", 20, "bold"),
            text_color=self.colors["text"]
        )
        header.pack(pady=(20, 10))
        
        # List frame
        list_frame = ctk.CTkFrame(dialog, fg_color=self.colors["bg_card"])
        list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        # Scrollable frame for history items
        scrollable = ctk.CTkScrollableFrame(
            list_frame,
            fg_color="transparent"
        )
        scrollable.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Reverse to show newest first
        history.reverse()
        
        selected_entry = {"value": None}
        
        def on_entry_click(entry):
            selected_entry["value"] = entry
            dialog.destroy()
        
        def on_delete_click(entry, item_frame):
            # Remove from history
            history_list = self._load_history()
            history_list = [h for h in history_list if h.get("timestamp") != entry.get("timestamp")]
            
            with open(HISTORY_FILE, 'w') as f:
                json.dump(history_list, f, indent=2)
            
            # Remove from UI
            item_frame.destroy()
            self.log_message(f"🗑️ Deleted history entry: {entry.get('project', 'Untitled')}")
        
        # Create history items
        for entry in history:
            item_frame = ctk.CTkFrame(scrollable, fg_color=self.colors["bg_dark"], corner_radius=8)
            item_frame.pack(fill="x", pady=5)
            
            # Content frame (clickable)
            content_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            content_frame.pack(side="left", fill="both", expand=True, padx=10, pady=8)
            
            project = entry.get("project", "Untitled Project")
            task = entry.get("task", "")
            timestamp = entry.get("timestamp", "")
            
            # Parse timestamp
            try:
                dt = datetime.fromisoformat(timestamp)
                time_str = dt.strftime("%Y-%m-%d %H:%M")
            except:
                time_str = timestamp
            
            # Project title
            proj_label = ctk.CTkLabel(
                content_frame,
                text=f"📁 {project}",
                font=("Helvetica", 13, "bold"),
                text_color=self.colors["text"],
                anchor="w"
            )
            proj_label.pack(anchor="w", fill="x")
            
            # Task preview (first 50 chars)
            task_preview = task[:50] + "..." if len(task) > 50 else task
            task_label = ctk.CTkLabel(
                content_frame,
                text=task_preview,
                font=("Helvetica", 10),
                text_color=self.colors["text_muted"],
                anchor="w"
            )
            task_label.pack(anchor="w", fill="x")
            
            # Timestamp
            time_label = ctk.CTkLabel(
                content_frame,
                text=f"🕒 {time_str}",
                font=("Helvetica", 9),
                text_color=self.colors["text_muted"],
                anchor="w"
            )
            time_label.pack(anchor="w")
            
            # Make content clickable
            content_frame.bind("<Button-1>", lambda e, entry=entry: on_entry_click(entry))
            proj_label.bind("<Button-1>", lambda e, entry=entry: on_entry_click(entry))
            task_label.bind("<Button-1>", lambda e, entry=entry: on_entry_click(entry))
            time_label.bind("<Button-1>", lambda e, entry=entry: on_entry_click(entry))
            
            # Delete button
            delete_btn = ctk.CTkButton(
                item_frame,
                text="🗑️",
                width=40,
                height=30,
                fg_color=self.colors["danger"],
                hover_color="#dc2626",
                command=lambda e=entry, f=item_frame: on_delete_click(e, f)
            )
            delete_btn.pack(side="right", padx=10)
        
        # Keyboard shortcuts
        def on_key(event):
            if event.keysym == "Escape":
                selected_entry["value"] = None
                dialog.destroy()
        
        dialog.bind("<Key>", on_key)
        
        # Wait for dialog to close
        dialog.wait_window()
        
        # Handle selection
        if selected_entry["value"]:
            self._load_history_entry(selected_entry["value"])

    def _load_history_entry(self, entry):
        """Load a history entry into the input fields"""
        project = entry.get("project", "")
        task = entry.get("task", "")
        
        # Check if current fields are empty
        current_project = self.entry_proj.get().strip()
        current_task = self.entry_task.get("0.0", "end").strip()
        
        if current_project or current_task:
            # Show confirmation dialog
            confirm = ctk.CTkToplevel(self)
            confirm.title("Confirm Replace")
            confirm.geometry("400x200")
            confirm.configure(fg_color=self.colors["bg_dark"])
            confirm.transient(self)
            confirm.update()  # Force window to render
            confirm.grab_set()
            
            label = ctk.CTkLabel(
                confirm,
                text="⚠️ Replace current project and task?",
                font=("Helvetica", 14, "bold"),
                text_color=self.colors["text"]
            )
            label.pack(pady=30)
            
            msg = ctk.CTkLabel(
                confirm,
                text="This will overwrite your current unsaved work.",
                font=("Helvetica", 11),
                text_color=self.colors["text_muted"]
            )
            msg.pack(pady=(0, 20))
            
            result = {"confirmed": False}
            
            def on_yes():
                result["confirmed"] = True
                confirm.destroy()
            
            def on_no():
                confirm.destroy()
            
            btn_frame = ctk.CTkFrame(confirm, fg_color="transparent")
            btn_frame.pack()
            
            yes_btn = ctk.CTkButton(
                btn_frame,
                text="Yes, Replace",
                command=on_yes,
                fg_color=self.colors["accent"],
                width=120
            )
            yes_btn.pack(side="left", padx=10)
            
            no_btn = ctk.CTkButton(
                btn_frame,
                text="Cancel",
                command=on_no,
                fg_color=self.colors["bg_card"],
                width=120
            )
            no_btn.pack(side="left", padx=10)
            
            confirm.wait_window()
            
            if not result["confirmed"]:
                return
        
        # Load the entry
        self.entry_proj.delete(0, 'end')
        self.entry_proj.insert(0, project)
        
        self.entry_task.delete("0.0", "end")
        self.entry_task.insert("0.0", task)
        
        self.log_message(f"📜 Loaded from history: {project}")
        
    def _setup_ui(self):
        """Setup the user interface"""
        # Main container with padding
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header = ctk.CTkLabel(
            main_frame, 
            text="🎯 Focus Warden", 
            font=("Helvetica", 28, "bold"),
            text_color=self.colors["text"]
        )
        header.pack(pady=(0, 5))
        
        subtitle = ctk.CTkLabel(
            main_frame,
            text="AI-Powered Productivity Guardian",
            font=("Helvetica", 12),
            text_color=self.colors["text_muted"]
        )
        subtitle.pack(pady=(0, 15))
        
        # Two-column container
        columns_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        columns_frame.pack(fill="both", expand=True)
        columns_frame.grid_columnconfigure(0, weight=1)
        columns_frame.grid_columnconfigure(1, weight=1)
        columns_frame.grid_rowconfigure(0, weight=1)
        
        # ========== LEFT COLUMN (Settings) ==========
        left_col = ctk.CTkFrame(columns_frame, fg_color="transparent")
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # API Key Section
        api_frame = ctk.CTkFrame(left_col, fg_color=self.colors["bg_card"], corner_radius=12)
        api_frame.pack(fill="x", pady=(0, 10))
        
        api_label = ctk.CTkLabel(
            api_frame, 
            text="🔑 Gemini API Key", 
            font=("Helvetica", 12, "bold"),
            text_color=self.colors["text"]
        )
        api_label.pack(anchor="w", padx=15, pady=(12, 5))
        
        self.entry_api = ctk.CTkEntry(
            api_frame, 
            height=35,
            placeholder_text="Enter your Gemini API key...",
            show="•",
            fg_color=self.colors["bg_dark"],
            border_color=self.colors["accent"],
            corner_radius=8
        )
        self.entry_api.pack(fill="x", padx=15, pady=(0, 8))
        
        # Pre-fill API key from saved config or environment
        saved_api = self.saved_config.get("api_key", "")
        if saved_api:
            self.entry_api.insert(0, saved_api)
        elif API_KEY and API_KEY != "YOUR_GEMINI_API_KEY_HERE":
            self.entry_api.insert(0, API_KEY)
        
        # Bind API key changes to auto-save
        self.entry_api.bind("<KeyRelease>", self._queue_save)
        
        # Bind Ctrl+A for select all
        self._bind_select_all(self.entry_api)
        
        # Advanced Settings (collapsible)
        self.advanced_visible = False
        
        advanced_toggle = ctk.CTkButton(
            api_frame,
            text="⚙️ Advanced Settings ▼",
            command=self._toggle_advanced,
            fg_color="transparent",
            hover_color=self.colors["bg_dark"],
            text_color=self.colors["text_muted"],
            height=28,
            anchor="w"
        )
        advanced_toggle.pack(anchor="w", padx=15, pady=(0, 5))
        self.advanced_toggle_btn = advanced_toggle
        
        # Advanced settings container (hidden by default)
        self.advanced_frame = ctk.CTkFrame(api_frame, fg_color="transparent")
        
        # Model selection
        model_label = ctk.CTkLabel(
            self.advanced_frame, 
            text="🤖 Model:", 
            font=("Helvetica", 11),
            text_color=self.colors["text_muted"]
        )
        model_label.pack(anchor="w", padx=15, pady=(5, 2))
        
        self.model_var = ctk.StringVar(value=self.selected_model)
        self.model_dropdown = ctk.CTkComboBox(
            self.advanced_frame,
            height=32,
            values=self.available_models,
            variable=self.model_var,
            fg_color=self.colors["bg_dark"],
            border_color=self.colors["accent"],
            button_color=self.colors["accent"],
            dropdown_fg_color=self.colors["bg_card"],
            command=self._on_model_change
        )
        self.model_dropdown.pack(fill="x", padx=15, pady=(0, 5))
        
        # Refresh models button
        refresh_btn = ctk.CTkButton(
            self.advanced_frame,
            text="🔄 Refresh Models",
            command=self._fetch_models,
            fg_color=self.colors["bg_dark"],
            hover_color=self.colors["accent"],
            height=28,
            font=("Helvetica", 10)
        )
        refresh_btn.pack(anchor="w", padx=15, pady=(0, 12))

        # Project Details Card
        project_frame = ctk.CTkFrame(left_col, fg_color=self.colors["bg_card"], corner_radius=12)
        project_frame.pack(fill="x", pady=(0, 10))
        
        proj_label = ctk.CTkLabel(
            project_frame, 
            text="📁 Current Project", 
            font=("Helvetica", 12, "bold"),
            text_color=self.colors["text"]
        )
        proj_label.pack(anchor="w", padx=15, pady=(12, 5))
        
        self.entry_proj = ctk.CTkEntry(
            project_frame, 
            height=35,
            placeholder_text="e.g., Thesis, Client Project",
            fg_color=self.colors["bg_dark"],
            border_color=self.colors["accent"],
            corner_radius=8
        )
        self.entry_proj.pack(fill="x", padx=15, pady=(0, 12))
        
        # Pre-fill project from saved config
        saved_project = self.saved_config.get("project", "")
        if saved_project:
            self.entry_proj.insert(0, saved_project)
        
        # Bind project changes to auto-save
        self.entry_proj.bind("<KeyRelease>", self._queue_save)
        
        # Bind Ctrl+A for select all
        self._bind_select_all(self.entry_proj)
        
        # Task Details Card
        task_frame = ctk.CTkFrame(left_col, fg_color=self.colors["bg_card"], corner_radius=12)
        task_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        task_label = ctk.CTkLabel(
            task_frame, 
            text="📝 What are you working on?", 
            font=("Helvetica", 12, "bold"),
            text_color=self.colors["text"]
        )
        task_label.pack(anchor="w", padx=15, pady=(12, 5))
        
        self.entry_task = ctk.CTkTextbox(
            task_frame, 
            height=80,
            fg_color=self.colors["bg_dark"],
            corner_radius=8
        )
        self.entry_task.pack(fill="both", expand=True, padx=15, pady=(0, 12))
        
        # Pre-fill task from saved config
        saved_task = self.saved_config.get("task", "")
        if saved_task:
            self.entry_task.insert("0.0", saved_task)
        
        # Bind task changes to auto-save
        self.entry_task.bind("<KeyRelease>", self._queue_save)
        
        # Bind Ctrl+A for select all
        self._bind_select_all(self.entry_task)
        
        # History button
        history_btn = ctk.CTkButton(
            task_frame,
            text="📜 History",
            command=self._show_history_dialog,
            fg_color=self.colors["accent"],
            hover_color="#5558d9",
            height=32,
            corner_radius=8,
            font=("Helvetica", 11)
        )
        history_btn.pack(fill="x", padx=15, pady=(0, 12))
        
        # Settings Row (Interval + Notifications)
        settings_frame = ctk.CTkFrame(left_col, fg_color=self.colors["bg_card"], corner_radius=12)
        settings_frame.pack(fill="x")
        
        # Interval
        interval_inner = ctk.CTkFrame(settings_frame, fg_color="transparent")
        interval_inner.pack(fill="x", padx=15, pady=10)
        
        interval_label = ctk.CTkLabel(
            interval_inner, 
            text="⏱️ Interval (sec):", 
            font=("Helvetica", 11),
            text_color=self.colors["text"]
        )
        interval_label.pack(side="left")
        
        self.interval_var = ctk.StringVar(value=str(self.saved_config.get("interval", DEFAULT_CHECK_INTERVAL)))
        self.interval_entry = ctk.CTkEntry(
            interval_inner,
            width=60,
            height=28,
            textvariable=self.interval_var,
            fg_color=self.colors["bg_dark"],
            border_color=self.colors["accent"],
            corner_radius=6
        )
        self.interval_entry.pack(side="left", padx=(10, 20))
        
        # Bind interval changes to auto-save
        self.interval_entry.bind("<KeyRelease>", self._queue_save)
        
        # Bind Ctrl+A for select all
        self._bind_select_all(self.interval_entry)
        
        # Notifications
        notif_label = ctk.CTkLabel(
            interval_inner, 
            text="🔔 Notifications:", 
            font=("Helvetica", 11),
            text_color=self.colors["text"]
        )
        notif_label.pack(side="left")
        
        self.notif_var = ctk.BooleanVar(value=self.saved_config.get("notifications", True))
        self.notif_switch = ctk.CTkSwitch(
            interval_inner,
            text="",
            variable=self.notif_var,
            command=self._toggle_notifications,
            onvalue=True,
            offvalue=False,
            width=40,
            fg_color=self.colors["accent"],
            progress_color=self.colors["success"]
        )
        self.notif_switch.pack(side="left", padx=(5, 0))
        
        # ========== RIGHT COLUMN (Monitoring) ==========
        right_col = ctk.CTkFrame(columns_frame, fg_color="transparent")
        right_col.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        # Start/Stop Button
        self.btn_start = ctk.CTkButton(
            right_col, 
            text="▶️  Start Watching Me", 
            command=self.toggle_monitoring,
            fg_color=self.colors["success"],
            hover_color="#16a34a",
            height=50,
            corner_radius=10,
            font=("Helvetica", 16, "bold")
        )
        self.btn_start.pack(fill="x", pady=(0, 15))
        
        # Status Display
        status_frame = ctk.CTkFrame(right_col, fg_color=self.colors["bg_card"], corner_radius=12)
        status_frame.pack(fill="x", pady=(0, 15))
        
        self.status_label = ctk.CTkLabel(
            status_frame, 
            text="💤 Status: Idle", 
            font=("Helvetica", 18, "bold"),
            text_color=self.colors["text_muted"]
        )
        self.status_label.pack(pady=20)
        
        # Activity Log
        log_label = ctk.CTkLabel(
            right_col, 
            text="📋 Activity Log", 
            font=("Helvetica", 12, "bold"),
            text_color=self.colors["text"]
        )
        log_label.pack(anchor="w", pady=(0, 5))
        
        self.log_box = ctk.CTkTextbox(
            right_col, 
            fg_color=self.colors["bg_card"],
            corner_radius=10,
            state="disabled"
        )
        self.log_box.pack(fill="both", expand=True)
        
        # Footer
        footer = ctk.CTkLabel(
            main_frame,
            text=f"Using {self.selected_model} | Free tier: 15 RPM, 1500/day",
            font=("Helvetica", 10),
            text_color=self.colors["text_muted"]
        )
        footer.pack(pady=(10, 0))
        
        # Store footer reference for updating
        self.footer_label = footer
        
        # Auto-fetch models if API key is available
        saved_api = self.saved_config.get("api_key", "")
        if saved_api:
            self.after(1000, self._fetch_models)  # Delay to let UI load first
        
        # Bind global keyboard shortcuts
        self.bind("<Control-h>", lambda e: self._show_history_dialog())

    def _toggle_advanced(self):
        """Toggle advanced settings visibility"""
        if self.advanced_visible:
            self.advanced_frame.pack_forget()
            self.advanced_toggle_btn.configure(text="⚙️ Advanced Settings ▼")
        else:
            self.advanced_frame.pack(fill="x", after=self.advanced_toggle_btn)
            self.advanced_toggle_btn.configure(text="⚙️ Advanced Settings ▲")
        self.advanced_visible = not self.advanced_visible
    
    def _on_model_change(self, value):
        """Handle model selection change"""
        self.selected_model = value
        # Update footer to show current model
        if hasattr(self, 'footer_label'):
            self.footer_label.configure(text=f"Using {value} | Free tier: 15 RPM, 1500/day")
        self._queue_save()
        self.log_message(f"📦 Model changed to: {value}")
    
    def _fetch_models(self):
        """Fetch available models from the Gemini API"""
        api_key = self.entry_api.get().strip()
        if not api_key or api_key == "YOUR_GEMINI_API_KEY_HERE":
            self.log_message("❌ Enter API key first to fetch models")
            return
        
        self.log_message("🔄 Fetching available models...")
        
        def fetch_in_background():
            try:
                client = genai.Client(api_key=api_key)
                models_response = client.models.list()
                
                # Filter for generative models that support vision
                vision_models = []
                for model in models_response:
                    model_name = model.name if hasattr(model, 'name') else str(model)
                    # Clean up model name (remove 'models/' prefix if present)
                    if model_name.startswith('models/'):
                        model_name = model_name[7:]
                    # Only include gemini models
                    if 'gemini' in model_name.lower():
                        vision_models.append(model_name)
                
                if vision_models:
                    # Sort by name
                    vision_models.sort(reverse=True)
                    self.available_models = vision_models
                    
                    # Update dropdown on main thread
                    self.after(0, lambda m=vision_models: self._update_model_dropdown(m))
                    self.after(0, lambda n=len(vision_models): self.log_message(f"✅ Found {n} models"))
                else:
                    self.after(0, lambda: self.log_message("⚠️ No models found, using defaults"))
                    
            except Exception as ex:
                error_msg = str(ex)[:80]
                logger.error(f"Failed to fetch models: {ex}", exc_info=True)
                self.after(0, lambda msg=error_msg: self.log_message(f"❌ Failed to fetch models: {msg}"))
        
        # Run in background thread
        threading.Thread(target=fetch_in_background, daemon=True).start()
    
    def _update_model_dropdown(self, models):
        """Update the model dropdown with new values"""
        self.model_dropdown.configure(values=models)
        # Keep current selection if it exists in new list
        if self.model_var.get() not in models and models:
            self.model_var.set(models[0])

    def toggle_monitoring(self):
        """Toggle the monitoring state"""
        if not self.is_running:
            # Check macOS permissions first
            if not self._check_macos_permissions():
                return
            
            # Validate API key
            api_key = self.entry_api.get().strip()
            if not api_key or api_key == "YOUR_GEMINI_API_KEY_HERE":
                self.log_message("❌ Error: Please enter a valid Gemini API key!")
                return
            
            # Validate interval
            try:
                self.check_interval = int(self.interval_var.get())
                if self.check_interval < 10:
                    self.check_interval = 10
                    self.log_message("⚠️ Minimum interval is 10 seconds")
            except ValueError:
                self.check_interval = DEFAULT_CHECK_INTERVAL
                self.log_message(f"⚠️ Invalid interval, using {DEFAULT_CHECK_INTERVAL}s")
            
            # Configure API client
            try:
                self.client = genai.Client(api_key=api_key)
                selected = self.model_var.get()
                self.log_message(f"✅ Connected with model: {selected}")
            except Exception as e:
                self.log_message(f"❌ API Error: {e}")
                return
            
            self.is_running = True
            
            # Save to history when starting
            self._save_history_entry()
            
            self.btn_start.configure(
                text="⏹️  Stop Monitoring", 
                fg_color=self.colors["danger"],
                hover_color="#dc2626"
            )
            self.status_label.configure(
                text="👀 Status: WATCHING", 
                text_color=self.colors["warning"]
            )
            
            # Start background monitoring thread
            threading.Thread(target=self.monitor_loop, daemon=True).start()
            self.log_message(f"🚀 Started monitoring every {self.check_interval}s")
        else:
            self.is_running = False
            self.btn_start.configure(
                text="▶️  Start Watching Me", 
                fg_color=self.colors["success"],
                hover_color="#16a34a"
            )
            self.status_label.configure(
                text="💤 Status: Idle", 
                text_color=self.colors["text_muted"]
            )
            self.log_message("⏸️ Monitoring stopped")

    def log_message(self, message: str):
        """Add a message to the activity log"""
        self.log_box.configure(state="normal")
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_box.insert("0.0", f"[{timestamp}] {message}\n")
        self.log_box.configure(state="disabled")
        # Also log to file/console
        logger.info(message)

    def _toggle_notifications(self):
        """Toggle notification state"""
        self.notifications_enabled = self.notif_var.get()
        status = "enabled" if self.notifications_enabled else "disabled"
        self.log_message(f"🔔 Notifications {status}")
        self._queue_save()

    def send_notification(self, title: str, message: str, urgency: str = "normal"):
        """Send a desktop notification (cross-platform)"""
        if not self.notifications_enabled:
            return
        
        import platform
        system = platform.system()
        
        try:
            if system == "Windows":
                # Windows notification
                try:
                    from plyer import notification
                    notification.notify(
                        title=title,
                        message=message,
                        app_name="Focus Warden",
                        timeout=5
                    )
                except ImportError:
                    # Fallback: just log if plyer not available
                    logger.info(f"Notification: {title} - {message}")
            
            elif system == "Darwin":  # macOS
                # Use osascript for native macOS notifications
                script = f'display notification "{message}" with title "{title}"'
                subprocess.run(
                    ["osascript", "-e", script],
                    check=False,
                    capture_output=True
                )
            
            else:  # Linux
                # Use notify-send for Linux
                icon = "dialog-warning" if urgency == "critical" else "dialog-information"
                subprocess.run(
                    ["notify-send", "-u", urgency, "-i", icon, title, message],
                    check=False,
                    capture_output=True
                )
        
        except FileNotFoundError:
            # Notification tool not available, silently skip
            pass
        except Exception as e:
            # Don't crash on notification errors
            logger.debug(f"Notification error: {e}")

    def _check_macos_permissions(self):
        """Check and guide for macOS screen recording permissions"""
        import platform
        if platform.system() != "Darwin":
            return True  # Not macOS, no check needed
        
        try:
            # Try to take a test screenshot
            import pyautogui
            pyautogui.screenshot()
            return True
        except Exception as e:
            # Permission likely denied
            self.log_message("⚠️ macOS Screen Recording permission required!")
            self.log_message("📋 Go to: System Settings > Privacy & Security > Screen Recording")
            self.log_message("📋 Enable permission for Focus Warden, then restart the app")
            return False

    def analyze_screen(self):
        """Take a screenshot and analyze it with Gemini"""
        project = self.entry_proj.get().strip() or "Unknown Project"
        task = self.entry_task.get("0.0", "end").strip() or "General work"
        
        try:
            # 1. Take Screenshot
            screenshot = pyautogui.screenshot()
            
            # Resize to reduce upload size and processing time
            # Maintain aspect ratio while limiting max dimension
            max_dim = 1280
            ratio = min(max_dim / screenshot.width, max_dim / screenshot.height)
            if ratio < 1:
                new_size = (int(screenshot.width * ratio), int(screenshot.height * ratio))
                screenshot = screenshot.resize(new_size, Image.Resampling.LANCZOS)
            
            # Convert PIL Image to bytes for the new API
            img_byte_arr = io.BytesIO()
            screenshot.save(img_byte_arr, format='PNG')
            img_bytes = img_byte_arr.getvalue()
            
            # 2. Construct Prompt
            prompt = f"""You are a strict but fair productivity manager analyzing a screenshot of someone's computer screen.

CONTEXT:
- Project they should be working on: "{project}"
- Specific task they described: "{task}"

INSTRUCTIONS:
1. Identify what applications/websites are currently visible on screen
2. Determine if the screen content is related to their stated work goal
3. Consider that research, documentation, and tool usage related to the project counts as WORKING
4. Social media, entertainment, games, or unrelated browsing counts as PROCRASTINATING

RESPOND IN THIS EXACT FORMAT:
VERDICT: [WORKING or PROCRASTINATING]
CONFIDENCE: [HIGH, MEDIUM, or LOW]
VISIBLE: [Brief description of what you see on screen]
REASON: [One witty sentence - encouraging if working, playfully sarcastic if procrastinating]

Be understanding that some activities like Stack Overflow, documentation, or tutorials might be work-related depending on the task."""

            # 3. Send to Gemini using the new API
            response = self.client.models.generate_content(
                model=self.model_var.get(),
                contents=[
                    types.Content(
                        parts=[
                            types.Part.from_text(text=prompt),
                            types.Part.from_bytes(data=img_bytes, mime_type="image/png"),
                        ]
                    )
                ]
            )
            text = response.text.strip()
            
            # 4. Parse and update UI
            if "PROCRASTINATING" in text.upper():
                self.status_label.configure(
                    text="🚨 CAUGHT SLACKING!", 
                    text_color=self.colors["danger"]
                )
                # Bring window to front briefly
                self.lift()
                self.attributes('-topmost', True)
                self.after(3000, lambda: self.attributes('-topmost', False))
            else:
                self.status_label.configure(
                    text="✅ Great Focus!", 
                    text_color=self.colors["success"]
                )
            
            # Extract and log the reason
            lines = text.split('\n')
            reason_line = next((l for l in lines if 'REASON:' in l.upper()), text)
            reason = reason_line.replace('REASON:', '').strip() if 'REASON:' in reason_line.upper() else text[:100]
            verdict = "SLACKING" if "PROCRASTINATING" in text.upper() else "FOCUSED"
            self.log_message(f"[{verdict}] {reason}")
            
            # Send desktop notification
            if "PROCRASTINATING" in text.upper():
                self.send_notification(
                    "🚨 Focus Warden - Caught Slacking!",
                    reason,
                    urgency="critical"
                )
            else:
                self.send_notification(
                    "✅ Focus Warden - Great Work!",
                    reason,
                    urgency="normal"
                )
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Screen analysis error: {e}", exc_info=True)
            if "API_KEY" in error_msg.upper() or "401" in error_msg:
                self.log_message("❌ Invalid API key")
            elif "429" in error_msg or "quota" in error_msg.lower():
                self.log_message("⚠️ Rate limited - waiting...")
            elif "404" in error_msg:
                self.log_message(f"❌ Model not found: {self.model_var.get()} - try a different model")
            else:
                self.log_message(f"❌ Error: {error_msg[:80]}")

    def monitor_loop(self):
        """Background loop that periodically checks the screen"""
        while self.is_running:
            self.analyze_screen()
            
            # Wait for next check with ability to cancel
            for _ in range(self.check_interval):
                if not self.is_running:
                    break
                time.sleep(1)


def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    app = FocusApp()
    app.mainloop()


if __name__ == "__main__":
    main()
