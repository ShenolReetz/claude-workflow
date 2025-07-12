# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
This is an automated video content creation pipeline that generates "Top 5" product videos with affiliate monetization. It integrates multiple AI services to create YouTube-style content automatically from Airtable topics.

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
- **Google Drive MCP** (`mcp_servers/google_drive_server.py`) - Video storage and organization
- **Voice Generation MCP** (`mcp_servers/voice_generation_server.py`) - ElevenLabs voice synthesis
- **Image Generation MCP** (`mcp_servers/image_generation_server.py`) - DALL-E product images

### Workflow Orchestrator
Main orchestrator: `src/workflow_runner.py` (class: `ContentPipelineOrchestrator`)

Workflow stages:
1. Fetch pending titles from Airtable
2. Generate SEO keywords and video descriptions
3. Search Amazon products and generate affiliate links
4. Create video using JSON2Video template
5. Upload video to Google Drive
6. Create WordPress blog post
7. Upload to YouTube
8. Update Airtable with all URLs and completion status

### Agent Classes
Located in `src/mcp/`:
- `amazon_affiliate_agent_mcp.py` - Amazon product search coordination
- `text_generation_control_agent_mcp_v2.py` - Content generation with retry logic
- `json2video_agent_mcp.py` - Video creation coordination
- `google_drive_agent_mcp.py` - Drive upload coordination
- `wordpress_mcp.py` - WordPress post creation
- `youtube_mcp.py` - YouTube upload automation

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
  "scrapingdog_api_key": ""
}
```

### Service Integration
- **YouTube**: OAuth credentials in `config/youtube_credentials.json`
- **Google Drive**: Service account credentials in `config/google_drive_credentials.json`
- **WordPress**: Site URL and credentials in API keys config

## Important Implementation Notes

### Current State (v1.0)
- Workflow runs end-to-end successfully
- Test mode uses 8-second videos (production: 60 seconds)
- Image and voice generation disabled for testing
- All MCP servers are functional

### Known Issues
- ScrapingDog API rate limiting (429 errors) - need 6-second delays between requests
- Some test files reference missing Airtable fields (TextControlStatus, TextControlAttempts)

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