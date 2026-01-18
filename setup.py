"""
cx_Freeze setup script for Focus Warden
Builds standalone executables for Windows, macOS, and Linux
"""
import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but may need fine tuning
build_exe_options = {
    "packages": [
        "google.genai",
        "customtkinter",
        "PIL",
        "pyautogui",
        "tkinter",
        "plyer",
    ],
    "excludes": [
        "test",
        "unittest",
        "distutils",
        "setuptools",
    ],
    "include_files": [
        # Include customtkinter assets
        # cx_Freeze will automatically find these through package data
    ],
    "optimize": 2,
}

# Platform-specific base
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # No console window on Windows

# Executable configuration
executable = Executable(
    script="focus_warden.py",
    base=base,
    target_name="FocusWarden" if sys.platform != "win32" else "FocusWarden.exe",
    icon=None,  # Add icon path here if you have one
)

setup(
    name="Focus Warden",
    version="1.0.0",
    description="AI-Powered Productivity Guardian",
    options={"build_exe": build_exe_options},
    executables=[executable],
)
