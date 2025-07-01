#!/usr/bin/env python3
"""
Fix the GoogleDriveAgent class structure
"""

import re

# Read the current file
with open('src/mcp/google_drive_agent_mcp.py', 'r') as f:
    content = f.read()

# Clean up duplicate methods and fix structure
fixed_content = '''import os
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import httpx
import tempfile

logger = logging.getLogger(__name__)

# Add the path to the project root
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from mcp_servers.airtable_server import AirtableMCPServer

class GoogleDriveAgent:
    """
    Google Drive agent for uploading videos
    """
    
    def __init__(self, credentials_path: str = 'config/google_drive_credentials.json'):
        self.credentials_path = credentials_path
        self.service = None
        logger.info("✅ Google Drive Agent initialized")
        
    def _initialize_service(self):
        """Initialize Google Drive service with credentials"""
        try:
            # Check if credentials file exists
            if not os.path.exists(self.credentials_path):
                logger.error(f"❌ Credentials file not found: {self.credentials_path}")
                raise FileNotFoundError(f"Credentials file not found: {self.credentials_path}")
                
            # Load service account credentials
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=['https://www.googleapis.com/auth/drive.file']
            )
            
            logger.info("✅ Using service account credentials")
            
            # Build the service
            self.service = build('drive', 'v3', credentials=credentials)
            logger.info("✅ Google Drive service initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Google Drive service: {e}")
            raise
            
    async def upload_video_to_drive(self, video_url: str, title: str) -> str:
        """
        Upload video to Google Drive
        
        Args:
            video_url: URL of the video to upload
            title: Title for the video file
            
        Returns:
            Google Drive URL of the uploaded video
        """
        try:
            # Initialize service if not already done
            if not self.service:
                self._initialize_service()
                
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
        """
        Get or create a folder in Google Drive
        
        Args:
            folder_name: Name of the folder
            parent_id: Parent folder ID (optional)
            
        Returns:
            Folder ID
        """
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


# Helper function for workflow runner
async def upload_video_to_google_drive(config, video_url, video_title, record_id=None):
    """
    Helper function to upload video to Google Drive
    
    Args:
        config: Configuration dictionary
        video_url: URL of the video to upload
        video_title: Title for the video
        record_id: Airtable record ID (optional)
        
    Returns:
        Dictionary with upload results
    """
    try:
        # Create GoogleDriveAgent instance
        gdrive_agent = GoogleDriveAgent(
            credentials_path=config.get('google_drive_credentials', 'config/google_drive_credentials.json')
        )
        
        # Upload video
        gdrive_url = await gdrive_agent.upload_video_to_drive(video_url, video_title)
        
        # Update Airtable if record_id provided
        if record_id and gdrive_url:
            airtable_config = {
                'api_key': config['airtable_api_key'],
                'base_id': config['airtable_base_id'],
                'table_name': config['airtable_table_name']
            }
            
            airtable_server = AirtableMCPServer(
                api_key=airtable_config['api_key'],
                base_id=airtable_config['base_id']
            )
            
            await airtable_server.update_record(
                table_name=airtable_config['table_name'],
                record_id=record_id,
                fields={'GoogleDriveURL': gdrive_url}
            )
            
            logger.info(f"✅ Updated Airtable record {record_id} with Google Drive URL")
        
        return {
            'success': True,
            'gdrive_url': gdrive_url,
            'record_id': record_id
        }
        
    except Exception as e:
        logger.error(f"Failed to upload video to Google Drive: {e}")
        return {
            'success': False,
            'error': str(e),
            'record_id': record_id
        }
'''

# Write the fixed content
with open('src/mcp/google_drive_agent_mcp.py', 'w') as f:
    f.write(fixed_content)

print("✅ Fixed GoogleDriveAgent class structure")
print("✅ Removed duplicate methods")
print("✅ Properly indented all methods within the class")
print("✅ Added initialization check in upload_video_to_drive")
