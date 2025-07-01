#!/bin/bash
echo "🚀 Starting Claude Workflow with fixes applied"
echo "Timestamp: $(date)"
echo "=" * 50

cd /home/claude-workflow
python3 src/workflow_runner.py 2>&1 | tee -a workflow_$(date +%Y%m%d_%H%M%S).log

echo ""
echo "✅ Workflow complete. Check the log file for details."
