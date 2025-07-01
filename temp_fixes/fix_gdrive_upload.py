#!/usr/bin/env python3
"""
Fix Google Drive upload arguments
"""

# Read the file
with open('/home/claude-workflow/src/workflow_runner.py', 'r') as f:
    content = f.read()

# Fix the upload call - it needs record_id as a separate argument
old_call = """upload_result = await upload_video_to_google_drive(
                self.config,
                pending_title['record_id'],
                video_result['video_url']
            )"""

new_call = """upload_result = await upload_video_to_google_drive(
                self.config,
                pending_title['record_id'],
                video_result['video_url'],
                pending_title['record_id']  # Add record_id as 4th argument
            )"""

# Try another pattern if the first doesn't match
if old_call not in content:
    # Find and fix by regex
    import re
    pattern = r"upload_result = await upload_video_to_google_drive\(\s*self\.config,\s*pending_title\['record_id'\],\s*video_result\['video_url'\]\s*\)"
    replacement = "upload_result = await upload_video_to_google_drive(\n                self.config,\n                pending_title['record_id'],\n                video_result['video_url'],\n                pending_title['record_id']\n            )"
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
else:
    content = content.replace(old_call, new_call)

# Write back
with open('/home/claude-workflow/src/workflow_runner.py', 'w') as f:
    f.write(content)

print("✅ Fixed Google Drive upload arguments")
