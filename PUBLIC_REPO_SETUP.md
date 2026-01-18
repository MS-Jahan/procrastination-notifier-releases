# Setting Up Public Repo Build System

## Steps to Complete Setup:

### 1. Clone the Public Repo

```bash
cd /path/to/your/projects
git clone https://github.com/MS-Jahan/procrastination-notifier-releases.git
cd procrastination-notifier-releases
```

### 2. Copy Files from Private Repo

```bash
# Copy all source files
cp -r /mnt/DABCEB02BCEAD851/Projects/procrastination-notifier/* .

# Remove private config files
rm -f focus_warden_config.json focus_warden_history.json *.log
```

### 3. The workflow file should already be in `.github/workflows/build-release-cxfreeze.yml`

If not, I'll create it separately.

### 4. Commit and Push

```bash
git add .
git commit -m "feat: Initial release setup with cx_Freeze build system"
git push origin main
```

### 5. Create Release

```bash
git tag v1.0.0
git push origin v1.0.0
```

This will trigger the build in the **public repo** (FREE unlimited builds!)

## Expected Build Times with cx_Freeze:

- Windows: 5-10 minutes ✅
- macOS: 5-10 minutes ✅
- Linux: 5-10 minutes ✅

**Total: ~30 minutes** (vs 3+ hours with Nuitka!)

## Ongoing Workflow:

When you want to release:
1. Work in private repo as usual
2. When ready: Copy files to public repo
3. Tag and push public repo
4. Builds happen (free!)
5. Users download from public repo

---

Want me to create a script to automate the sync from private → public repo?
