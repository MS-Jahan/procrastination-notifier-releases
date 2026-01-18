# Nuitka Build Configuration
# This file contains configuration for building Focus Warden with Nuitka

# Build Notes:
# - Icons are optional - builds will work without them
# - To add icons, place them in assets/:
#   - assets/icon.png (Linux, any size, preferably 512x512)
#   - assets/icon.ico (Windows, multi-resolution .ico file)
#   - assets/icon.icns (macOS, use iconutil to create from iconset)

# Platform-specific considerations:
#
# Windows:
# - --windows-console-mode=disable: No console window (GUI only)
# - Creates single .exe file
#
# macOS:
# - --macos-create-app-bundle: Creates .app bundle
# - Not code-signed (users must right-click → Open first time)
# - Screen Recording permission required (see MACOS_SETUP.md)
#
# Linux:
# - Creates standalone binary
# - Requires patchelf installed on build system
# - Works on most modern distros

# Nuitka Plugins Used:
# - tk-inter: Required for customtkinter/tkinter support

# Performance Options:
# - --onefile: Single executable (slower startup, easier distribution)
# - Alternative: --standalone (faster startup, multiple files)

# To build locally:
# pip install nuitka ordered-set zstandard
# python -m nuitka --standalone --onefile --enable-plugin=tk-inter focus_warden.py
