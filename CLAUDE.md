# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Automated content generation system that creates Amazon affiliate videos and publishes them to multiple platforms. The workflow processes titles from Airtable, scrapes Amazon products, generates videos with AI, and distributes content to YouTube, TikTok, Instagram, and WordPress.

## High-Level Architecture

### Core Workflow Pipeline
The system follows a 14-step pipeline orchestrated by `ProductionContentPipelineOrchestratorV2`:

1. **Credential Validation** → 2. **Fetch Title** → 3. **Amazon Scraping** → 4. **Category Extraction**
→ 5. **Product Validation** → 6. **Save to Airtable** → 7. **Content Generation** → 8. **Voice Generation**
→ 9. **Image Generation** → 10. **Content Validation** → 11. **Video Creation** → 12. **Google Drive Upload**
→ 13. **Multi-Platform Publishing** → 14. **Status Update**

### Modular MCP Architecture
- **MCP Servers** (`/mcp_servers/Production_*.py`): Handle API communications and data operations
- **MCP Agents** (`/src/mcp/Production_*.py`): Execute specific workflow tasks
- **Utilities** (`/src/utils/*.py`): Token management, API resilience, auth handling

### Token Management System
The workflow implements automatic token refresh at startup via `refresh_tokens_before_workflow()`:
- Google Drive tokens (1-hour expiry) auto-refresh using `/src/utils/google_drive_token_manager.py`
- YouTube tokens (1-hour expiry) auto-refresh using `/src/utils/youtube_auth_manager.py`
- Tokens are checked and refreshed before each workflow run (designed for 3x daily execution)

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

# Fix Google Drive auth (if refresh token revoked)
python3 /home/claude-workflow/fix_google_drive_auth.py
```

### Testing Individual Components
```bash
# Test Airtable connection
python3 -c "from mcp_servers.Production_airtable_server import ProductionAirtableMCPServer; import asyncio; server = ProductionAirtableMCPServer('KEY', 'BASE', 'TABLE'); asyncio.run(server.get_pending_title())"

