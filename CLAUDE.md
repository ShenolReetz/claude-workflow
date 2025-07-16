# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
This is an automated video content creation pipeline that generates "Top 5" product videos with affiliate monetization. It integrates multiple AI services to create YouTube-style content automatically from Airtable topics.

**Current Status: v2.9 - FULL PRODUCTION MODE ACTIVE**
- ✅ **COMPLETE END-TO-END WORKFLOW** (Golf GPS Units successfully processed)
- ✅ **FULL 60-SECOND VIDEOS** (Intro + 5 Products + Outro)
- ✅ **COMPLETE VOICE NARRATION** (ElevenLabs for all segments)
- ✅ **ALL TIMEOUTS REMOVED** (Uninterrupted workflow execution)
- ✅ **PRODUCTION VIDEO TEMPLATES** (Reviews, ratings, voice integration)
- ✅ **AIRTABLE FIELD MAPPING FIXED** (ProductNo1-5Photo correctly updated)
- ✅ **GOOGLE DRIVE INTEGRATION** (Voice files, images, videos all uploaded)
- ✅ Enhanced video generation with reviews and ratings
- ✅ WordPress integration with product photos and countdown format
- ✅ YouTube Shorts automation (token refresh needed)
- ⏸️ TikTok integration **DISABLED** (API still in review)
- ✅ Instagram Reels integration **ENABLED** (token refresh needed)
- ✅ API credit monitoring with email alerts
- ✅ 90+ keywords per video across 5 platforms
- ✅ ElevenLabs voice generation integration
- ✅ Product category extraction for improved Amazon scraping
- ✅ Flow control and validation system
- ✅ Top-to-bottom title processing with automatic skipping
- ✅ Curated content database (1,095 high-retention titles)
- ✅ Voice field mapping to existing Airtable structure
- ✅ Google Drive image upload errors resolved

## Development Commands

### Running the Workflow
```bash
# Main workflow execution
cd /home/claude-workflow
python3 src/workflow_runner.py

# Run with logging (recommended)
./run_workflow.sh

# Run final workflow with enhanced logging
./run_workflow_final.sh
```

### Testing Components
```bash
# Test individual components
python3 src/test_complete_workflow.py
python3 src/test_minimal_workflow.py
python3 src/test_elevenlabs_api.py
python3 src/test_voice_generation.py
python3 src/test_image_generation.py
python3 src/test_google_drive.py
python3 src/test_wordpress.py
python3 src/test_youtube.py

# Test new v2.6 features
python3 src/test_enhanced_video_generation.py
python3 src/test_enhanced_wordpress.py
python3 src/test_credit_monitoring.py
python3 src/test_tiktok_validation.py
python3 src/test_instagram_validation.py
python3 src/test_voice_workflow_integration.py

# Test specific MCP servers
python3 mcp_servers/test_airtable.py
python3 mcp_servers/test_field_creation.py
python3 mcp_servers/verify_fields.py
```

### Installation
```bash
# Install Python dependencies
pip install --break-system-packages httpx beautifulsoup4 lxml anthropic openai google-api-python-client airtable-python-wrapper python-dotenv requests

# Setup YouTube integration
./setup_youtube.sh
```

## Architecture Overview

### MCP (Model Context Protocol) Microservices
The project uses a microservices architecture with MCP servers:

- **Airtable MCP** (`mcp_servers/airtable_server.py`) - Database operations
- **Content Generation MCP** (`mcp_servers/content_generation_server.py`) - Claude AI content creation
- **Amazon Affiliate MCP** (`mcp_servers/amazon_affiliate_server.py`) - Product search and affiliate links
- **JSON2Video MCP** (`mcp_servers/json2video_server.py`) - Video creation via JSON2Video API
- **JSON2Video Enhanced** (`mcp_servers/json2video_enhanced_server.py`) - 60s videos with reviews/ratings
- **Google Drive MCP** (`mcp_servers/google_drive_server.py`) - Video storage and organization
- **Voice Generation MCP** (`mcp_servers/voice_generation_server.py`) - ElevenLabs voice synthesis
- **Image Generation MCP** (`mcp_servers/image_generation_server.py`) - DALL-E product images
- **Product Category Extractor MCP** (`mcp_servers/product_category_extractor_server.py`) - Marketing title to search term conversion
- **Flow Control MCP** (`mcp_servers/flow_control_server.py`) - Workflow validation and control
- **TikTok MCP** (`mcp_servers/tiktok_server.py`) - TikTok Reels upload (ready for approval)
- **Instagram MCP** (`mcp_servers/instagram_server.py`) - Instagram Reels upload (ready for approval)
- **Credit Monitor MCP** (`mcp_servers/credit_monitor_server.py`) - API credit monitoring with email alerts

