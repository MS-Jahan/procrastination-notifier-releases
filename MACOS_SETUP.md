# macOS Setup Guide

Focus Warden requires Screen Recording permission on macOS to capture screenshots for AI analysis.

## First Launch

When you first run Focus Warden on macOS, you'll see this message in the Activity Log:

```
⚠️ macOS Screen Recording permission required!
📋 Go to: System Settings > Privacy & Security > Screen Recording
📋 Enable permission for Focus Warden, then restart the app
```

## Granting Permission

### macOS Ventura (13.0+) and Sonoma (14.0+):

1. Open **System Settings**
2. Navigate to **Privacy & Security**
3. Click **Screen Recording** in the left sidebar
4. Toggle **ON** for Focus Warden
5. **Restart** Focus Warden

### macOS Monterey (12.0) and earlier:

1. Open **System Preferences**
2. Click **Security & Privacy**
3. Select **Privacy** tab
4. Click **Screen Recording** in the left sidebar
5. Check the box next to **Focus Warden**
6. **Restart** Focus Warden

## Running Unsigned Apps

Since Focus Warden is not code-signed, macOS Gatekeeper will block it on first launch.

### To bypass Gatekeeper:

**Method 1: Right-click to Open**
1. Right-click (or Control-click) the Focus Warden app
2. Select **Open** from the menu
3. Click **Open** in the dialog that appears

**Method 2: System Settings**
1. Try to open Focus Warden normally (it will be blocked)
2. Open **System Settings** > **Privacy & Security**
3. Scroll down to find "Focus Warden was blocked..."
4. Click **Open Anyway**
5. Confirm by clicking **Open**

You only need to do this once. After the first launch, macOS will remember your choice.

## Notifications

Focus Warden uses macOS native notifications via `osascript`. These should work without additional permissions.

If you don't see notifications:
1. Open **System Settings** > **Notifications**
2. Find **Script Editor** or **Focus Warden** in the list
3. Ensure notifications are enabled

## Troubleshooting

### "App is damaged and can't be opened"

This happens because the app is not notarized by Apple.

**Solution:**
```bash
# Remove the quarantine attribute
xattr -cr /path/to/FocusWarden.app
```

Then try opening again using Method 1 above.

### Screenshot permission not working

1. Make sure you've granted Screen Recording permission
2. **Restart** Focus Warden after granting permission
3. Check Console.app for any error messages
4. Try running from Terminal to see detailed error output

## Need Help?

Report issues at: https://github.com/yourusername/procrastination-notifier/issues
