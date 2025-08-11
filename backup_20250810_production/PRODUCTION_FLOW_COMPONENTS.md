# Production Flow Components Documentation

## 🚨 CRITICAL: PRODUCTION FILES ONLY
This document lists ONLY the files used in the Production workflow. 
**DO NOT** modify Test files when working on Production issues.

---

## 📁 Main Entry Point

### Production Workflow Runner
**File**: `/src/Production_workflow_runner.py`
- **Class**: `ProductionContentPipelineOrchestratorV2`
- **Purpose**: Main orchestrator for the entire production workflow
- **Entry Method**: `run_complete_workflow()`
- **Token Refresh**: `refresh_tokens_before_workflow()` - Runs at start

---

## 🔧 MCP Servers (11 Total)

Located in `/home/claude-workflow/mcp_servers/`

### 1. Production_airtable_server.py
- **Class**: `ProductionAirtableMCPServer`
- **Purpose**: All Airtable operations (read/write records)
- **Used in Steps**: 1, 2, 6, 7, throughout for status updates

### 2. Production_content_generation_server.py
- **Class**: `ProductionContentGenerationMCPServer`
- **Purpose**: Generate content using OpenAI GPT models
- **Used in Steps**: 7 (content generation)

### 3. Production_progressive_amazon_scraper.py
- **Class**: `ProductionProgressiveAmazonScraper`
- **Purpose**: Scrape Amazon products with variant testing
- **Used in Steps**: 3 (product discovery)

### 4. Production_voice_generation_server.py
- **Class**: `ProductionVoiceGenerationMCPServer`
- **Purpose**: Generate voice using ElevenLabs API
- **Used in Steps**: 8 (voice narration)

### 5. Production_product_category_extractor_server.py
- **Class**: `ProductionProductCategoryExtractorMCPServer`
- **Purpose**: Extract product category from title
- **Used in Steps**: 4 (category extraction)

### 6. Production_flow_control_server.py
- **Class**: `ProductionFlowControlMCPServer`
- **Purpose**: Control workflow flow and decision making
- **Used**: Throughout workflow for flow control

### 7. Production_amazon_product_validator.py
- **Class**: `ProductionAmazonProductValidator`
- **Purpose**: Validate scraped Amazon products
- **Used in Steps**: 5 (product validation)

### 8. Production_credential_validation_server.py
- **Class**: `ProductionCredentialValidationServer`
- **Purpose**: Validate all API credentials at start
- **Used in Steps**: 1 (credential check)

### 9. Production_scraping_variant_generator.py *(Helper)*
- **Purpose**: Generate search variants for scraping
- **Used by**: Progressive scraper

### 10. Production_amazon_category_scraper.py *(Unused)*
- Legacy file, not actively used

### 11. Production_scrapingdog_amazon_server.py *(Unused)*
- Legacy file, replaced by progressive scraper

---

## 🤖 MCP Agents (17 Total)

Located in `/home/claude-workflow/src/mcp/`

### Core Workflow Agents (Used in Main Flow)

#### 1. Production_amazon_affiliate_agent_mcp.py
- **Function**: `production_run_amazon_affiliate_generation()`
- **Purpose**: Generate Amazon affiliate links
- **Used in Steps**: 6 (affiliate link generation)

#### 2. Production_text_generation_control_agent_mcp_v2.py
- **Function**: `production_run_text_control_with_regeneration()`
- **Purpose**: Generate scripts with regeneration capability
- **Used in Steps**: 6.5 (script generation)

#### 3. Production_json2video_agent_mcp.py
- **Function**: `production_run_video_creation()`
- **Purpose**: Create video using JSON2Video API
- **Used in Steps**: 11 (video creation)

#### 4. Production_enhanced_google_drive_agent_mcp.py
- **Function**: `production_upload_all_assets_to_google_drive()`
- **Purpose**: Upload all assets to Google Drive
- **Used in Steps**: 12 (Google Drive upload)
- **Note**: PRIMARY Google Drive agent

