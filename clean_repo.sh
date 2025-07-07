#!/bin/bash
set -e  # Exit on error

echo "🔥 Starting Nuclear Repository Cleanup..."
echo "==========================================="

# Step 1: Create temporary backup of code only (no .git)
echo "📁 Creating clean backup of code..."
mkdir -p ../claude-workflow-clean
rsync -av --exclude='.git' --exclude='config/api_keys.json*' ./ ../claude-workflow-clean/

# Step 2: Create new orphan branch (no history)
echo "🌱 Creating new orphan branch..."
git checkout --orphan clean-main

# Step 3: Remove everything from git tracking
echo "🧹 Removing all files from git..."
git rm -rf . 2>/dev/null || true

# Step 4: Copy back clean files
echo "📥 Copying back clean files..."
cp -r ../claude-workflow-clean/* .
cp ../claude-workflow-clean/.gitignore . 2>/dev/null || true

# Step 5: Create comprehensive .gitignore
echo "📝 Creating comprehensive .gitignore..."
cat > .gitignore << 'GITIGNORE'
# API Keys and sensitive files
config/api_keys.json
config/api_keys.json.*
config/*.key
config/*.pem
config/google_drive_credentials.json
config/*_credentials.json

# Environment files
.env
.env.*

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/

# Logs
*.log
logs/

# OS files
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/

# Temporary files
*.tmp
*.temp
*.swp
*.swo
*~

# Backup files
*.backup
*.bak
GITIGNORE

# Step 6: Create example config files
echo "📄 Creating example configuration files..."
cat > config/api_keys.example.json << 'EXAMPLE'
{
  "anthropic_api_key": "sk-ant-api03-YOUR-KEY-HERE",
  "openai_api_key": "sk-proj-YOUR-KEY-HERE",
  "airtable_api_key": "patYOUR-KEY-HERE",
  "airtable_base_id": "appYOUR-BASE-ID",
  "airtable_table_name": "Video Titles",
  "elevenlabs_api_key": "sk_YOUR-KEY-HERE",
  "json2video_api_key": "YOUR-KEY-HERE",
  "amazon_associate_id": "reviewch3kr0d-20",
  "scrapingdog_api_key": "YOUR-KEY-HERE",
  "google_drive_credentials": "/home/claude-workflow/config/google_drive_credentials.json",
  "youtube_api_key": "YOUR-YOUTUBE-KEY",
  "instagram": {
    "account_id": "YOUR-INSTAGRAM-BUSINESS-ACCOUNT-ID",
    "page_access_token": "YOUR-PAGE-ACCESS-TOKEN"
  }
}
EXAMPLE

cat > config/google_drive_credentials.example.json << 'GDRIVE'
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "your-key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR-KEY-HERE\n-----END PRIVATE KEY-----\n",
  "client_email": "your-service-account@project.iam.gserviceaccount.com",
  "client_id": "your-client-id"
}
GDRIVE

# Step 7: Add all files and commit
echo "💾 Creating fresh commit..."
git add .
git commit -m "Initial commit - Clean repository setup without secrets"

# Step 8: Clean up the old branches
echo "🗑️  Cleaning up old branches..."
git branch -D master 2>/dev/null || true
git branch -m master

# Step 9: Final status
echo ""
echo "✅ Repository cleaned and ready!"
echo "==========================================="
echo "📋 Next steps:"
echo "   1. Run: git push origin master --force"
echo "   2. Restore your API keys: cp ~/api_keys_backup.json config/api_keys.json"
echo "   3. Never commit api_keys.json again!"
echo ""
echo "Your old repository is backed up at: ../claude-workflow-FULL-BACKUP"