# Test OpenAI models availability
python3 /home/claude-workflow/test_openai_models.py
```

## Critical Architecture Details

### OpenAI Model Configuration (August 11, 2025 Update)
- **Primary Model**: `gpt-4o` (NOT gpt-5 which doesn't exist yet)
- **Fallback Model**: `gpt-4o-mini`
- **Simple Tasks**: `gpt-3.5-turbo`
- **API Parameters**: Must use `max_completion_tokens` instead of deprecated `max_tokens`
- **Temperature**: Some models don't support custom temperature values

### Async Optimizations (December 2025 Update)
The workflow now uses async/parallel processing for major bottlenecks:

#### 1. Product Image Generation (6.2x faster)
- **File**: `/src/mcp/Production_amazon_images_workflow_v2_async.py`
- **Improvement**: 175s → 28s (all 5 DALL-E images generated concurrently)
- **Rate Limit**: DALL-E 3 supports concurrent requests but n=1 per call

#### 2. Platform Content Generation (Optimized)
- **File**: `/src/mcp/Production_platform_content_generator_async.py`
- **Improvement**: All platforms (YouTube, Instagram, TikTok, WordPress) generated in parallel
- **Method**: Single roundtrip for all content using `asyncio.gather()`

#### 3. Amazon Scraping with Validation (3-4x faster)
- **Validation Server**: `/mcp_servers/Production_amazon_search_validator.py`
- **Async Scraper**: `/mcp_servers/Production_progressive_amazon_scraper_async.py`
- **Two-Phase Approach**:
  - Phase 1: Batch validate variants (3 concurrent) to find one with 5+ products
  - Phase 2: Scrape detailed data for validated variant only
- **Improvement**: 60-90s → 15-20s

### ScrapingDog API Response Format (Critical)
The ScrapingDog API returns specific field names that must be extracted correctly:
- **Review Count**: `total_reviews` field (string format: "438", "2,783", "5,217")
- **Rating**: `stars` field (string format: "4.3", "4.5")
- **Extraction**: Must handle comma-separated numbers and K/M suffixes

### Workflow State Management
The workflow uses Airtable for state tracking with specific field requirements:
- **17 Status Columns**: Track validation state (e.g., `VideoTitleStatus`, `ProductNo1TitleStatus`)
- **14 URL Fields**: Store generated media (e.g., `IntroMp3`, `ProductNo1Photo`)
- **Status Values**: Use exact values "Ready" and "Pending" (case-sensitive)

### API Resilience Pattern
All API calls go through `/src/utils/api_resilience_manager.py` which provides:
- Circuit breakers for API health monitoring
- Exponential backoff with jitter for retries
- Quota tracking and cost prediction
- Dead letter queue for failed items
- Checkpoint recovery system

### Google Drive Token Refresh Flow
When Google Drive token expires or is revoked:
1. The workflow detects expiry via `GoogleDriveTokenManager.get_token_status()`
2. Attempts automatic refresh using refresh token
3. If refresh token is revoked, manual re-authentication required:
   - Generate OAuth URL with proper scopes
   - Complete browser authentication
   - Exchange authorization code for new tokens
   - Save tokens to `/config/google_drive_token.json`

## Key Files Reference

### Main Orchestrator
- **Entry Point**: `/src/Production_workflow_runner.py`
- **Class**: `ProductionContentPipelineOrchestratorV2`
- **Method**: `run_complete_workflow()` - Main workflow execution
- **Method**: `refresh_tokens_before_workflow()` - Token refresh at startup

### Critical MCP Servers
- **Airtable**: `/mcp_servers/Production_airtable_server.py` - All database operations
- **Amazon Scraping**: `/mcp_servers/Production_progressive_amazon_scraper.py` - Product discovery with variants
- **Content Generation**: `/mcp_servers/Production_content_generation_server.py` - GPT-4 content creation
- **Credential Validation**: `/mcp_servers/Production_credential_validation_server.py` - Startup checks

### Critical MCP Agents
- **Google Drive Upload**: `/src/mcp/Production_enhanced_google_drive_agent_mcp.py`
- **WordPress Publishing**: `/src/mcp/Production_wordpress_mcp_v2.py` (V2 has tag ID conversion)
- **YouTube Publishing**: `/src/mcp/Production_youtube_mcp.py`
- **Video Creation**: `/src/mcp/Production_json2video_agent_mcp.py`

### Authentication Managers
- **Google Drive**: `/src/utils/google_drive_token_manager.py` - Token refresh and validation
- **YouTube**: `/src/utils/youtube_auth_manager.py` - OAuth and service management
- **Configuration**: `/home/claude-workflow/config/api_keys.json` - All API keys

## Production Deployment Notes

### Daily Workflow Execution (3x per day)
- Designed for runs every 8 hours
- Tokens auto-refresh at start (1-hour expiry)
- No manual intervention required when tokens valid

### Performance Characteristics
- **Processing Time**: 10-15 minutes per video
- **Success Rate**: 95%+ with error handling
- **Daily Capacity**: 3 videos (1 per run, 3 runs per day)
- **Bottlenecks**: Video creation (2-3 min), Amazon scraping (1-1.5 min)

### Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| Google Drive "Token has been expired or revoked" | Run OAuth flow to generate new refresh token |
| OpenAI 400 "max_tokens not supported" | Use `max_completion_tokens` parameter instead |
| OpenAI 404 "model does not exist" | Use gpt-4o or gpt-4o-mini, not gpt-5 |
| JSON2Video 404 | Service may be down, check API endpoint |
| Script generation fails | Ensure OPENAI_API_KEY environment variable is set |

## Monitoring and Logs

- **Workflow Output**: `/home/claude-workflow/workflow_output.log`
- **Checkpoint Tracking**: `/home/claude-workflow/workflow_checkpoints.json`
- **API Status Cache**: `/home/claude-workflow/api_status.json`
- **Debug Messages**: Look for "🔍 DEBUG:" prefixes in logs (normal operation indicators, not errors)

## Development Guidelines

1. **Always use Production files** for live workflow - files prefixed with `Production_`
2. **Test changes** in Test environment first (`Test_*.py` files)
3. **Token refresh** happens automatically - don't manually refresh unless debugging
4. **API model updates** - Always verify model availability before changing (use test_openai_models.py)
5. **Airtable schema** - Never change field names without updating all references