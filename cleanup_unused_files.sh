#!/bin/bash
# Cleanup script for unused files in the new agent orchestration system

echo "🧹 Starting cleanup of unused files..."
echo ""

# Create backup directory
BACKUP_DIR="/home/claude-workflow/backup_old_files_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
echo "📦 Backup directory created: $BACKUP_DIR"
echo ""

# Function to move file to backup
backup_and_remove() {
    local file="$1"
    if [ -f "$file" ]; then
        echo "  Moving $file to backup..."
        mv "$file" "$BACKUP_DIR/"
    fi
}

# === REMOVE UNUSED MCP SERVERS ===
echo "🗑️  Removing unused MCP servers..."

# Duplicates (functionality moved to _mcp_server.py versions)
backup_and_remove "mcp_servers/production_quality_assurance.py"
backup_and_remove "mcp_servers/production_analytics_tracker.py"
backup_and_remove "mcp_servers/production_remotion_wow_video_mcp.py"
backup_and_remove "mcp_servers/production_content_generation_server.py"
backup_and_remove "mcp_servers/production_voice_generation_server_local.py"

# Not used by agent system
backup_and_remove "mcp_servers/production_flow_control_server.py"
backup_and_remove "mcp_servers/production_credential_validation_server.py"
backup_and_remove "mcp_servers/production_auto_recovery_manager.py"
backup_and_remove "mcp_servers/production_cost_tracker.py"
backup_and_remove "mcp_servers/production_thumbnail_generator.py"
backup_and_remove "mcp_servers/production_title_optimizer.py"
backup_and_remove "mcp_servers/production_hashtag_optimizer.py"
backup_and_remove "mcp_servers/production_trending_products.py"
backup_and_remove "mcp_servers/production_token_lifecycle_manager.py"
backup_and_remove "mcp_servers/production_airtable_server.py"
backup_and_remove "mcp_servers/production_amazon_product_validator.py"
backup_and_remove "mcp_servers/production_amazon_search_validator.py"
backup_and_remove "mcp_servers/production_product_category_extractor_server.py"
backup_and_remove "mcp_servers/production_progressive_amazon_scraper_async.py"
backup_and_remove "mcp_servers/production_progressive_amazon_scraper.py"
backup_and_remove "mcp_servers/production_scraping_variant_generator.py"
backup_and_remove "mcp_servers/product_category_extractor.py"

echo "✅ Unused MCP servers cleaned"
echo ""

# === REMOVE UNUSED SRC/MCP FILES ===
echo "🗑️  Removing unused src/mcp files..."

# Not used by agents
backup_and_remove "src/mcp/production_youtube_mcp.py"
backup_and_remove "src/mcp/production_amazon_drive_integration.py"
backup_and_remove "src/mcp/production_voice_timing_optimizer.py"
backup_and_remove "src/mcp/production_imagen4_ultra_with_gpt4_vision.py"
backup_and_remove "src/mcp/production_video_status_monitoring.py"
backup_and_remove "src/mcp/production_amazon_scraper_local_save.py"
backup_and_remove "src/mcp/production_amazon_guided_image_generation.py"
backup_and_remove "src/mcp/production_platform_content_generator_async.py"
backup_and_remove "src/mcp/production_text_length_validation_with_regeneration_agent_mcp.py"
backup_and_remove "src/mcp/production_amazon_affiliate_agent_mcp.py"

echo "✅ Unused src/mcp files cleaned"
echo ""

# === REMOVE OLD DOCUMENTATION FILES ===
echo "🗑️  Removing old/superseded documentation files..."

