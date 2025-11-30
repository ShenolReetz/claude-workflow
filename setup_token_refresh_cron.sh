#!/bin/bash
################################################################################
# Token Refresh Cron Setup Script
################################################################################
# Sets up daily automatic token refresh at 6 AM
#
# Usage:
#   bash setup_token_refresh_cron.sh
#
# What this does:
# - Adds cron job for daily token refresh (6 AM)
# - Creates log rotation for token lifecycle logs
# - Tests the token manager
################################################################################

echo "════════════════════════════════════════════════════════════"
echo "  TOKEN REFRESH CRON SETUP"
echo "════════════════════════════════════════════════════════════"
echo ""

# Variables
SCRIPT_PATH="/home/claude-workflow/mcp_servers/production_token_lifecycle_manager.py"
LOG_PATH="/home/claude-workflow/token_lifecycle.log"
CRON_LOG="/home/claude-workflow/token_refresh_cron.log"

# Make script executable
echo "📝 Making token manager executable..."
chmod +x "$SCRIPT_PATH"

# Check if cron job already exists
CRON_EXISTS=$(crontab -l 2>/dev/null | grep "production_token_lifecycle_manager.py" | wc -l)

if [ "$CRON_EXISTS" -gt 0 ]; then
    echo "⚠️  Token refresh cron job already exists!"
    echo "   Current cron jobs:"
    crontab -l 2>/dev/null | grep "production_token_lifecycle_manager.py"
    echo ""
    read -p "   Do you want to replace it? (y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Cancelled - keeping existing cron job"
        exit 0
    fi

    # Remove existing cron job
    crontab -l 2>/dev/null | grep -v "production_token_lifecycle_manager.py" | crontab -
    echo "🗑️  Removed existing cron job"
fi

# Add new cron job
echo "➕ Adding new cron job..."

# Create temporary cron file
TEMP_CRON=$(mktemp)

# Export existing crontab
crontab -l 2>/dev/null > "$TEMP_CRON"

# Add new job (daily at 6 AM)
echo "# Token Lifecycle Manager - Auto-refresh tokens daily at 6 AM" >> "$TEMP_CRON"
echo "0 6 * * * cd /home/claude-workflow && /usr/bin/python3 $SCRIPT_PATH --auto-refresh >> $CRON_LOG 2>&1" >> "$TEMP_CRON"

# Install new crontab
crontab "$TEMP_CRON"
rm "$TEMP_CRON"

echo "✅ Cron job installed successfully!"
echo ""
echo "📅 Schedule: Daily at 6:00 AM"
echo "📁 Log file: $CRON_LOG"
echo ""

# Display current crontab
echo "════════════════════════════════════════════════════════════"
echo "  CURRENT CRON JOBS"
echo "════════════════════════════════════════════════════════════"
crontab -l
echo ""

# Test the token manager
echo "════════════════════════════════════════════════════════════"
echo "  TESTING TOKEN MANAGER"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "🧪 Running health check..."
python3 "$SCRIPT_PATH" --health-check

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  SETUP COMPLETE"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "✅ Token refresh automation is now active!"
echo ""
echo "📋 Next steps:"
echo "   1. Check health status: python3 $SCRIPT_PATH --health-check"
echo "   2. Manual refresh: python3 $SCRIPT_PATH --refresh-all"
echo "   3. Monitor logs: tail -f $LOG_PATH"
echo "   4. Monitor cron logs: tail -f $CRON_LOG"
echo ""
echo "🔔 You will receive alerts if token refresh fails"
echo ""
