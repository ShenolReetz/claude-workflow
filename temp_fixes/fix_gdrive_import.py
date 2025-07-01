with open('src/workflow_runner.py', 'r') as f:
    content = f.read()

# Fix the import statement
content = content.replace(
    'from mcp.google_drive_agent_mcp import upload_video_to_google_drive',
    'from mcp.google_drive_agent_mcp import GoogleDriveAgent'
)

# Also fix any calls to upload_video_to_google_drive
# Replace function calls with class method calls
import re

# Pattern to find upload_video_to_google_drive calls
pattern = r'await upload_video_to_google_drive\((.*?)\)'
replacement = r'await self.google_drive_agent.upload_video_to_drive(\1)'

# Apply the replacement
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Write back
with open('src/workflow_runner.py', 'w') as f:
    f.write(content)

print("✅ Fixed Google Drive imports")
