# Setup Guide - Working on Another PC

Complete guide to set up this agent-based video workflow system on a new computer.

---

## Prerequisites

### 1. Install Required Software

#### Git (Version Control)
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install git

# macOS
brew install git

# Windows
# Download from: https://git-scm.com/download/win
```

#### Python 3.11+ (Required)
```bash
# Ubuntu/Debian
sudo apt install python3.11 python3.11-venv python3-pip

# macOS
brew install python@3.11

# Windows
# Download from: https://www.python.org/downloads/
# Make sure to check "Add Python to PATH" during installation
```

#### Node.js 18+ (For Remotion video generation)
```bash
# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# macOS
brew install node@18

# Windows
# Download from: https://nodejs.org/en/download/
```

#### Claude Code CLI (Optional but recommended)
```bash
# Install Claude Code
npm install -g @anthropic-ai/claude-code

# Or follow: https://docs.claude.com/en/docs/claude-code
```

---

## Step-by-Step Setup

### Step 1: Clone the Repository

```bash
# Navigate to where you want the project
cd ~/Documents  # or any folder you prefer

# Clone from GitHub
git clone https://github.com/ShenolReetz/claude-workflow.git

# Enter the project directory
cd claude-workflow

# Verify you have all files
ls -la
```

**Expected output**: You should see folders like:
- `agents/`
- `mcp_servers/`
- `src/`
- `config/`
- `tests/`

---

### Step 2: Set Up Python Environment

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# Your prompt should now show (venv)
```

#### Install Python Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install all required packages
pip install \
    aiohttp \
    asyncio \
    openai \
    anthropic \
    elevenlabs \
    airtable-python-wrapper \
    python-dotenv \
    pillow \
    requests \
    huggingface_hub \
    google-auth \
    google-auth-oauthlib \
    google-auth-httplib2 \
    google-api-python-client \
    wordpress-xmlrpc \
    instagrapi \
    redis
```

**Or** if there's a `requirements.txt` (we should create one):
```bash
pip install -r requirements.txt
```

---

### Step 3: Configure API Keys

#### 3.1 Copy Example Config

```bash
# Navigate to config folder
cd config

# Check if example exists
ls -la

# If api_keys.example.json exists:
cp api_keys.example.json api_keys.json

# If not, create api_keys.json from scratch
```

#### 3.2 Fill in Your API Keys

Edit `config/api_keys.json` with your actual API keys:

```json
{
  "openai_api_key": "sk-proj-YOUR_OPENAI_KEY_HERE",
  "huggingface": "hf_YOUR_HUGGINGFACE_TOKEN_HERE",
  "hf_api_token": "hf_YOUR_HUGGINGFACE_TOKEN_HERE",
  "hf_image_model": "black-forest-labs/FLUX.1-schnell",
  "hf_text_model": "Qwen/Qwen2.5-72B-Instruct",
  "hf_use_inference_api": true,

  "elevenlabs_api_key": "YOUR_ELEVENLABS_KEY_HERE",
  "scrapingdog_api_key": "YOUR_SCRAPINGDOG_KEY_HERE",

  "airtable_api_key": "YOUR_AIRTABLE_KEY_HERE",
  "airtable_base_id": "appXXXXXXXXXXXXXX",
  "airtable_table_name": "Video Titles",

  "fal_key": "YOUR_FAL_AI_KEY_HERE",

  "youtube_client_secrets_file": "config/youtube_client_secret.json",
  "youtube_token_file": "config/youtube_token.json",

  "wordpress_url": "https://yoursite.com",
  "wordpress_user": "your_username",
  "wordpress_password": "your_app_password",

  "instagram_session_file": "config/instagram_session.json"
}
```

#### 3.3 Where to Get API Keys

| Service | How to Get Key | Cost |
|---------|----------------|------|
| **OpenAI** | https://platform.openai.com/api-keys | Pay-per-use (fallback only) |
| **HuggingFace** | https://huggingface.co/settings/tokens | FREE (Inference API) |
| **ElevenLabs** | https://elevenlabs.io/app/settings/api-keys | $5/month starter |
| **ScrapingDog** | https://www.scrapingdog.com/dashboard | $20/month (1000 requests) |
| **Airtable** | https://airtable.com/create/tokens | FREE tier available |
| **fal.ai** | https://fal.ai/dashboard/keys | Pay-per-use (backup only) |

#### 3.4 Set Up YouTube Authentication

```bash
# Download OAuth credentials from Google Cloud Console
# 1. Go to: https://console.cloud.google.com/apis/credentials
# 2. Create OAuth 2.0 Client ID (Desktop app)
# 3. Download JSON file
# 4. Save as: config/youtube_client_secret.json