### Workflow Orchestrator
Main orchestrator: `src/workflow_runner.py` (class: `ContentPipelineOrchestrator`)

Workflow stages (v2.9):
1. Fetch pending titles from Airtable (top-to-bottom order)
2. Validate title has minimum 5 Amazon products (skip if insufficient)
3. Extract clean product category from marketing title using Claude AI
4. Search Amazon products using extracted category and generate affiliate links
5. Generate multi-platform SEO keywords (90+ keywords across 5 platforms)
6. Generate countdown script with actual product data
7. Run text generation quality control with retry logic
8. Download Amazon product images from scraped data
9. Generate Amazon-guided OpenAI product images
10. Generate voice text for intro, outro, and all products
11. Create voice narration using ElevenLabs (intro, outro, 5 products)
12. Upload voice files to Google Drive
13. Create enhanced video using JSON2Video (with reviews, ratings, voice)
14. Upload video to Google Drive
15. Create WordPress blog post with product photos and countdown format
16. Upload to YouTube Shorts (token refresh needed)
17. Upload to TikTok (DISABLED - API still in review)
18. Upload to Instagram Reels (token refresh needed)
19. Monitor API credits and send email alerts
20. Update Airtable with all URLs and completion status

### Agent Classes
Located in `src/mcp/`:
- `amazon_affiliate_agent_mcp.py` - Amazon product search coordination
- `text_generation_control_agent_mcp_v2.py` - Content generation with retry logic
- `json2video_agent_mcp.py` - Video creation coordination
- `google_drive_agent_mcp.py` - Drive upload coordination
- `wordpress_mcp.py` - WordPress post creation with enhanced formatting
- `youtube_mcp.py` - YouTube upload automation
- `tiktok_workflow_integration.py` - TikTok Reels integration
- `instagram_workflow_integration.py` - Instagram Reels integration

## Configuration

### Required API Keys
Configuration file: `config/api_keys.json`
```json
{
  "airtable_api_key": "",
  "airtable_base_id": "",
  "airtable_table_name": "Video Titles",
  "anthropic_api_key": "",
  "openai_api_key": "",
  "elevenlabs_api_key": "",
  "json2video_api_key": "",
  "amazon_associate_id": "reviewch3kr0d-20",
  "scrapingdog_api_key": "",
  "wordpress_url": "https://reviewch3kr.com",
  "wordpress_user": "",
  "wordpress_password": "",
  "tiktok_client_id": "",
  "tiktok_client_secret": "",
  "instagram_app_id": "",
  "instagram_app_secret": "",
  "email_sender": "shenolreetz@reviewch3kr.com",
  "email_recipient": "shenolb@live.com",
  "credit_monitoring_enabled": true
}
```

### Service Integration
- **YouTube**: OAuth credentials in `config/youtube_credentials.json`
- **Google Drive**: OAuth2 credentials in `config/google_drive_oauth_credentials.json` and token in `config/google_drive_token.json`
- **WordPress**: Site URL and credentials in API keys config
- **TikTok**: App credentials (pending approval)
- **Instagram**: App credentials (pending approval)
- **Email Alerts**: SMTP configuration for credit monitoring

## Important Implementation Notes

