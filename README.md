# 🎯 Focus Warden - AI Procrastination Detector

An AI-powered productivity tool that monitors your screen and keeps you accountable. Uses **Google Gemini 2.5 Flash** to analyze screenshots and determine if you're working or procrastinating.

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Features

- **🤖 AI-Powered Analysis**: Uses Gemini 2.5 Flash to understand screen context
- **📸 Periodic Screenshots**: Configurable check intervals (default: 60 seconds)
- **🎯 Context-Aware**: Knows that Stack Overflow might be work, not slacking!
- **🖥️ Modern Dark UI**: Beautiful customtkinter-based interface
- **📋 Activity Log**: Track your productivity history
- **🔔 Gentle Alerts**: Window pops up when you're caught slacking

## 🚀 Quick Start

### 1. Get a Free Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click "Create API Key"
3. Copy your key

**Free Tier Limits**: 15 requests/minute, 1,500 requests/day, 1M token context

### 2. Install Dependencies

```bash
cd procrastination-notifier
pip install -r requirements.txt
```

### 3. Run the App

```bash
# Option 1: Set API key as environment variable (recommended)
export GEMINI_API_KEY="your-api-key-here"
python focus_warden.py

# Option 2: Just run and enter key in the GUI
python focus_warden.py
```

## 🐳 Docker Usage (Linux with X11)

```bash
# Allow X11 connections
xhost +local:docker

# Set your API key
export GEMINI_API_KEY="your-api-key-here"

# Build and run
docker-compose up --build
```

## 📖 How It Works

1. **Set Your Goal**: Enter your project name and what you're working on
2. **Start Monitoring**: Click the button to begin
3. **Work Normally**: Minimize the app and focus on your work
4. **Get Feedback**: The AI periodically checks if you're on track
   - ✅ **WORKING**: You're focused! Keep it up!
   - 🚨 **PROCRASTINATING**: Caught slacking! Window pops up with a witty comment

## 🛠️ Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| Check Interval | 60 seconds | How often to analyze the screen |
| Model | gemini-2.5-flash-preview-05-20 | Gemini model to use |

## 🔧 Model Options

The app uses `gemini-2.5-flash-preview-05-20` by default. Other options:

| Model | Speed | Price | Notes |
|-------|-------|-------|-------|
| gemini-2.5-flash-preview-05-20 | Fast | $0.15/M input | **Recommended** - Latest, best value |
| gemini-2.0-flash | Very Fast | $0.10/M input | Good alternative |
| gemini-1.5-flash | Fast | ~$0.075/M input | Legacy, being phased out |

## 📁 Project Structure

```
procrastination-notifier/
├── focus_warden.py     # Main application
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker configuration
├── docker-compose.yml  # Docker Compose setup
└── README.md           # This file
```

## 🔒 Privacy

- Screenshots are processed in real-time and **not stored**
- Images are sent directly to Google's Gemini API
- No data is saved locally (except the activity log in memory)

## 🐛 Troubleshooting

### "Screenshot failed" on Linux
Install `scrot`:
```bash
sudo apt install scrot
```

### GUI doesn't appear in Docker
Make sure X11 forwarding is set up:
```bash
xhost +local:docker
```

### Rate limiting (429 errors)
You've exceeded the free tier limits. Wait a minute or increase your check interval.

## 📄 License

MIT License - Feel free to modify and share!

---

Made with ☕ and a desire to actually finish my projects