#### 5. Production_wordpress_mcp_v2.py
- **Class**: `ProductionWordPressMCPV2`
- **Purpose**: Publish to WordPress with tag ID conversion
- **Used in Steps**: 13 (WordPress publishing)

#### 6. Production_youtube_mcp.py
- **Class**: `ProductionYouTubeMCP`
- **Purpose**: Upload videos to YouTube
- **Used in Steps**: 13 (YouTube publishing)

#### 7. Production_voice_timing_optimizer.py
- **Class**: `ProductionVoiceTimingOptimizer`
- **Purpose**: Optimize voice timing for TTS
- **Used in Steps**: 8 (voice generation)

#### 8. Production_intro_image_generator.py
- **Function**: `production_generate_intro_image_for_workflow()`
- **Purpose**: Generate intro images
- **Used in Steps**: 9 (image generation)

#### 9. Production_outro_image_generator.py
- **Function**: `production_generate_outro_image_for_workflow()`
- **Purpose**: Generate outro images
- **Used in Steps**: 9 (image generation)

#### 10. Production_platform_content_generator.py
- **Function**: `production_generate_platform_content_for_workflow()`
- **Purpose**: Generate platform-specific content
- **Used in Steps**: 7 (content generation)

#### 11. Production_text_length_validation_with_regeneration_agent_mcp.py
- **Function**: `production_run_text_validation_with_regeneration()`
- **Purpose**: Validate and regenerate text for TTS timing
- **Used in Steps**: 10 (content validation)

#### 12. Production_amazon_images_workflow_v2.py
- **Function**: `production_download_and_save_amazon_images_v2()`
- **Purpose**: Download and enhance Amazon product images
- **Used in Steps**: 5.5 (image enhancement)

### Supporting Agents (Available but not in main flow)

#### 13. Production_google_drive_agent_mcp.py
- Legacy Google Drive agent (replaced by enhanced version)

#### 14. Production_wordpress_mcp.py
- Legacy WordPress agent (replaced by V2)

#### 15. Production_amazon_guided_image_generation.py
- Alternative image generation approach

#### 16. Production_amazon_drive_integration.py
- Amazon to Drive integration helper

#### 17. Production_video_status_monitoring.py
- Video status monitoring utilities

---

## 🛠️ Utility Files (7 Total)

Located in `/home/claude-workflow/src/utils/`

### 1. api_resilience_manager.py
- **Class**: `APIResilienceManager`
- **Purpose**: Handle API rate limiting and retries
- **Used**: Throughout workflow

### 2. google_drive_token_manager.py
- **Class**: `GoogleDriveTokenManager`
- **Purpose**: Manage Google Drive OAuth tokens
- **Used**: Token refresh at workflow start

### 3. youtube_auth_manager.py
- **Class**: `YouTubeAuthManager`
- **Purpose**: Manage YouTube OAuth tokens
- **Used**: Token refresh at workflow start

### 4. google_drive_auth_manager.py
- **Class**: `GoogleDriveAuthManager`
- **Purpose**: Google Drive authentication handling
- **Used**: By Google Drive agents

### 5. filename_utils.py
- **Purpose**: Utility functions for filename handling
- **Used**: Various file operations

### 6. openai_helper.py
- **Purpose**: OpenAI API helper functions
- **Used**: Content generation

### 7. __init__.py
- Package initialization file

---

## 📋 Workflow Steps & Component Usage

### Pre-Workflow: Token Refresh
- `google_drive_token_manager.py`
- `youtube_auth_manager.py`

### Step 1: Credential Validation
- `Production_credential_validation_server.py`

### Step 2: Fetch Pending Title
- `Production_airtable_server.py`

### Step 3: Amazon Product Scraping
- `Production_progressive_amazon_scraper.py`
- `Production_scraping_variant_generator.py` (helper)

### Step 4: Category Extraction
- `Production_product_category_extractor_server.py`

### Step 5: Product Validation
- `Production_amazon_product_validator.py`

### Step 5.5: Product Image Enhancement
- `Production_amazon_images_workflow_v2.py`

