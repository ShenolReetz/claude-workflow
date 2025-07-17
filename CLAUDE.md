# Claude Workflow Project Documentation

## Project Status: Production Ready v3.1

**Last Updated:** July 17, 2025  
**Current Version:** v3.1 Sequential ID Selection Integration - Complete Workflow Synchronization  
**Architecture:** Dual-Flow System (Production + Testing)

## Overview

This project implements a comprehensive automated content generation workflow that processes titles from Airtable, generates Amazon affiliate content, creates videos, and publishes to multiple platforms (YouTube, TikTok, Instagram, WordPress).

## Architecture Summary

The project now operates with a **dual-flow architecture**:

1. **Production Flow** - Live workflow for actual content generation
2. **Test Flow** - Complete testing environment with isolated Test MCP servers and agents

## Project Structure

### Main Production Workflow

**Entry Point:** `src/workflow_runner.py`

#### Core MCP Servers (`mcp_servers/`)
- `airtable_server.py` - Airtable database operations
- `amazon_affiliate_server.py` - Amazon affiliate link generation
- `amazon_category_scraper.py` - Amazon product category extraction
- `amazon_product_validator.py` - Amazon product validation
- `content_generation_server.py` - AI content generation
- `enhanced_amazon_scraper.py` - Advanced Amazon scraping
- `flow_control_server.py` - Workflow orchestration
- `google_drive_server.py` - Google Drive file management
- `image_generation_server.py` - AI image generation
- `instagram_server.py` - Instagram operations
- `json2video_enhanced_server_v2.py` - Video generation
- `product_category_extractor_server.py` - Product categorization
- `scrapingdog_amazon_server.py` - Alternative Amazon scraping
- `text_generation_control_server.py` - Text generation control
- `tiktok_server.py` - TikTok operations
- `voice_generation_server.py` - AI voice generation

#### Core MCP Agents (`src/mcp/`)
- `amazon_affiliate_agent_mcp.py` - Amazon affiliate workflow
- `amazon_drive_integration.py` - Drive integration for Amazon data
- `amazon_guided_image_generation.py` - AI-guided image creation
- `amazon_images_workflow_v2.py` - Image processing workflow
- `google_drive_agent_mcp.py` - Google Drive agent
- `instagram_workflow_integration.py` - Instagram publishing
- `intro_image_generator.py` - Video intro generation
- `json2video_agent_mcp.py` - Video creation agent
- `outro_image_generator.py` - Video outro generation
- `platform_content_generator.py` - Multi-platform content
- `text_generation_control_agent_mcp_v2.py` - Text control agent
- `tiktok_workflow_integration.py` - TikTok publishing
- `voice_timing_optimizer.py` - Voice timing optimization
- `wordpress_mcp.py` - WordPress publishing
- `youtube_mcp.py` - YouTube publishing

### Test Workflow Environment

**Entry Point:** `src/Test_workflow_runner.py`

#### Test MCP Servers (`mcp_servers/Test_*.py`)
Complete mirror of production servers with `Test_` prefix:
- `Test_airtable_server.py`
- `Test_amazon_affiliate_server.py`
- `Test_amazon_category_scraper.py`
- `Test_amazon_product_validator.py`
- `Test_content_generation_server.py`
- `Test_enhanced_amazon_scraper.py`
- `Test_flow_control_server.py`
- `Test_google_drive_server.py`
- `Test_image_generation_server.py`
- `Test_instagram_server.py`
- `Test_json2video_enhanced_server_v2.py`
- `Test_product_category_extractor_server.py`
- `Test_scrapingdog_amazon_server.py`
- `Test_text_generation_control_server.py`
- `Test_tiktok_server.py`
- `Test_voice_generation_server.py`

#### Test MCP Agents (`src/mcp/Test_*.py`)
Complete mirror of production agents with `Test_` prefix:
- `Test_amazon_affiliate_agent_mcp.py`
- `Test_amazon_drive_integration.py`
- `Test_amazon_guided_image_generation.py`
- `Test_amazon_images_workflow_v2.py`
- `Test_google_drive_agent_mcp.py`
- `Test_instagram_workflow_integration.py`
- `Test_intro_image_generator.py`
- `Test_json2video_agent_mcp.py`
- `Test_outro_image_generator.py`
- `Test_platform_content_generator.py`
- `Test_text_generation_control_agent_mcp_v2.py`
- `Test_tiktok_workflow_integration.py`
- `Test_voice_timing_optimizer.py`
- `Test_wordpress_mcp.py`
- `Test_youtube_mcp.py`

## Workflow Features

