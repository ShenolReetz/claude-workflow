import asyncio
from typing import Dict, Optional
import logging
import httpx
import io

logger = logging.getLogger(__name__)

# Import the Google Drive server
import sys
sys.path.append('/home/claude-workflow')
from mcp_servers.google_drive_server import GoogleDriveMCPServer

class GoogleDriveAgentMCP:
    """Controls the Google Drive upload workflow"""
    
    def __init__(self, config: dict):
        self.config = config
        self.drive_server = GoogleDriveMCPServer('/home/claude-workflow/config/google_drive_credentials.json')
        

    def _clean_folder_name(self, name: str) -> str:
        """Clean folder name for Google Drive"""
        # Remove problematic characters
        cleaned = name.replace("'", "")
        cleaned = cleaned.replace('"', "")
        cleaned = cleaned.replace("\\", "")
        cleaned = cleaned.replace("/", "-")
        # Limit length
        return cleaned[:60]

    async def initialize(self):
        """Initialize the Google Drive service"""
        return await self.drive_server.initialize_drive_service()
    
    async def upload_video_to_drive(self, video_url: str, video_title: str, record_id: str) -> Dict:
        """Download video from JSON2Video and upload to Google Drive"""
        try:
            logger.info(f"📥 Downloading video from: {video_url}")
            
            # Download the video
            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.get(video_url)
                if response.status_code != 200:
                    raise Exception(f"Failed to download video: {response.status_code}")
                
                video_data = response.content
            
            logger.info(f"✅ Downloaded video ({len(video_data) / 1024 / 1024:.2f} MB)")
            
            # Create project structure in Google Drive
            folder_ids = await self.drive_server.create_project_structure(video_title)
            if not folder_ids.get('video'):
                raise Exception("Failed to create video folder")
            
            # Upload video to Google Drive
            logger.info(f"📤 Uploading video to Google Drive...")
            
            # Create a file-like object from the video data
            video_stream = io.BytesIO(video_data)
            
            # Upload using the service directly (we need to add this method)
            file_metadata = {
                'name': f"{video_title}.mp4",
                'parents': [folder_ids['video']]
            }
            
            from googleapiclient.http import MediaIoBaseUpload
            media = MediaIoBaseUpload(
                video_stream,
                mimetype='video/mp4',
                resumable=True
            )
            
            file = self.drive_server.service.files().create(
                body=file_metadata,
                media_body=media
            ).execute()
            
            # Make it publicly accessible
            file_id = file.get('id')
            self.drive_server.service.permissions().create(
                fileId=file_id,
                body={'role': 'reader', 'type': 'anyone'}
            ).execute()
            
            # Get the shareable link
            file_info = self.drive_server.service.files().get(
                fileId=file_id, 
                fields='webViewLink'
            ).execute()
            
            drive_url = file_info.get('webViewLink')
            
            logger.info(f"✅ Video uploaded to Google Drive: {drive_url}")
            
            return {
                'success': True,
                'drive_url': drive_url,
                'folder_ids': folder_ids,
                'file_id': file_id
            }
            
        except Exception as e:
            logger.error(f"❌ Error uploading video to Google Drive: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

# Integration function
async def upload_video_to_google_drive(config: Dict, video_url: str, video_title: str, record_id: str) -> Dict:
    """Upload video to Google Drive"""
    agent = GoogleDriveAgentMCP(config)
    
    # Initialize Google Drive service
    if not await agent.initialize():
        return {
            'success': False,
            'error': 'Failed to initialize Google Drive service'
        }
    
    # Upload the video
    return await agent.upload_video_to_drive(video_url, video_title, record_id)