### Step 6: Save Products to Airtable
- `Production_airtable_server.py`
- `Production_amazon_affiliate_agent_mcp.py`

### Step 6.5: Script Generation
- `Production_text_generation_control_agent_mcp_v2.py`

### Step 7: Content Generation
- `Production_content_generation_server.py`
- `Production_platform_content_generator.py`

### Step 8: Voice Generation
- `Production_voice_generation_server.py`
- `Production_voice_timing_optimizer.py`

### Step 9: Image Generation
- `Production_intro_image_generator.py`
- `Production_outro_image_generator.py`

### Step 10: Content Validation
- `Production_text_length_validation_with_regeneration_agent_mcp.py`

### Step 11: Video Creation
- `Production_json2video_agent_mcp.py`

### Step 12: Google Drive Upload
- `Production_enhanced_google_drive_agent_mcp.py`
- `google_drive_auth_manager.py`

### Step 13: Platform Publishing
- `Production_youtube_mcp.py`
- `Production_wordpress_mcp_v2.py`

### Step 14: Workflow Completion
- `Production_airtable_server.py` (status updates)

---

## 🔑 Configuration Files

### Primary Config
- `/home/claude-workflow/config/api_keys.json` - All API keys and settings

### Token Files
- `/home/claude-workflow/config/google_drive_token.json`
- `/home/claude-workflow/config/youtube_token.json`
- `/home/claude-workflow/config/instagram_token_cache.json`

### OAuth Credentials
- `/home/claude-workflow/config/google_drive_oauth_credentials.json`
- `/home/claude-workflow/config/youtube_credentials.json`

---

## ⚠️ Important Notes

### DO NOT CONFUSE WITH TEST FILES
All Test files have `Test_` prefix. Examples:
- ❌ `Test_workflow_runner.py` - NOT for production
- ❌ `Test_airtable_server.py` - NOT for production
- ✅ `Production_workflow_runner.py` - USE THIS
- ✅ `Production_airtable_server.py` - USE THIS

### Version Notes
- `Production_wordpress_mcp_v2.py` - Current version (with tag ID conversion)
- `Production_wordpress_mcp.py` - Legacy (do not use)
- `Production_enhanced_google_drive_agent_mcp.py` - Current version
- `Production_google_drive_agent_mcp.py` - Legacy (do not use)

### Critical Files for Debugging
1. **Workflow Issues**: `/src/Production_workflow_runner.py`
2. **Airtable Issues**: `/mcp_servers/Production_airtable_server.py`
3. **Google Drive Issues**: `/src/mcp/Production_enhanced_google_drive_agent_mcp.py`
4. **WordPress Issues**: `/src/mcp/Production_wordpress_mcp_v2.py`
5. **Token Issues**: `/src/utils/google_drive_token_manager.py`

---

## 🚀 Running Production Workflow

### Main Command
```bash
python3 /home/claude-workflow/src/Production_workflow_runner.py
```

### With Explicit Token Refresh
```bash
python3 /home/claude-workflow/run_workflow_with_token_refresh.py
```

### Check Auth Status
```bash
python3 /home/claude-workflow/check_all_auth_status.py
```

---

## 📊 Summary Statistics

- **Total Production Files**: 35
- **MCP Servers**: 11 (8 active, 3 legacy/unused)
- **MCP Agents**: 17 (12 active, 5 supporting)
- **Utility Files**: 7
- **Workflow Steps**: 14
- **External APIs**: 8 (Airtable, OpenAI, ElevenLabs, ScrapingDog, JSON2Video, Google Drive, YouTube, WordPress)

---

## 🔄 Update History

- **Last Updated**: August 9, 2025
- **Version**: Production V2 with Enhanced Scraping
- **Token Refresh**: Integrated at workflow start
- **WordPress**: V2 with tag ID conversion
- **Google Drive**: Enhanced agent with folder structure

---

**⚠️ ALWAYS REFER TO THIS DOCUMENT WHEN WORKING ON PRODUCTION ISSUES**