#!/usr/bin/env python3
"""
Fix Google Drive upload to use video URL instead of record_id
"""

# Read the file
with open('/home/claude-workflow/src/workflow_runner.py', 'r') as f:
    content = f.read()

# The issue is we're passing record_id twice - should be config, record_id, video_url
# Find and fix the upload call
import re

# Pattern to find the upload call
pattern = r"upload_result = await upload_video_to_google_drive\(\s*self\.config,\s*pending_title\['record_id'\],\s*video_result\['video_url'\],\s*pending_title\['record_id'\]\s*\)"

# Check if this pattern exists
if re.search(pattern, content):
    # Remove the duplicate record_id
    replacement = """upload_result = await upload_video_to_google_drive(
                self.config,
                pending_title['record_id'],
                video_result['video_url']
            )"""
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    print("✅ Fixed Google Drive upload call")
else:
    print("Pattern not found, checking current state...")

# Write back
with open('/home/claude-workflow/src/workflow_runner.py', 'w') as f:
    f.write(content)
