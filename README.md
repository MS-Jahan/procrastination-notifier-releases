# 🎯 Focus Warden - AI Procrastination Detector

An AI-powered productivity tool that monitors your screen and keeps you accountable. Uses **Google Gemini 2.5 Flash** to analyze screenshots and determine if you're working or procrastinating.

![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-blue)

## 📥 Download & Install

**[Get the Latest Release](https://github.com/MS-Jahan/procrastination-notifier-releases/releases/latest)**

| OS | Download | Setup |
|----|----------|-------|
| **Windows** | [`FocusWarden-Windows.zip`](https://github.com/MS-Jahan/procrastination-notifier-releases/releases/latest/download/FocusWarden-Windows.zip) | Extract `.zip`, run `FocusWarden.exe`. (Click "Run Anyway" if Defender warns you) |
| **macOS** | [`FocusWarden-macOS.zip`](https://github.com/MS-Jahan/procrastination-notifier-releases/releases/latest/download/FocusWarden-macOS.zip) | Extract `.zip`, right-click `FocusWarden.app` -> Open. (See [Setup Guide](MACOS_SETUP.md)) |
| **Linux** | [`FocusWarden-Linux.tar.gz`](https://github.com/MS-Jahan/procrastination-notifier-releases/releases/latest/download/FocusWarden-Linux.tar.gz) | Extract, ensure executable (`chmod +x FocusWarden`), run `./FocusWarden` |

## ✨ Features

- **🤖 AI-Powered Analysis**: Uses Gemini 2.5 Flash to understand screen context
- **📸 Periodic Screenshots**: Configurable check intervals (default: 60 seconds)
- **🎯 Context-Aware**: Knows that Stack Overflow might be work, not slacking!
- **🖥️ Modern Dark UI**: Beautiful interface that stays out of your way
- **📋 Activity Log**: Track your productivity history
- **🔔 Gentle Alerts**: Window pops up when you're caught slacking

## 🚀 Quick Start

### 1. Get a Free Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click "Create API Key"
3. Copy your key

*(Free Tier Limits: 15 requests/minute, 1,500 requests/day - plenty for personal use)*

### 2. Run the App

1. Launch **Focus Warden**
2. Paste your API Key into the settings
3. Enter your **Project Name** and **Goal** (e.g., "Writing Code", "Finishing the report")
4. Click **Start Monitoring**

## 📖 How It Works

1. **Set Your Goal**: Tell the AI what you SHOULD be doing.
2. **Work Normally**: Minimize the app.
3. **Get Feedback**: The AI periodically checks your screen.
   - ✅ **WORKING**: You're focused! (Silent notification)
   - 🚨 **PROCRASTINATING**: You're on Reddit/YouTube? The window pops up to nudge you back.

## 🛠️ Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| Check Interval | 60 seconds | How often to analyze the screen |
| Model | gemini-2.5-flash... | Gemini model to use (Flash is recommended) |

## 🔒 Privacy

- Screenshots are processed in real-time and **not stored**
- Images are sent directly to Google's Gemini API for analysis only
- No data is saved locally (except your session history log)

## 🐛 Troubleshooting

### macOS: "App is damaged" or "Cannot be opened"
Apple blocks unsigned apps by default. To fix:
1. Move the app to your Applications folder.
2. Right-click the app icon and select **Open**.
3. Click **Open** in the dialog box.
4. Grant **Screen Recording** permissions in System Settings when asked.
See [MACOS_SETUP.md](MACOS_SETUP.md) for details.

### "Screenshot failed"
Ensure you have granted screen recording permissions to the app.

---

Made with ☕ and a desire to actually finish my projects
