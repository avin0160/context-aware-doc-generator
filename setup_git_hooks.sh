#!/bin/bash

# Git hooks setup for automatic GitHub updates
# This script sets up git hooks to automatically push changes

HOOK_DIR=".git/hooks"
PRE_COMMIT_HOOK="$HOOK_DIR/pre-commit"
POST_COMMIT_HOOK="$HOOK_DIR/post-commit"

echo "🔧 Setting up Git hooks for automatic GitHub updates..."

# Create pre-commit hook
cat > "$PRE_COMMIT_HOOK" << 'EOF'
#!/bin/bash
# Pre-commit hook: Run basic checks before commit

echo "🔍 Running pre-commit checks..."

# Check for large files (> 50MB)
large_files=$(find . -type f -size +50M -not -path "./.git/*" 2>/dev/null)
if [ ! -z "$large_files" ]; then
    echo "⚠️  Warning: Large files detected:"
    echo "$large_files"
    echo "Consider using Git LFS for large files"
fi

# Check for common sensitive files
sensitive_patterns=("*.key" "*.pem" "*.p12" "*password*" "*secret*" ".env")
for pattern in "${sensitive_patterns[@]}"; do
    if git diff --cached --name-only | grep -i "$pattern" > /dev/null 2>&1; then
        echo "🚨 Warning: Potentially sensitive file detected matching '$pattern'"
        echo "Please review before committing"
    fi
done

echo "✅ Pre-commit checks completed"
EOF

# Create post-commit hook for auto-push (optional)
cat > "$POST_COMMIT_HOOK" << 'EOF'
#!/bin/bash
# Post-commit hook: Automatically push to GitHub after commit

# Only auto-push if AUTO_PUSH environment variable is set
if [ "$AUTO_PUSH" = "true" ]; then
    echo "🚀 Auto-pushing to GitHub..."
    git push origin main
    if [ $? -eq 0 ]; then
        echo "✅ Successfully pushed to GitHub"
    else
        echo "❌ Failed to push to GitHub"
    fi
fi
EOF

# Make hooks executable
chmod +x "$PRE_COMMIT_HOOK"
chmod +x "$POST_COMMIT_HOOK"

echo "✅ Git hooks setup completed!"
echo ""
echo "📋 Available update methods:"
echo "1. Manual: ./update_github.sh 'Your commit message'"
echo "2. Quick: git add . && git commit -m 'message' && git push origin main"
echo "3. Auto-push: export AUTO_PUSH=true (then normal git commit will auto-push)"
echo ""
echo "🔧 Hooks installed in .git/hooks/"