# First time authentication will open browser
# Token will be saved to config/youtube_token.json
```

#### 3.5 Set Up WordPress

```bash
# WordPress requires application password
# 1. Go to: https://yoursite.com/wp-admin/profile.php
# 2. Scroll to "Application Passwords"
# 3. Create new application password
# 4. Copy to config/api_keys.json
```

#### 3.6 Set Up Instagram (Optional)

Instagram requires session authentication - will be handled during first run.

---

### Step 4: Install Remotion Dependencies

```bash
# Navigate to remotion folder
cd remotion-video-generator

# Install Node.js dependencies
npm install

# This installs:
# - @remotion/cli
# - @remotion/lambda
# - react
# - react-dom
# - And other video rendering dependencies

# Go back to project root
cd ..
```

---

### Step 5: Create Required Directories

```bash
# Create directories for local storage
mkdir -p local_storage
mkdir -p logs
mkdir -p config/token_backups

# Set permissions
chmod 755 local_storage
chmod 755 logs
chmod 700 config  # Keep config private
```

---

### Step 6: Set Up MCP Servers (If Using Claude Code)

```bash
# Add MCP servers to Claude Code
claude mcp add production-amazon-scraper python3 /full/path/to/claude-workflow/mcp_servers/production_amazon_scraper_mcp_server.py

claude mcp add production-remotion-wow-video python3 /full/path/to/claude-workflow/mcp_servers/production_remotion_wow_video_mcp_server.py

claude mcp add production-content-generation python3 /full/path/to/claude-workflow/mcp_servers/production_content_generation_mcp_server.py

claude mcp add production-voice-generation python3 /full/path/to/claude-workflow/mcp_servers/production_voice_generation_mcp_server.py

claude mcp add production-quality-assurance python3 /full/path/to/claude-workflow/mcp_servers/production_quality_assurance_mcp_server.py

claude mcp add production-analytics python3 /full/path/to/claude-workflow/mcp_servers/production_analytics_mcp_server.py

# Verify MCP servers
claude mcp list
```

---

### Step 7: Test the Setup

#### 7.1 Test Python Environment

```bash
# Make sure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Test Python imports
python3 -c "import aiohttp, openai, elevenlabs; print('✅ Python dependencies OK')"
```

#### 7.2 Test Configuration

```bash
# Run configuration validator
python3 -c "
import json
with open('config/api_keys.json') as f:
    config = json.load(f)
    print('✅ API keys loaded')
    print(f'   - OpenAI: {\"Present\" if config.get(\"openai_api_key\") else \"Missing\"}')
    print(f'   - HuggingFace: {\"Present\" if config.get(\"huggingface\") else \"Missing\"}')
    print(f'   - ElevenLabs: {\"Present\" if config.get(\"elevenlabs_api_key\") else \"Missing\"}')
    print(f'   - Airtable: {\"Present\" if config.get(\"airtable_api_key\") else \"Missing\"}')
"
```

#### 7.3 Run Agent System Test

```bash
# Run the test workflow
python3 run_agent_workflow.py --test

# Expected output:
# ✅ TEST WORKFLOW PASSED - System is ready!
```

---

## Common Issues & Solutions

### Issue 1: Python Version Mismatch

**Error**: `Python 3.11 required, found 3.9`

**Solution**:
```bash
# Ubuntu - Install Python 3.11
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.11 python3.11-venv

# Recreate virtual environment
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

### Issue 2: Permission Denied on MCP Servers

**Error**: `Permission denied: production_amazon_scraper_mcp_server.py`

**Solution**:
```bash
# Make MCP servers executable
chmod +x mcp_servers/*.py

# Also ensure they have Python shebang
head -1 mcp_servers/production_amazon_scraper_mcp_server.py
# Should show: #!/usr/bin/env python3
```

---

### Issue 3: Missing config/api_keys.json

**Error**: `FileNotFoundError: config/api_keys.json`

**Solution**:
```bash
# Create from template
cat > config/api_keys.json << 'EOF'
{
  "openai_api_key": "REPLACE_WITH_YOUR_KEY",
  "huggingface": "REPLACE_WITH_YOUR_TOKEN",
  "hf_api_token": "REPLACE_WITH_YOUR_TOKEN",
  "elevenlabs_api_key": "REPLACE_WITH_YOUR_KEY",
  "scrapingdog_api_key": "REPLACE_WITH_YOUR_KEY",
  "airtable_api_key": "REPLACE_WITH_YOUR_KEY",
  "airtable_base_id": "REPLACE_WITH_YOUR_BASE_ID",
  "fal_key": "REPLACE_WITH_YOUR_KEY",
  "wordpress_url": "https://yoursite.com",
  "wordpress_user": "your_username",
  "wordpress_password": "your_password"
}
EOF

# Then edit with your actual keys
nano config/api_keys.json  # or use any text editor
```

---

### Issue 4: Remotion npm install fails

**Error**: `Cannot find module '@remotion/cli'`

