# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Automated content generation system that creates Amazon affiliate videos and publishes them to multiple platforms. The workflow processes titles from Airtable, scrapes Amazon products, generates videos with AI, and distributes content to YouTube, TikTok, Instagram, and WordPress.

## Architecture

### Dual-Flow System
- **Production Flow**: `/src/Production_workflow_runner.py` - Live workflow with real API calls
- **Test Flow**: `/src/Test_workflow_runner.py` - Isolated testing with defaults (DO NOT use for production)

### MCP (Model Context Protocol) Architecture
The system uses a modular architecture with:
- **MCP Servers** (`/mcp_servers/Production_*.py`): Handle API communications and data operations
- **MCP Agents** (`/src/mcp/Production_*.py`): Execute specific workflow tasks
- **Utilities** (`/src/utils/*.py`): Token management, API resilience, auth handling

## Essential Commands

### Running the Workflow
```bash
# Main production workflow (includes automatic token refresh)
python3 /home/claude-workflow/src/Production_workflow_runner.py

# With explicit token refresh wrapper
python3 /home/claude-workflow/run_workflow_with_token_refresh.py

# Check all authentication status
python3 /home/claude-workflow/check_all_auth_status.py
```

### Token Management
```bash
# Check Google Drive token
python3 /home/claude-workflow/src/utils/google_drive_token_manager.py

# Check YouTube token  
python3 /home/claude-workflow/src/utils/youtube_auth_manager.py
```

### Testing Individual Components
```bash
# Test Airtable connection
python3 -c "from mcp_servers.Production_airtable_server import ProductionAirtableMCPServer; import asyncio; server = ProductionAirtableMCPServer('KEY', 'BASE', 'TABLE'); asyncio.run(server.get_pending_title())"

# Test text validation
python3 test_text_length_validation.py
```

## Critical Files Reference

### Workflow Issues
- **Main Entry**: `/src/Production_workflow_runner.py` - Class: `ProductionContentPipelineOrchestratorV2`
- **Token Refresh**: Method `refresh_tokens_before_workflow()` runs at workflow start

### API Integration Issues
- **Airtable**: `/mcp_servers/Production_airtable_server.py`
- **Amazon Scraping**: `/mcp_servers/Production_progressive_amazon_scraper.py`
- **Google Drive**: `/src/mcp/Production_enhanced_google_drive_agent_mcp.py`
- **WordPress**: `/src/mcp/Production_wordpress_mcp_v2.py` (V2 has tag ID conversion)
- **YouTube**: `/src/mcp/Production_youtube_mcp.py`

### Authentication Issues
- **Google Drive Token**: `/src/utils/google_drive_token_manager.py`
- **YouTube Token**: `/src/utils/youtube_auth_manager.py`
- **Config**: `/home/claude-workflow/config/api_keys.json`

## Workflow Pipeline (14 Steps)

1. **Credential Validation** - Verify all API keys
2. **Fetch Title** - Get pending title from Airtable (smallest ID)
3. **Amazon Scraping** - Progressive variant testing for 5+ products
4. **Category Extraction** - OpenAI categorization
5. **Product Validation** - Min 3.5★ rating, 10+ reviews
6. **Save to Airtable** - Products with affiliate links
7. **Content Generation** - Platform-specific content
8. **Voice Generation** - ElevenLabs TTS (7 segments)
9. **Image Generation** - DALL-E intro/outro
10. **Content Validation** - TTS timing checks
11. **Video Creation** - JSON2Video API
12. **Google Drive Upload** - Organized by type
13. **Publishing** - YouTube, TikTok, Instagram, WordPress
14. **Status Update** - Mark complete in Airtable

## Important Production vs Test Distinction

**ALWAYS use Production files for live workflow:**
- ✅ `Production_*.py` files
- ✅ `/src/Production_workflow_runner.py`
- ❌ NOT `Test_*.py` files
- ❌ NOT `/src/Test_workflow_runner.py`

## API Configuration

All API keys in `/config/api_keys.json`:
- `airtable_api_key`, `airtable_base_id`, `airtable_table_name`
- `openai_api_key`, `anthropic_api_key`
- `elevenlabs_api_key`, `scrapingdog_api_key`
- `json2video_api_key`
- `wordpress_user`, `wordpress_password`, `wordpress_url`

## Performance Characteristics

- **Processing Time**: 10-15 minutes per video
- **Success Rate**: 95%+ with error handling
- **Daily Capacity**: 96-144 videos
- **Token Refresh**: Automatic every workflow run (1-hour tokens)
- **Bottlenecks**: Video creation (2-3 min), Amazon scraping (1-1.5 min)

## Error Handling Patterns

The workflow uses comprehensive error handling:
- Automatic token refresh before each run
- API resilience manager for rate limiting
- Fallback mechanisms for failed operations
- Status tracking in Airtable for debugging

## Airtable Schema Requirements

17 status columns for validation:
- `VideoTitleStatus`, `VideoDescriptionStatus`
- `ProductNo[1-5]TitleStatus`, `ProductNo[1-5]DescriptionStatus`, `ProductNo[1-5]PhotoStatus`

14 URL fields for media:
- Audio: `IntroMp3`, `OutroMp3`, `Product[1-5]Mp3`
- Images: `IntroPhoto`, `OutroPhoto`, `ProductNo[1-5]Photo`

## Recent Fixes (August 9, 2025)

- ✅ Google Drive authentication with auto-refresh
- ✅ YouTube authentication with auto-refresh
- ✅ WordPress tag conversion to IDs
- ✅ Enhanced error logging in Airtable operations
- ✅ Complete workflow operational for 3x daily runs

## Development Guidelines

1. **When debugging production issues**: Always refer to `/PRODUCTION_FLOW_COMPONENTS.md`
2. **When modifying workflow**: Test changes in Test environment first
3. **When adding features**: Follow existing MCP server/agent patterns
4. **When handling tokens**: Use existing token managers, never hardcode

## Monitoring and Logs

- **Workflow logs**: `/home/claude-workflow/workflow_output.log`
- **Checkpoint tracking**: `/home/claude-workflow/workflow_checkpoints.json`
- **API status**: `/home/claude-workflow/api_status.json`

## Claude Code Agent Integration

Three specialized agents available:
- `mcp-test-agent`: MCP tools testing
- `python-error-diagnostician`: Error analysis
- `workflow-performance-optimizer`: Performance optimization

## MCP Tool Permissions

Pre-approved tools in `.claude/settings.local.json`:
- Airtable operations
- Python execution
- Git operations
- Web fetching for Remotion and GitHub