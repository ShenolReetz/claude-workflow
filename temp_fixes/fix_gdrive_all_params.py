#!/usr/bin/env python3
"""
Fix all parameters in upload_video_to_drive method
"""

# Read the current file
with open('src/mcp/google_drive_agent_mcp.py', 'r') as f:
    content = f.read()

# Find and replace the method signature to accept parent_folder_name
old_signature = 'async def upload_video_to_drive(self, video_url: str, video_title: str) -> str:'
new_signature = 'async def upload_video_to_drive(self, video_url: str, video_title: str, parent_folder_name: str = None) -> str:'

content = content.replace(old_signature, new_signature)

# Update the docstring to include the new parameter
old_docstring = '''        """
        Upload video to Google Drive
        
        Args:
            video_url: URL of the video to upload
            video_title: Title for the video file
            
        Returns:
            Google Drive URL of the uploaded video
        """'''

new_docstring = '''        """
        Upload video to Google Drive
        
        Args:
            video_url: URL of the video to upload
            video_title: Title for the video file
            parent_folder_name: Name of parent folder (optional, defaults to 'Video')
            
        Returns:
            Google Drive URL of the uploaded video
        """'''

content = content.replace(old_docstring, new_docstring)

# Update the folder logic to use parent_folder_name if provided
content = content.replace(
    "video_folder_id = await self._get_or_create_folder('Video')",
    "video_folder_id = await self._get_or_create_folder(parent_folder_name or 'Video')"
)

# Write the fixed content
with open('src/mcp/google_drive_agent_mcp.py', 'w') as f:
    f.write(content)

print("✅ Fixed method signature to accept parent_folder_name parameter")
print("✅ Updated folder logic to use parent_folder_name when provided")
