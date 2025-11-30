#!/bin/bash
#
# Weekly Complete Cleanup Wrapper Script
# Runs complete cleanup every Sunday at 07:00
# Deletes ALL files in media storage
#

LOG_FILE="/home/claude-workflow/cleanup_cron.log"
echo "========================================" >> $LOG_FILE
echo "WEEKLY COMPLETE CLEANUP started at $(date)" >> $LOG_FILE
echo "Action: DELETE ALL FILES" >> $LOG_FILE
echo "========================================" >> $LOG_FILE

# Run COMPLETE cleanup (deletes everything)
cd /home/claude-workflow
/usr/bin/python3 /home/claude-workflow/cleanup_all_storage.py >> $LOG_FILE 2>&1

# Check exit status
if [ $? -eq 0 ]; then
    echo "✅ Cleanup completed successfully at $(date)" >> $LOG_FILE
else
    echo "❌ Cleanup failed at $(date)" >> $LOG_FILE
fi

echo "" >> $LOG_FILE
