#!/bin/bash
#
# Setup Weekly Cleanup Cron Job
# ==============================
# This script sets up a cron job to run the cleanup script weekly
#

echo "╔══════════════════════════════════════════════╗"
echo "║   SETUP WEEKLY CLEANUP CRON JOB              ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# Define the cleanup command
CLEANUP_CMD="cd /home/claude-workflow && /usr/bin/python3 /home/claude-workflow/cleanup_local_storage.py --days 7"

# Define cron schedule (every Sunday at 7 AM)
CRON_SCHEDULE="0 7 * * 0"

# Create a wrapper script for better logging
WRAPPER_SCRIPT="/home/claude-workflow/run_cleanup.sh"

cat > $WRAPPER_SCRIPT << 'EOF'
#!/bin/bash
#
# Cleanup Wrapper Script
# Runs cleanup and logs output
#

LOG_FILE="/home/claude-workflow/cleanup_cron.log"
echo "========================================" >> $LOG_FILE
echo "Cleanup started at $(date)" >> $LOG_FILE
echo "========================================" >> $LOG_FILE

# Run cleanup
cd /home/claude-workflow
/usr/bin/python3 /home/claude-workflow/cleanup_local_storage.py --days 7 >> $LOG_FILE 2>&1

# Check exit status
if [ $? -eq 0 ]; then
    echo "✅ Cleanup completed successfully at $(date)" >> $LOG_FILE
else
    echo "❌ Cleanup failed at $(date)" >> $LOG_FILE
fi

echo "" >> $LOG_FILE
EOF

# Make wrapper script executable
chmod +x $WRAPPER_SCRIPT

# Check if cron job already exists
crontab -l 2>/dev/null | grep -q "run_cleanup.sh"
if [ $? -eq 0 ]; then
    echo "⚠️  Cron job already exists. Removing old entry..."
    # Remove existing entry
    crontab -l 2>/dev/null | grep -v "run_cleanup.sh" | crontab -
fi

# Add new cron job
(crontab -l 2>/dev/null; echo "$CRON_SCHEDULE $WRAPPER_SCRIPT") | crontab -

echo "✅ Cron job installed successfully!"
echo ""
echo "📅 Schedule: Every Sunday at 07:00 (7:00 AM)"
echo "📝 Log file: /home/claude-workflow/cleanup_cron.log"
echo ""
echo "Current cron jobs:"
crontab -l

echo ""
echo "To test the cleanup script manually, run:"
echo "  python3 /home/claude-workflow/cleanup_local_storage.py --dry-run"
echo ""
echo "To remove the cron job, run:"
echo "  crontab -l | grep -v 'run_cleanup.sh' | crontab -"
echo ""
echo "To view cleanup logs:"
echo "  tail -f /home/claude-workflow/cleanup_cron.log"