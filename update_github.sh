#!/bin/bash

# Auto-update GitHub repository script
# Usage: ./update_github.sh "Your commit message"

set -e  # Exit on any error

echo "🔄 Updating GitHub repository..."

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

# Check if commit message is provided
if [ -z "$1" ]; then
    echo "📝 No commit message provided, using default..."
    COMMIT_MSG="Update project files - $(date '+%Y-%m-%d %H:%M:%S')"
else
    COMMIT_MSG="$1"
fi

echo "📁 Adding all changes to git..."
git add .

# Check if there are any changes to commit
if git diff --staged --quiet; then
    echo "ℹ️  No changes to commit"
    exit 0
fi

echo "💾 Committing changes..."
git commit -m "$COMMIT_MSG"

echo "🚀 Pushing to GitHub..."
git push origin main

echo "✅ Successfully updated GitHub repository!"
echo "📊 Latest commit: $COMMIT_MSG"

# Show the remote repository URL
REPO_URL=$(git config --get remote.origin.url)
echo "🔗 Repository: $REPO_URL"