### Production Workflow Capabilities
1. **Airtable Integration** - Fetches pending titles and saves generated content
2. **Amazon Product Validation** - Validates titles have sufficient products (minimum 5)
3. **Multi-Platform Content Generation** - Creates optimized content for YouTube, TikTok, Instagram, WordPress
4. **AI Content Creation** - Generates scripts, keywords, and optimized titles
5. **Voice Generation** - Creates AI voices for intro, outro, and product segments
6. **Image Generation** - Creates custom intro/outro images and product images
7. **Video Production** - Generates complete videos with JSON2Video integration
8. **Multi-Platform Publishing** - Publishes to YouTube, TikTok, Instagram, WordPress
9. **Google Drive Integration** - Manages file storage and organization
10. **Error Handling & Recovery** - Robust error handling with fallback mechanisms

### Test Workflow Capabilities
- **Complete Production Mirror** - All production features available in isolated environment
- **Safe Testing** - No interference with production data or processes
- **Independent Execution** - Runs completely separately from production workflow
- **Development & QA** - Perfect for feature development and quality assurance

## Usage

### Running Production Workflow
```bash
cd /home/claude-workflow
python3 src/workflow_runner.py
```

### Running Test Workflow
```bash
cd /home/claude-workflow
python3 src/Test_workflow_runner.py
```

## Configuration

### Required API Keys (`config/api_keys.json`)
- `airtable_api_key` - Airtable database access
- `airtable_base_id` - Airtable base identifier
- `airtable_table_name` - Airtable table name
- `anthropic_api_key` - Claude AI API key
- `elevenlabs_api_key` - Voice generation API key
- `openai_api_key` - OpenAI API key for image generation
- `scrapingdog_api_key` - Web scraping API key
- `json2video_api_key` - Video generation API key
- Google Drive API credentials
- YouTube API credentials
- Instagram API credentials
- WordPress API credentials
- TikTok API credentials

## Project Cleanup Status

### Completed Cleanup
✅ **Unused files removed** - All deprecated and unused files have been deleted  
✅ **Dual architecture implemented** - Clean separation between production and test flows  
✅ **Import issues resolved** - All import dependencies fixed and verified  
✅ **Code compilation verified** - All files compile and import successfully  

### Current File Status
- **Production files:** Clean, optimized, and production-ready
- **Test files:** Complete mirror with Test_ prefix for safe testing
- **Deprecated files:** Removed from project
- **Documentation:** Up-to-date and comprehensive

## Development Guidelines

### Adding New Features
1. Develop in Test environment first using `Test_` prefixed files
2. Test thoroughly with `Test_workflow_runner.py`
3. Once verified, implement in production files using integration process
4. Maintain dual-flow architecture

### Testing Protocol
1. Use Test workflow for all development and QA
2. Test environment is completely isolated
3. Production workflow should only be used for live content generation
4. All new features must pass Test workflow before production deployment

## Flow Synchronization System

### Overview
The project uses a **Test-First Development** approach where:
- All changes are developed and tested in Test flow first
- Successful changes are systematically integrated into Production flow
- Integration is tracked and documented for safety

### Synchronization Documents
- **`FLOW_SYNC_TRACKER.md`** - Tracks differences between Test and Production flows
- **`INTEGRATION_CHECKLIST.md`** - Step-by-step integration procedures
- **`CLAUDE.md`** - This documentation (updated with each integration)

### Integration Workflow

#### 1. Development Phase (Test Environment)
```bash
# Work in Test files
vim mcp_servers/Test_[component].py
vim src/mcp/Test_[component].py

# Test changes
python3 src/Test_workflow_runner.py
```

#### 2. Verification Phase
```bash
# Verify Test workflow works
python3 -c "import src.Test_workflow_runner; print('✅ Test workflow OK')"

# Document changes in FLOW_SYNC_TRACKER.md
```

#### 3. Integration Phase
```bash
# Create backup
cp [production_file].py [production_file].py.backup_$(date +%Y%m%d_%H%M%S)

# Apply changes (remove Test_ prefixes, update imports)
# Follow INTEGRATION_CHECKLIST.md

# Verify integration
python3 -m py_compile [production_file].py
python3 -c "import src.workflow_runner; print('✅ Production workflow OK')"
```

#### 4. Documentation Phase
```bash
# Update FLOW_SYNC_TRACKER.md with integration status
# Update CLAUDE.md if architectural changes
# Clean up old backups (keep recent ones)
```

### Current Synchronization Status
- **Last Sync:** July 16, 2025
- **Status:** Test flow is clone of Production flow
- **Pending Integrations:** None (flows are synchronized)
- **Known Fixes in Test:** Import issue in `Test_amazon_drive_integration.py` (Production already correct)

