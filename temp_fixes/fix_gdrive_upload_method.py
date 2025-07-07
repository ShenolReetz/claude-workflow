#!/usr/bin/env python3
"""
This script adds the missing upload_video_to_drive method to GoogleDriveAgent
"""

import re
import os

# Read the current google_drive_agent_mcp.py
with open('src/mcp/google_drive_agent_mcp.py', 'r') as f:
    content = f.read()

# Method to add
new_method = """
    async def upload_video_to_drive(self, video_url: str, title: str) -> str:
        \"\"\"
        Upload video to Google Drive
        
        Args:
            video_url: URL of the video to upload
            title: Title for the video file
            
        Returns:
            Google Drive URL of the uploaded video
        \"\"\"
        try:
            # Download video from URL first
            import httpx
            import tempfile
            
            # Create temp file for video
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp_file:
                temp_path = tmp_file.name
                
            # Download video
            async with httpx.AsyncClient() as client:
                response = await client.get(video_url, follow_redirects=True)
                response.raise_for_status()
                
                with open(temp_path, 'wb') as f:
                    f.write(response.content)
            
            # Upload to Google Drive
            from googleapiclient.http import MediaFileUpload
            
            # Sanitize filename
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{safe_title}.mp4"
            
            # Get or create Video folder
            video_folder_id = await self._get_or_create_folder('Video')
            
            # Upload file
            file_metadata = {
                'name': filename,
                'parents': [video_folder_id]
            }
            
            media = MediaFileUpload(temp_path, mimetype='video/mp4', resumable=True)
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,webViewLink'
            ).execute()
            
            # Clean up temp file
            os.unlink(temp_path)
            
            gdrive_url = file.get('webViewLink', '')
            logger.info(f"✅ Video uploaded to Google Drive: {gdrive_url}")
            
            return gdrive_url
            
        except Exception as e:
            logger.error(f"Failed to upload video to Google Drive: {e}")
            raise

    async def _get_or_create_folder(self, folder_name: str, parent_id: str = None) -> str:
        \"\"\"
        Get or create a folder in Google Drive
        
        Args:
            folder_name: Name of the folder
            parent_id: Parent folder ID (optional)
            
        Returns:
            Folder ID
        \"\"\"
        try:
            # Search for existing folder
            query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            if parent_id:
                query += f" and '{parent_id}' in parents"
                
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)'
            ).execute()
            
            items = results.get('files', [])
            
            if items:
                # Folder exists
                return items[0]['id']
            else:
                # Create folder
                file_metadata = {
                    'name': folder_name,
                    'mimeType': 'application/vnd.google-apps.folder'
                }
                if parent_id:
                    file_metadata['parents'] = [parent_id]
                    
                folder = self.service.files().create(
                    body=file_metadata,
                    fields='id'
                ).execute()
                
                logger.info(f"📁 Created folder: {folder_name}")
                return folder.get('id')
                
        except Exception as e:
            logger.error(f"Error managing folder {folder_name}: {e}")
            raise
"""

# Find the last method in the GoogleDriveAgent class
# We'll insert the new method before the run_google_drive_upload function
insertion_point = "async def run_google_drive_upload"

if insertion_point in content:
    # Split the content at the insertion point
    parts = content.split(insertion_point)
    
    # Insert the new method before the run function
    updated_content = parts[0] + new_method + "\n\n" + insertion_point + parts[1]
    
    # Write the updated content
    with open('src/mcp/google_drive_agent_mcp.py', 'w') as f:
        f.write(updated_content)
    
    print("✅ Added upload_video_to_drive method to GoogleDriveAgent")
else:
    print("❌ Could not find insertion point in GoogleDriveAgent")
    print("Trying alternate approach...")
    
    # Try to find the class definition and add at the end
    class_match = re.search(r'(class GoogleDriveAgent.*?:.*?)(\n\nclass|\n\nasync def run_|\Z)', content, re.DOTALL)
    if class_match:
        # Insert before the next class or function
        updated_content = content[:class_match.end(1)] + new_method + content[class_match.end(1):]
        
        with open('src/mcp/google_drive_agent_mcp.py', 'w') as f:
            f.write(updated_content)
        
        print("✅ Added upload_video_to_drive method to GoogleDriveAgent (alternate method)")
    else:
        print("❌ Failed to patch. Please add the method manually.")