# Old status reports and plans (superseded by AGENT_IMPLEMENTATION_COMPLETE.md)
backup_and_remove "AGENT_REFACTORING_PLAN.md"
backup_and_remove "AIRTABLE_API_LIMIT_FIX.md"
backup_and_remove "airtable_status_integration.md"
backup_and_remove "authentication_analysis.md"
backup_and_remove "COMPLETE_MCP_IMPLEMENTATION_REPORT.md"
backup_and_remove "critical_fixes_2025_08_12.md"
backup_and_remove "FUTURE_MONITORING_DASHBOARD_PLAN.md"
backup_and_remove "google_drive_reauth_instructions.md"
backup_and_remove "gpt5_usage_guide.md"
backup_and_remove "HF_PRODUCTION_READY_SUMMARY.md"
backup_and_remove "imagen4_ultra_implementation.md"
backup_and_remove "IMPLEMENTATION_PROGRESS.md"
backup_and_remove "local_storage_implementation.md"
backup_and_remove "mcp_conversion_guide.md"
backup_and_remove "MCP_IMPLEMENTATION_SUMMARY.md"
backup_and_remove "MCP_PHASE_2_COMPLETION_REPORT.md"
backup_and_remove "MCP_PHASE_3_COMPLETION_REPORT.md"
backup_and_remove "NEXT_STEPS.md"
backup_and_remove "PRODUCTION_DEVELOPMENT_PLAN.md"
backup_and_remove "PROJECT_STATUS_SUMMARY.md"
backup_and_remove "REFACTORING_SUMMARY.md"
backup_and_remove "remotion_airtable_integration_complete.md"
backup_and_remove "REMOTION_ENHANCEMENTS_IMPLEMENTED.md"
backup_and_remove "remotion_implementation_analysis.md"
backup_and_remove "remotion_integration_complete.md"
backup_and_remove "REMOTION_MCP_AND_AGENT_GUIDE.md"
backup_and_remove "remotion_subagent_architecture.md"
backup_and_remove "REMOTION_VIDEO_ENHANCEMENT_PLAN.md"
backup_and_remove "remotion_vs_json2video_assessment.md"
backup_and_remove "remotion_wow_video_schema.md"
backup_and_remove "subagent_integration_assessment.md"
backup_and_remove "todo.md"
backup_and_remove "TOKEN_LIFECYCLE_MANAGER_GUIDE.md"
backup_and_remove "token_refresh_implementation.md"
backup_and_remove "weekly_cleanup_implementation.md"
backup_and_remove "workflow_improvements_2025_08_12.md"

echo "✅ Old documentation files cleaned"
echo ""

# === REMOVE OLD PYTHON SCRIPTS ===
echo "🗑️  Removing old/unused Python scripts..."

backup_and_remove "authenticate_google_drive.py"
backup_and_remove "complete_google_drive_auth.py"
backup_and_remove "reauth_google_drive.py"
backup_and_remove "refresh_google_drive_manual.py"
backup_and_remove "refresh_google_drive_token.py"
backup_and_remove "test_hf_api.py"
backup_and_remove "test_hf_final.py"
backup_and_remove "test_hf_inference_client.py"
backup_and_remove "test_fal_image_generation.py"

echo "✅ Old Python scripts cleaned"
echo ""

# === REMOVE TEST/TEMPORARY FILES ===
echo "🗑️  Removing test/temporary files..."

backup_and_remove "test_flux_image.jpg"
backup_and_remove "test_product_image.jpg"
backup_and_remove "hf_api_test_results.json"
backup_and_remove "hf_final_test_results.json"
backup_and_remove "hf_inference_test_results.json"

echo "✅ Test/temporary files cleaned"
echo ""

# === SUMMARY ===
echo "📊 Cleanup Summary:"
echo "  Backup location: $BACKUP_DIR"
echo "  Files backed up: $(ls -1 $BACKUP_DIR | wc -l)"
echo ""
echo "✅ Cleanup complete!"
echo ""
echo "💡 Kept files (used by new agent system):"
echo "  ✓ agents/ directory (all files)"
echo "  ✓ tests/ directory (all files)"
echo "  ✓ run_agent_workflow.py"
echo "  ✓ run_local_storage.py"
echo "  ✓ src/production_flow.py (for --legacy support)"
echo "  ✓ src/mcp/production_huggingface_client.py"
echo "  ✓ src/mcp/production_fal_image_generator.py"
echo "  ✓ src/mcp/production_text_generation_control_agent_mcp_v2.py"
echo "  ✓ src/mcp/production_instagram_reels_upload.py"
echo "  ✓ src/mcp/production_wordpress_local_media.py"
echo "  ✓ src/mcp/production_youtube_local_upload.py"
echo "  ✓ src/mcp/production_remotion_video_generator_strict.py"
echo "  ✓ src/mcp/production_wow_video_generator.py"
echo "  ✓ src/utils/circuit_breaker.py"
echo "  ✓ MCP Servers (6 active):"
echo "    - production_amazon_scraper_mcp_server.py"
echo "    - production_remotion_wow_video_mcp_server.py"
echo "    - production_content_generation_mcp_server.py"
echo "    - production_voice_generation_mcp_server.py"
echo "    - production_quality_assurance_mcp_server.py"
echo "    - production_analytics_mcp_server.py"
echo "  ✓ Documentation (new):"
echo "    - AGENT_IMPLEMENTATION_COMPLETE.md"
echo "    - AGENT_SYSTEM_DOCUMENTATION.md"
echo "    - QUICK_START_AGENT_SYSTEM.md"
echo "    - readme.md"
echo "    - COMPLETE_SYSTEM_INVENTORY.md"
echo "    - HETZNER_SERVER_ANALYSIS.md"
echo ""
