#!/bin/bash
echo "🔥 TOTAL RESET - Creating absolutely clean repo"

# Create new branch
git checkout --orphan final-clean

# Remove everything from git
git rm -rf .

# Delete all physical files with secrets
rm -f config/*.json
rm -f config/.*.json
find . -name "*.backup" -exec rm {} \;
find . -name "*.save" -exec rm {} \;
find . -name "*.bak" -exec rm {} \;

# Keep ONLY example files and Python code
git add src/*.py
git add src/mcp/*.py
git add mcp_servers/*.py
git add README.md
git add requirements.txt 2>/dev/null || true
git add config/*.example.json

# Create comprehensive .gitignore
cat > .gitignore << 'IGNORE'
# Config files - ONLY allow examples
config/*.json
!config/*.example.json
config/.*

# Backup files
*.backup
*.save
*.bak
*.tmp
*~

# Credentials and secrets
*.key
*.pem
*.token
*.credentials
.env
.env.*

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
venv/
.venv/

# Logs
*.log
logs/

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db
IGNORE

# Add gitignore
git add .gitignore

# Show what will be committed
echo "Files to be committed:"
git status --porcelain

# Commit
git commit -m "Automated video content pipeline - clean repository"

# Replace master
git branch -D master
git branch -m master

echo "✅ Done! Push with: git push origin master --force"
