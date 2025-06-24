# Claude Workflow Automation System

An automated content creation pipeline that generates YouTube-style "Top 5" product videos with affiliate monetization using AI and web scraping.

## 🎥 What It Does

This system automatically:
1. Reads topic ideas from Airtable (e.g., "Top 5 Gaming Laptops 2025")
2. Generates SEO-optimized content using Claude AI
3. Creates product countdown scripts
4. Fetches Amazon affiliate links
5. Produces videos using JSON2Video API
6. Uploads to Google Drive with organized folder structure
7. Updates Airtable with video URLs

## 🏗️ Architecture

Built using MCP (Model Context Protocol) microservices:
- **Content Generation MCP** - SEO keywords, titles, descriptions
- **Amazon Affiliate MCP** - Product links and monetization
- **JSON2Video MCP** - Video creation and rendering
- **Google Drive MCP** - Storage and organization
- **Airtable MCP** - Workflow management

## 🚀 Quick Start

### Prerequisites
- Ubuntu server with Python 3.12+
- API keys for all services (see Configuration)

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/claude-workflow.git
cd claude-workflow

# Copy example configs
cp config/api_keys.example.json config/api_keys.json
cp config/google_drive_credentials.example.json config/google_drive_credentials.json

# Edit configs with your actual API keys
nano config/api_keys.json

# Install dependencies
pip install --break-system-packages httpx beautifulsoup4 lxml anthropic openai google-api-python-client

# Run the workflow
python3 src/workflow_runner.py

## 🆕 Text Generation Control MCP

The latest addition to the system is the **Text Generation Control MCP**, which ensures all generated content meets strict timing requirements for text-to-speech conversion.

### Features:
- **9-Second Timing Validation**: Each product description is validated to ensure it can be read in exactly 9 seconds
- **Automatic Regeneration**: Products that don't meet timing requirements are automatically regenerated
- **Keyword Enforcement**: Ensures SEO keywords are properly integrated into product descriptions
- **Category Validation**: Verifies products match their assigned categories

### Implementation Files:
- `mcp_servers/text_generation_control_server.py` - Quality control server
- `src/mcp/text_generation_control_agent_mcp_v2.py` - Control agent with regeneration loop

### Workflow Integration:
The Text Control MCP runs after countdown script generation to ensure all products meet quality standards before proceeding to video creation.

## 📊 Project Status Update (June 24, 2025)

### ✅ Achievements Today

1. **Fixed Google Drive Upload Issue**
   - Resolved parameter ordering issue in `upload_video_to_google_drive` function
   - Videos now successfully upload to Google Drive with proper folder structure
   - Each video gets organized in: `N8N Projects/[Video Title]/Video/`

2. **Airtable Integration Improvements**
   - Added support for `TextControlStatus` field for quality control tracking
   - Added `ProductNo1-5AffiliateLink` fields for Amazon affiliate links
   - Integrated `FinalVideo` field to store Google Drive URLs
   - Added `JSON2VideoProjectID` and `GenerationAttempts` tracking

3. **Workflow Enhancements**
   - Complete end-to-end automation working: Airtable → AI Content → Video → Google Drive
   - Status properly updates to "Done" after successful completion
   - Better error handling and logging throughout the pipeline

### 🚀 Current Workflow Status

The automated pipeline now successfully:
- ✅ Reads topics from Airtable
- ✅ Generates SEO keywords and optimized titles using Claude AI
- ✅ Creates product countdown scripts with quality control
- ✅ Attempts Amazon affiliate link generation (currently rate-limited)
- ✅ Produces videos via JSON2Video API
- ✅ Uploads videos to organized Google Drive folders
- ✅ Updates Airtable with video URLs and completion status

### 🐛 Known Issues
- Amazon affiliate link generation faces 503 rate limiting (needs proxy/delay adjustment)
- Some Airtable field updates show warnings but don't affect functionality

### 📈 Success Rate
- Video Generation: 100% success
- Google Drive Upload: 100% success (after fixes)
- Amazon Links: 20% success (due to rate limiting)
