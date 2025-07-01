#!/bin/bash
echo "🚀 Starting Claude Workflow with all fixes applied"
echo "Timestamp: $(date)"
echo "=" * 50

cd /home/claude-workflow

# Ensure we're using the right Python path
export PYTHONPATH=/home/claude-workflow/src:$PYTHONPATH

# Run with detailed output
python3 -u src/workflow_runner.py 2>&1 | tee -a workflow_$(date +%Y%m%d_%H%M%S).log

echo ""
echo "✅ Workflow complete. Check the log file for details."
