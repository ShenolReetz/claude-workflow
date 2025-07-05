# Claude Workflow - Automated Video Content Creation Pipeline 🚀

**Version 1.0 - Stable Release (July 2, 2025)**

An automated content creation pipeline that generates YouTube-style "Top 5" product videos with affiliate monetization using AI and web scraping.

## 🎯 Project Overview

This system automatically:
- Reads topic ideas from Airtable (e.g., "Top 5 Gaming Laptops 2025")
- Generates SEO-optimized content using Claude AI
- Creates product countdown scripts with viral titles
- Fetches Amazon affiliate links for monetization
- Produces videos using JSON2Video API
- Uploads to Google Drive with organized folder structure
- Creates WordPress blog posts with affiliate links
- Uploads videos to YouTube with metadata
- Updates Airtable with all URLs and status tracking

## ✅ Current Status (v1.0 - July 2, 2025)

### ✨ Working Features
- ✅ **Content Generation** - SEO keywords, viral titles, product descriptions
- ✅ **Amazon Affiliate Integration** - Product search and link generation
- ✅ **Video Creation** - JSON2Video API integration (8-second test videos)
- ✅ **Google Drive Integration** - Automatic folder creation and video upload
- ✅ **WordPress Integration** - Automated blog post creation
- ✅ **YouTube Integration** - Automatic video upload with metadata
- ✅ **Airtable Sync** - Full workflow tracking and status management

### 🔧 Recent Fixes in v1.0
- Fixed YouTube variable references and authentication
- Fixed Airtable field updates (added YouTubeURL field)
- Fixed Google Drive special character handling
- Removed duplicate YouTube upload sections
- Fixed all syntax errors and cleaned up code
- Workflow runs error-free from start to finish

## 🏗 Architecture

Built using MCP (Model Context Protocol) microservices:
- **Content Generation MCP** - SEO keywords, titles, descriptions
- **Amazon Affiliate MCP** - Product search and affiliate link generation
- **JSON2Video MCP** - Video creation and rendering
- **Google Drive MCP** - Storage and organization
- **YouTube MCP** - Video upload and metadata
- **WordPress MCP** - Blog post publishing
- **Airtable MCP** - Workflow management

## 📋 Prerequisites

- Ubuntu server with Python 3.12+
- API keys for all services
- Airtable base with proper schema
- Google OAuth credentials
- WordPress with REST API

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/ShenolReetz/claude-workflow.git
cd claude-workflow

# Install dependencies
pip install --break-system-packages httpx beautifulsoup4 lxml anthropic openai google-api-python-client

# Configure API keys
cp config/api_keys.example.json config/api_keys.json
nano config/api_keys.json

# Run the workflow
cd src
python3 workflow_runner.py
📊 Sample Results

YouTube Videos: Successfully uploading as private shorts
WordPress Posts: Auto-published with affiliate links
Processing Time: ~2 minutes per video
Success Rate: 100% workflow completion

🚀 What's Next

 Production mode (50-second full videos)
 Voice narration (ElevenLabs)
 Product images (DALL-E)
 Instagram Reels
 TikTok integration
 Batch processing
 Scheduled automation
 ### High Priority
- [x] **WordPress Installation** - ✅ Completed
- [ ] **WordPress Integration** - Connect WordPress MCP to workflow
- [ ] **JSON2Video Template Integration** - Implement new countdown video template with Amazon reviews
  - [ ] Update Amazon MCP to scrape review data
  - [ ] Add review count/rating fields to Airtable
  - [ ] Integrate new template with workflow_runner.py
  - [ ] Test with production data
  - See: [JSON2Video Template Documentation](docs/JSON2Video_Template_Update.md)

📝 License
MIT License - See LICENSE file for details

Status: ✅ Stable and Working
Version: 1.0
Last Updated: July 2, 2025
