#!/bin/bash
set -euo pipefail

echo "=== Git History Cleanup Script ==="
echo "This script removes karma_history.json and karma_plot.png from all git history"
echo "while preserving the current versions of these files."
echo ""
echo "⚠️  WARNING: This rewrites git history!"
echo "After running this, you'll need to force push: git push origin --force --all"
echo ""

if ! command -v git-filter-repo >/dev/null 2>&1; then
    echo "Error: git-filter-repo is required but not installed."
    echo "  Install: brew install git-filter-repo  (or: pip install git-filter-repo)"
    echo "  See: https://github.com/newren/git-filter-repo"
    exit 1
fi

if [ ! -f data/karma_history.json ] || [ ! -f images/karma_plot.png ]; then
    echo "Error: expected data/karma_history.json and images/karma_plot.png to exist."
    echo "Run this script from the repository root."
    exit 1
fi

read -p "Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

COMMIT_COUNT=$(git rev-list --count HEAD)
ORIGIN_URL=$(git remote get-url origin 2>/dev/null || echo "")

echo ""
echo "Step 1: Saving current versions of files..."
TMPDIR=$(mktemp -d)
cp data/karma_history.json "$TMPDIR/karma_history.json"
cp images/karma_plot.png "$TMPDIR/karma_plot.png"
echo "✓ Files saved to $TMPDIR"

echo ""
echo "Step 2: Removing files from git history..."
echo "Processing $COMMIT_COUNT commits..."
git filter-repo --force \
  --invert-paths \
  --path data/karma_history.json \
  --path images/karma_plot.png
echo "✓ Files removed from history"

echo ""
echo "Step 3: Running garbage collection..."
git reflog expire --expire=now --all
git gc --prune=now --aggressive
echo "✓ Git cleanup complete"

# git filter-repo removes the origin remote as a safety measure; restore it
if [ -n "$ORIGIN_URL" ] && ! git remote get-url origin >/dev/null 2>&1; then
    git remote add origin "$ORIGIN_URL"
    echo "✓ Restored origin remote: $ORIGIN_URL"
fi

echo ""
echo "Step 4: Restoring current versions and committing..."
mkdir -p data images
cp "$TMPDIR/karma_history.json" data/karma_history.json
cp "$TMPDIR/karma_plot.png" images/karma_plot.png
git add data/karma_history.json images/karma_plot.png
git commit -m "Add current karma data (history cleaned)"
echo "✓ Current files restored and committed"

echo ""
echo "=== Cleanup Complete! ==="
echo ""
echo "Repository size after cleanup:"
du -sh .git
echo ""
echo "Next steps:"
echo "  1. Verify the latest commit has your data files"
echo "  2. Push to GitHub: git push origin --force --all"
echo "  3. Push tags (if any): git push origin --force --tags"
echo ""
echo "Note: Anyone else with a clone will need to re-clone or reset their local copy."