### Integration Safety Measures
1. **Always backup before integration**
2. **Test compilation after each change**
3. **Verify full workflow functionality**
4. **Document all changes**
5. **Keep rollback procedure ready**

### Emergency Rollback
```bash
# If integration fails, restore from backup
cp [production_file].py.backup_[timestamp] [production_file].py
python3 -m py_compile [production_file].py  # Verify rollback
```

## Technical Notes

### MCP Architecture
- **MCP Servers:** Core functionality providers
- **MCP Agents:** Workflow orchestrators that use multiple servers
- **Workflow Runners:** Entry points that coordinate the entire process

### Error Handling
- Comprehensive error handling with fallback mechanisms
- Failed titles are marked and skipped to prevent infinite loops
- Detailed logging for debugging and monitoring

### Performance Optimizations
- Efficient API usage with proper rate limiting
- Optimized file handling and storage
- Streamlined workflow processes

## Recent Updates (v3.1)

### Sequential ID Selection Integration
- **✅ CRITICAL FIX:** Production Airtable server now uses correct `ID` field instead of non-existent `TitleID`
- **✅ DATA POPULATED:** ID column populated with 4,188 sequential numbers (1-4188)
- **✅ VERIFIED:** Both Test and Production workflows now select titles sequentially by lowest ID
- **✅ WORKFLOW CONFIRMED:** Test workflow completed successfully with ID-based selection

### Text-to-Speech Timing Validation System
- **✅ IMPLEMENTED:** Complete text validation system with dual-flow architecture
- **✅ AUTO-APPROVAL:** Test environment auto-approves all validations for speed
- **✅ PRODUCTION VALIDATION:** Production performs actual TTS timing validation
- **✅ REGENERATION:** Failed validations trigger automatic text regeneration
- **✅ VIDEO PREREQUISITE:** Video generation blocked until all 12 status columns are "Approved"

### Title Processing Enhancement
- Sequential processing from top to bottom (ID: 1, 2, 3... 4188)
- No more random title selection - predictable, ordered processing
- Proper skipping of completed titles to process next available
- High-retention title filtering system ready for 1500 best titles

### Enhanced JSON2Video Integration (v3.0)
- Professional video production capabilities
- Improved voice timing optimization
- Enhanced image generation for intro/outro
- Better platform-specific content optimization

### Dual-Flow Architecture (v3.0)
- Complete Test environment implementation
- Production and Test workflow separation
- Safe development and testing environment

### Code Quality Improvements (v3.0)
- Removed all unused and deprecated files
- Fixed import dependencies
- Improved code organization and structure
- Enhanced documentation and comments

### Development Environment Configuration
- **Bash timeout set to 20 minutes** for workflow monitoring (user repeatedly requested this)
- Test workflow optimizations for rapid development cycles
- Comprehensive error handling and logging

### Text-to-Speech Timing Validation Status Columns
**CRITICAL:** The following 12 Airtable columns must be updated with validation status:

📊 **Video Content Status Columns (5-second limit):**
- `VideoTitleStatus` → Validates: VideoTitle field
- `VideoDescriptionStatus` → Validates: VideoDescription field

📦 **Product Content Status Columns (9-second limit each):**
- `ProductNo1TitleStatus` → Validates: ProductNo1Title field
- `ProductNo1DescriptionStatus` → Validates: ProductNo1Description field
- `ProductNo2TitleStatus` → Validates: ProductNo2Title field
- `ProductNo2DescriptionStatus` → Validates: ProductNo2Description field
- `ProductNo3TitleStatus` → Validates: ProductNo3Title field
- `ProductNo3DescriptionStatus` → Validates: ProductNo3Description field
- `ProductNo4TitleStatus` → Validates: ProductNo4Title field
- `ProductNo4DescriptionStatus` → Validates: ProductNo4Description field
- `ProductNo5TitleStatus` → Validates: ProductNo5Title field
- `ProductNo5DescriptionStatus` → Validates: ProductNo5Description field

**Status Values:**
- `"Approved"` - Text fits within timing requirements
- `"Rejected"` - Text exceeds timing limits (triggers regeneration in production)
- `"Pending"` - Awaiting validation or during regeneration process

**Test Environment:** All columns auto-populated with "Approved" for speed
**Production Environment:** Actual validation with regeneration for failed fields

## Future Roadmap

### Planned Features
- Advanced analytics and reporting
- Enhanced AI content optimization
- Additional platform integrations
- Performance monitoring and optimization

### Maintenance Tasks
- Regular API key rotation
- Performance monitoring and optimization
- Feature updates and improvements
- Security audits and updates

---

*This documentation is maintained and updated with each major version release.*