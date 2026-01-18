# How to Create a Release

This guide explains how to create a new release of Focus Warden that will automatically build executables for Windows, macOS, and Linux.

## Prerequisites

- Make sure all changes are committed and pushed to the `main` branch
- Ensure the code is working and tested
- Update the version number in relevant files if needed

## Creating a Release

### Method 1: Using Git Tags (Recommended)

1. **Create and push a version tag:**

```bash
# Create a tag (e.g., v1.0.0, v1.2.3)
git tag v1.0.0

# Push the tag to GitHub
git push origin v1.0.0
```

2. **Automated build starts:**
   - GitHub Actions automatically triggers the build workflow
   - Builds executables for Windows, macOS, and Linux in parallel
   - This takes about 10-15 minutes

3. **Release is created automatically:**
   - Go to: https://github.com/YOUR_USERNAME/procrastination-notifier/releases
   - You'll see the new release with downloadable files attached

### Method 2: Manual Trigger from GitHub

1. **Go to Actions tab:**
   - Visit: https://github.com/YOUR_USERNAME/procrastination-notifier/actions

2. **Run workflow:**
   - Click "Build and Release" workflow
   - Click "Run workflow" button
   - Select branch (usually `main`)
   - Click green "Run workflow" button

3. **Create GitHub Release manually:**
   - After build completes, go to Releases
   - Click "Draft a new release"
   - Create a tag (e.g., v1.0.0)
   - Upload the artifacts from the workflow run

## Version Numbering

Use [Semantic Versioning](https://semver.org/):

- **v1.0.0**: Major release (breaking changes)
- **v1.1.0**: Minor release (new features, backwards compatible)
- **v1.0.1**: Patch release (bug fixes)

## What Happens During Build

The GitHub Actions workflow:

1. ✅ Checks out code
2. ✅ Sets up Python 3.11
3. ✅ Installs dependencies + Nuitka
4. ✅ Builds executables on 3 platforms simultaneously:
   - **Windows**: `FocusWarden-Windows.exe` (single file)
   - **macOS**: `FocusWarden-macOS.app` (app bundle)
   - **Linux**: `FocusWarden-Linux` (binary)
5. ✅ Packages with README and setup guides
6. ✅ Creates GitHub Release
7. ✅ Uploads all files to the release

## Download URLs

Once released, users can download from:

**Latest release:**
```
https://github.com/YOUR_USERNAME/procrastination-notifier/releases/latest
```

**Direct download links** (always points to latest):
```
Windows:
https://github.com/YOUR_USERNAME/procrastination-notifier/releases/latest/download/FocusWarden-Windows-vX.X.X.zip

macOS:
https://github.com/YOUR_USERNAME/procrastination-notifier/releases/latest/download/FocusWarden-macOS-vX.X.X.zip

Linux:
https://github.com/YOUR_USERNAME/procrastination-notifier/releases/latest/download/FocusWarden-Linux-vX.X.X.tar.gz
```

## Releases on Private Repos

**Important:** GitHub Releases are **publicly accessible** even on private repositories!

This means:
- ✅ Your source code stays private
- ✅ Users can download executables from release page
- ✅ Users can see release notes and version history
- ❌ Users CANNOT see your source code
- ❌ Users CANNOT clone the repository

Perfect for distributing commercial software while keeping code private!

## Troubleshooting

### Build fails on macOS

If you see icon-related errors, the workflow will continue without icons. To add icons:

1. Create icon files in `assets/` directory:
   - `icon.png` (512x512 for Linux)
   - `icon.ico` (Windows multi-resolution)
   - `icon.icns` (macOS, create with iconutil)

2. Commit and push

3. Create new tag

### Build fails on Windows

- Check that all file paths use forward slashes `/` not backslashes `\`
- Verify `requirements.txt` has Windows-compatible packages

### Build takes too long

- Normal: 10-15 minutes for all 3 platforms
- Slow: 20+ minutes may indicate caching issues
- Check GitHub Actions logs for detailed timing

### Release not appearing

1. Verify tag was pushed: `git tag -l`
2. Check Actions tab for workflow status
3. Ensure tag starts with `v` (e.g., `v1.0.0`)

## Editing Release Notes

After automatic release creation:

1. Go to Releases page
2. Click "Edit" on the release
3. Modify the description
4. Add changelog details
5. Click "Update release"

## Deleting a Release

```bash
# Delete tag locally
git tag -d v1.0.0

# Delete tag from GitHub
git push origin :refs/tags/v1.0.0

# Then delete the release from GitHub UI
```

## Next Steps

After creating a release:

1. ✅ Test downloads on different platforms
2. ✅ Verify executables work correctly
3. ✅ Share download links with users
4. ✅ Update README with latest version number
5. ✅ Announce on social media / forums
