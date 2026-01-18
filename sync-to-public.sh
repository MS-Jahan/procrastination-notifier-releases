#!/bin/bash
# Sync private repo to public repo for release

set -e

PRIVATE_REPO="/mnt/DABCEB02BCEAD851/Projects/procrastination-notifier"
PUBLIC_REPO="/mnt/DABCEB02BCEAD851/Projects/procrastination-notifier-releases"

echo "🔄 Syncing private repo to public repo..."

# Check if public repo exists
if [ ! -d "$PUBLIC_REPO" ]; then
    echo "❌ Public repo not found at $PUBLIC_REPO"
    echo "📥 Clone it first: git clone https://github.com/MS-Jahan/procrastination-notifier-releases.git"
    exit 1
fi

# Copy files
echo "📂 Copying files..."
rsync -av --exclude='.git' \
          --exclude='venv' \
          --exclude='__pycache__' \
          --exclude='*.pyc' \
          --exclude='focus_warden_config.json' \
          --exclude='focus_warden_history.json' \
          --exclude='*.log' \
          --exclude='.serena' \
          --exclude='build' \
          --exclude='dist' \
          "$PRIVATE_REPO/" "$PUBLIC_REPO/"

echo "✅ Sync complete!"
echo ""
echo "Next steps:"
echo "1. cd $PUBLIC_REPO"
echo "2. git add ."
echo "3. git commit -m 'Update for release'"
echo "4. git tag v1.0.0"
echo "5. git push origin main --tags"
