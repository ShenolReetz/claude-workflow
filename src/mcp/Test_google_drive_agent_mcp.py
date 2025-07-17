import asyncio
from typing import Dict, Optional
import logging
import httpx
import io

logger = logging.getLogger(__name__)

# Import the Google Drive server
import sys
sys.path.append('/home/claude-workflow')
from mcp_servers.Test_google_drive_server import GoogleDriveMCPServer

class GoogleDriveAgentMCP:
    """Controls the Google Drive upload workflow"""
    
    def __init__(self, config: dict):
        self.config = config
        self.drive_server = GoogleDriveMCPServer(config)
        

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
            async with httpx.AsyncClient(timeout=86400) as client:
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
    async def create_project_folder_structure(self, n8n_folder_name: str, project_folder_name: str, include_affiliate_photos: bool = False) -> Dict:
        """Create the folder structure: /N8N Projects/[Project Name]/Affiliate Photos/"""
        try:
            service = await self.initialize()
            
            # Find or create N8N Projects folder
            n8n_query = f"name='{n8n_folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            n8n_results = service.files().list(q=n8n_query, fields="files(id, name)").execute()
            n8n_items = n8n_results.get('files', [])
            
            if n8n_items:
                n8n_folder_id = n8n_items[0]['id']
            else:
                n8n_folder_metadata = {
                    'name': n8n_folder_name,
                    'mimeType': 'application/vnd.google-apps.folder'
                }
                n8n_folder = service.files().create(body=n8n_folder_metadata, fields='id').execute()
                n8n_folder_id = n8n_folder.get('id')
                logger.info(f"📁 Created folder: {n8n_folder_name}")
            
            # Create project folder
            project_folder_name_clean = self._clean_folder_name(project_folder_name)
            project_query = f"name='{project_folder_name_clean}' and '{n8n_folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
            project_results = service.files().list(q=project_query, fields="files(id, name)").execute()
            project_items = project_results.get('files', [])
            
            if project_items:
                project_folder_id = project_items[0]['id']
            else:
                project_folder_metadata = {
                    'name': project_folder_name_clean,
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': [n8n_folder_id]
                }
                project_folder = service.files().create(body=project_folder_metadata, fields='id').execute()
                project_folder_id = project_folder.get('id')
                logger.info(f"📁 Created folder: {project_folder_name_clean}")
            
            result = {
                'n8n_folder_id': n8n_folder_id,
                'project_folder_id': project_folder_id
            }
            
            if include_affiliate_photos:
                # Create Affiliate Photos subfolder
                affiliate_query = f"name='Affiliate Photos' and '{project_folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
                affiliate_results = service.files().list(q=affiliate_query, fields="files(id, name)").execute()
                affiliate_items = affiliate_results.get('files', [])
                
                if affiliate_items:
                    affiliate_folder_id = affiliate_items[0]['id']
                else:
                    affiliate_folder_metadata = {
                        'name': 'Affiliate Photos',
                        'mimeType': 'application/vnd.google-apps.folder',
                        'parents': [project_folder_id]
                    }
                    affiliate_folder = service.files().create(body=affiliate_folder_metadata, fields='id').execute()
                    affiliate_folder_id = affiliate_folder.get('id')
                    logger.info(f"📁 Created folder: Affiliate Photos")
                
                result['affiliate_photos_folder_id'] = affiliate_folder_id
            
            logger.info(f"✅ Created: /{n8n_folder_name}/{project_folder_name_clean}/Affiliate Photos/")
            return result
            
        except Exception as e:
            logger.error(f"Error creating folder structure: {str(e)}")
            raise
    
    async def upload_file(self, file_content: bytes, filename: str, folder_id: str, mime_type: str = 'image/jpeg') -> Dict:
        """Upload a file to Google Drive"""
        try:
            service = await self.initialize()
            
            # Create file metadata
            file_metadata = {
                'name': filename,
                'parents': [folder_id]
            }
            
            # Upload file
            from googleapiclient.http import MediaInMemoryUpload
            media = MediaInMemoryUpload(file_content, mimetype=mime_type)
            
            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,webViewLink'
            ).execute()
            
            logger.info(f"✅ Uploaded file: {filename}")
            return file
            
        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            return None