**Solution**:
```bash
# Navigate to remotion folder
cd remotion-video-generator

# Clear npm cache
npm cache clean --force

# Delete node_modules and package-lock.json
rm -rf node_modules package-lock.json

# Reinstall
npm install

# If still fails, update Node.js
node --version  # Should be 18+
npm install -g npm@latest
```

---

### Issue 5: Git clone fails (private repo)

**Error**: `Repository not found`

**Solution**:
```bash
# If repo is private, you need GitHub authentication

# Option 1: Use personal access token
git clone https://YOUR_GITHUB_TOKEN@github.com/ShenolReetz/claude-workflow.git

# Option 2: Use SSH (recommended)
# 1. Generate SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# 2. Add to GitHub
cat ~/.ssh/id_ed25519.pub
# Copy output and add to: https://github.com/settings/keys

# 3. Clone with SSH
git clone git@github.com:ShenolReetz/claude-workflow.git
```

---

## Quick Start Checklist

Use this checklist when setting up on a new PC:

```
[ ] Install Git
[ ] Install Python 3.11+
[ ] Install Node.js 18+
[ ] Clone repository
[ ] Create virtual environment
[ ] Install Python dependencies
[ ] Create config/api_keys.json
[ ] Fill in all API keys
[ ] Set up YouTube OAuth (if publishing to YouTube)
[ ] Install Remotion dependencies (npm install)
[ ] Create local_storage and logs directories
[ ] Make MCP servers executable (chmod +x)
[ ] Run test: python3 run_agent_workflow.py --test
[ ] Verify output: "✅ TEST WORKFLOW PASSED"
```

---

## Syncing Changes Between PCs

### On PC #1 (Making changes):

```bash
# After making changes
git add .
git commit -m "Your commit message"
git push origin master
```

### On PC #2 (Getting updates):

```bash
# Pull latest changes
git pull origin master

# If you have local changes you want to keep:
git stash  # Save your local changes
git pull origin master  # Get updates
git stash pop  # Restore your local changes
```

### Best Practice - Work on Branches:

```bash
# On PC #1
git checkout -b feature/my-new-feature
# Make changes
git commit -am "Add new feature"
git push origin feature/my-new-feature

# On PC #2
git fetch origin
git checkout feature/my-new-feature
# Continue working
```

---

## File/Folder Exclusions (.gitignore)

These files are **NOT** synced via Git (they're in .gitignore):

```
❌ NOT synced:
- config/api_keys.json (your API keys)
- config/*.token (authentication tokens)
- config/token_backups/ (token backups)
- local_storage/ (generated videos/images)
- logs/ (log files)
- venv/ (Python virtual environment)
- remotion-video-generator/node_modules/ (Node dependencies)
- __pycache__/ (Python cache)

✅ SYNCED:
- All Python code (agents/, src/, mcp_servers/)
- Remotion source code (remotion-video-generator/src/)
- Documentation (.md files)
- Tests (tests/)
- Scripts (run_*.py)
```

**Important**: You need to set up `config/api_keys.json` separately on each PC!

---

## Backup Your Config (Optional)

If you want to keep your API keys synced privately:

### Option 1: Private Gist (Recommended)

```bash
# Create private gist at: https://gist.github.com/
# Upload config/api_keys.json
# Keep gist URL private

# On new PC, download:
curl -o config/api_keys.json https://gist.githubusercontent.com/YOUR_USERNAME/GIST_ID/raw/api_keys.json
```

### Option 2: Encrypted USB Drive

```bash
# Copy config folder to encrypted USB
cp -r config /media/usb-drive/claude-workflow-config

# On new PC
cp -r /media/usb-drive/claude-workflow-config/* config/
```

### Option 3: Password Manager (1Password, LastPass, etc.)

Store `config/api_keys.json` content as a secure note in your password manager.

---

## Advanced: Docker Setup (Optional)

If you want consistent environment across all PCs:

```dockerfile
# Dockerfile (to be created)
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    git \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python3", "run_agent_workflow.py", "--test"]
```

Then on any PC:
```bash
docker build -t claude-workflow .
docker run -v ./config:/app/config claude-workflow
```

---

## Summary

### Minimum Setup Time: ~30 minutes

1. **5 min** - Install prerequisites (Git, Python, Node)
2. **2 min** - Clone repository
3. **5 min** - Set up Python environment
4. **10 min** - Configure API keys
5. **5 min** - Install Remotion dependencies
6. **3 min** - Test the system

### You're Ready When:

✅ `python3 run_agent_workflow.py --test` shows:
```
✅ TEST WORKFLOW PASSED - System is ready!
```

---

## Need Help?

- **Documentation**: Check other .md files in project root
- **GitHub Issues**: https://github.com/ShenolReetz/claude-workflow/issues
- **Claude Code Docs**: https://docs.claude.com/en/docs/claude-code

---

**Happy coding on your new PC!** 🚀