### Current State (v2.9 - Full Production Active)
- ✅ **COMPLETE END-TO-END WORKFLOW VALIDATED** (Golf GPS Units processed successfully)
- ✅ **FULL 60-SECOND PRODUCTION VIDEOS** (No more test limitations)
- ✅ **ALL TIMEOUTS COMPLETELY REMOVED** (Uninterrupted execution)
- ✅ **PRODUCTION JSON2Video TEMPLATES** (Full intro + 5 products + outro)
- ✅ **AIRTABLE FIELD MAPPING CORRECTED** (ProductNo1-5Photo properly updated)
- ✅ Enhanced JSON2Video templates with reviews and ratings
- ✅ WordPress integration with product photos and countdown format
- ✅ YouTube Shorts automation (needs token refresh)
- ✅ API credit monitoring with email alerts
- ✅ 90+ keywords across 5 platforms (YouTube, TikTok, Instagram, WordPress, Universal)
- ✅ Amazon-guided OpenAI image generation (5-second rate limiting)
- ✅ ElevenLabs voice generation fully integrated (all voice files uploaded to Drive)
- ✅ Product category extraction for improved Amazon scraping
- ✅ Flow control and validation system
- ✅ Top-to-bottom title processing with automatic failure handling
- ✅ Curated content database (4,188 titles analyzed, 1,095 high-retention selected)
- ✅ Voice field mapping complete (IntroMp3, OutroMp3, Product[X]Mp3)
- ⏸️ TikTok integration **DISABLED** (API still in review)
- ✅ Instagram Reels integration **ENABLED** (needs token refresh)
- ✅ Google Drive OAuth2 authentication complete for voice file uploads

### Current Issues & Status
- ✅ JSON2Video: €39.40 remaining (~197 videos, 11,854 seconds)
- ✅ ScrapingDog: €198.49 remaining (198,490 requests)
- ✅ ElevenLabs: €32.10 remaining (178,334 characters)
- ✅ OpenAI: API authentication verified (usage API error does not affect functionality)

### Code Patterns
- All MCP servers use async/await patterns
- Error handling with try/catch blocks and logging
- Configuration loaded from JSON files
- HTTP requests use httpx for async operations
- Video templates stored in `templates/` directory

### Testing Strategy
- Individual component tests in `src/test_*.py`
- MCP server validation tests in `mcp_servers/test_*.py`
- Integration testing via minimal workflow scripts
- Log files generated with timestamps for debugging

### Development Workflow
1. Test individual components first
2. Run minimal workflow for integration testing
3. Use `run_workflow.sh` for full pipeline testing
4. Check logs in timestamped files for debugging
5. Update Airtable status tracking for progress monitoring
6. Monitor API credits with `python3 src/test_credit_monitoring.py`
7. Test social platform integrations when APIs are approved

## Platform Integration Status

### ✅ Active Platforms
- **Airtable**: Database and workflow tracking
- **Amazon**: Product search and affiliate links  
- **OpenAI**: AI image generation (DALL-E)
- **Anthropic**: Content generation (Claude)
- **JSON2Video**: Enhanced video creation with reviews
- **Google Drive**: Video storage and organization
- **WordPress**: Blog posts with product photos (reviewch3kr.com)
- **YouTube**: Shorts automation

### ⏳ Ready for Activation
- **TikTok**: Reels upload (awaiting API approval)
- **Instagram**: Reels upload (awaiting API approval)

### 🚨 Resolved Issues
- ✅ **Amazon Scraping**: Niche categories now automatically skipped (workflow moves to next title)
- ✅ **Voice Field Mapping**: All voice fields now correctly map to existing Airtable structure
- ✅ **Title Processing Order**: Workflow processes titles top-to-bottom as intended
- ✅ **Google Drive Initialization**: Fixed "'bool' object has no attribute 'files'" error
- ✅ **ProductNo1-5Photo Fields**: Fixed field mapping from DriveImageURL to ProductNo1-5Photo
- ✅ **Production Mode**: Changed from test videos to full 60-second production videos
- ✅ **Timeout Removal**: Eliminated all timeout constraints for uninterrupted workflow
- ⚠️ **YouTube Token Refresh**: Needs manual token refresh for uploads
- ⚠️ **Instagram Token Refresh**: Needs manual token refresh for uploads  
- ⚠️ **OpenAI Usage API**: Credit monitoring shows API error (functionality still works)

## Cost Management
- **Credit Monitoring**: Email alerts when ≤ €10 remaining
- **Estimated Cost**: ~€1.10 per video (~€33/month for 30 videos)
- **Email Alerts**: Sent to shenolb@live.com
- **Auto-monitoring**: Runs after each workflow