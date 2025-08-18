#!/bin/bash
# Setup script for local storage workflow

echo "========================================="
echo "Setting up Local Storage Workflow"
echo "========================================="

# Create directory structure
echo "📁 Creating local storage directories..."
mkdir -p /home/claude-workflow/media_storage/{audio,images,videos}
mkdir -p /home/claude-workflow/media_storage/$(date +%Y-%m-%d)/{audio,images,videos}

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x /home/claude-workflow/run_local_storage.py
chmod +x /home/claude-workflow/cleanup_local_storage.py

# Test cleanup script (dry run)
echo "🧪 Testing cleanup script (dry run)..."
python3 /home/claude-workflow/cleanup_local_storage.py --dry-run --days 7

# Setup cron job for daily cleanup (optional)
echo ""
echo "📅 To setup automatic daily cleanup, add this to crontab:"
echo "   0 3 * * * /usr/bin/python3 /home/claude-workflow/cleanup_local_storage.py --days 7"
echo ""
echo "Run: crontab -e"
echo "And add the line above to run cleanup at 3 AM daily"

echo ""
echo "✅ Setup complete!"
echo ""
echo "To run the workflow:"
echo "   python3 /home/claude-workflow/run_local_storage.py"
echo ""
echo "To manually cleanup old files:"
echo "   python3 /home/claude-workflow/cleanup_local_storage.py --days 7"
echo ""
echo "To test cleanup without deleting (dry run):"
echo "   python3 /home/claude-workflow/cleanup_local_storage.py --dry-run --days 7"
echo ""