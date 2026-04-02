#!/bin/bash
set -e

echo "=== Git History Cleanup Script ==="
echo "This script removes karma_history.json and karma_plot.png from all git history"
echo "while preserving the current versions of these files."
echo ""
echo "⚠️  WARNING: This rewrites git history!"
echo "After running this, you'll need to force push: git push origin --force --all"
echo ""
read -p "Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

echo ""
echo "Step 1: Saving current versions of files..."
cp data/karma_history.json /tmp/karma_history.json
cp images/karma_plot.png /tmp/karma_plot.png
echo "✓ Files saved to /tmp/"

echo ""
echo "Step 2: Removing files from git history..."
echo "This may take a while (processing 765+ commits)..."
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch data/karma_history.json images/karma_plot.png' \
  --prune-empty --tag-name-filter cat -- --branches
echo "✓ Files removed from history"

echo ""
echo "Step 3: Cleaning up git references..."
rm -rf .git/refs/original/
git reflog expire --expire=now --all
git gc --prune=now --aggressive
echo "✓ Git cleanup complete"

echo ""
echo "Step 4: Restoring current versions and committing..."
mkdir -p data images
cp /tmp/karma_history.json data/karma_history.json
cp /tmp/karma_plot.png images/karma_plot.png
git add data/karma_history.json images/karma_plot.png
git commit -m "Add current karma data (history cleaned)"
echo "✓ Current files restored and committed"

echo ""
echo "=== Cleanup Complete! ==="
echo ""
echo "Repository size before and after:"
du -sh .git
echo ""
echo "Next steps:"
echo "  1. Verify the latest commit has your data files"
echo "  2. Push to GitHub: git push origin --force --all"
echo "  3. Push tags (if any): git push origin --force --tags"
echo ""
echo "Note: Anyone else with a clone will need to re-clone or reset their local copy."
