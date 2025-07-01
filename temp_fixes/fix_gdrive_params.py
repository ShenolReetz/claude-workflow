#!/usr/bin/env python3
"""
Fix the parameter name in upload_video_to_drive method
"""

# Read the current file
with open('src/mcp/google_drive_agent_mcp.py', 'r') as f:
    content = f.read()

# Fix the parameter name from 'title' to 'video_title'
content = content.replace(
    'async def upload_video_to_drive(self, video_url: str, title: str) -> str:',
    'async def upload_video_to_drive(self, video_url: str, video_title: str) -> str:'
)

# Also fix the usage of 'title' to 'video_title' inside the method
content = content.replace(
    'safe_title = "".join(c for c in title if c.isalnum()',
    'safe_title = "".join(c for c in video_title if c.isalnum()'
)

# Write the fixed content
with open('src/mcp/google_drive_agent_mcp.py', 'w') as f:
    f.write(content)

print("✅ Fixed parameter name from 'title' to 'video_title'")
