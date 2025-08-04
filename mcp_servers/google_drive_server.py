import asyncio
import json
import io
import base64
import os
from typing import Dict, List, Optional
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

class GoogleDriveMCPServer:
    def __init__(self, config: Dict):
        self.config = config
        self.service = None
        self.parent_folder_id = None
        self.use_oauth = config.get('google_drive_token') is not None
    
    def sanitize_folder_name(self, name: str) -> str:
        """Sanitize folder name for Google Drive compatibility"""
        import re
        import unicodedata
        
        # Remove emojis and special unicode characters (including emoji symbols)
        # This removes all characters in the Symbol category (which includes emojis)
        name = ''.join(char for char in name if unicodedata.category(char)[0] not in ['S', 'C'])
        
        # Replace problematic characters with safe alternatives
        name = re.sub(r'[<>:"/\\|?*$]', '', name)  # Remove illegal characters including $
        name = re.sub(r"[()!']", '', name)  # Remove parentheses, exclamation marks, and apostrophes
        name = re.sub(r'\s+', ' ', name)  # Replace multiple spaces with single space
        name = name.strip()  # Remove leading/trailing spaces
        
        # Ensure name is not empty after sanitization
        if not name:
            name = "Untitled_Project"
        
        # Limit length to avoid issues
        if len(name) > 50:
            name = name[:47] + "..."
        
        return name
        
    async def initialize_drive_service(self):
        """Initialize Google Drive service with OAuth2 or service account credentials"""
        try:
            if self.use_oauth:
                # Use improved token manager for automatic refresh
                import sys
                sys.path.append('/home/claude-workflow')
                from src.utils.google_drive_token_manager import GoogleDriveTokenManager
                
                token_manager = GoogleDriveTokenManager()
                creds = token_manager.get_valid_credentials()
                
                if not creds:
                    print("❌ Could not obtain valid Google Drive credentials")
                    print("   Token may have expired and requires manual re-authorization")
                    print("   Workflow will continue without Google Drive integration")
                    return False
                
                self.service = build('drive', 'v3', credentials=creds)
                print("✅ Google Drive service initialized with automatic token management")
            else:
                # Fallback to service account (for folder operations only)
                from google.oauth2.service_account import Credentials as ServiceAccountCredentials
                creds_path = self.config.get('google_drive_credentials')
                
                creds = ServiceAccountCredentials.from_service_account_file(
                    creds_path,
                    scopes=['https://www.googleapis.com/auth/drive']
                )
                self.service = build('drive', 'v3', credentials=creds)
                print("⚠️  Google Drive service initialized with service account")
                print("   Note: File uploads will fail due to storage quota limits")
            
            return True
        except Exception as e:
            print(f"❌ Error initializing Google Drive: {e}")
            return False
    
    async def find_or_create_folder(self, folder_name: str, parent_id: str = None) -> Optional[str]:
        """Find existing folder or create new one"""
        try:
            query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
            if parent_id:
                query += f" and '{parent_id}' in parents"
            
            results = self.service.files().list(q=query).execute()
            items = results.get('files', [])
            
            if items:
                print(f"📁 Found existing folder: {folder_name}")
                return items[0]['id']
            
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            if parent_id:
                folder_metadata['parents'] = [parent_id]
            
            folder = self.service.files().create(body=folder_metadata).execute()
            print(f"📁 Created new folder: {folder_name}")
            return folder.get('id')
            
        except Exception as e:
            print(f"❌ Error with folder {folder_name}: {e}")
            return None
    
    async def create_project_structure(self, video_title: str) -> Dict[str, str]:
        """Create complete project folder structure"""
        try:
            folder_ids = {}
            
            if not self.parent_folder_id:
                self.parent_folder_id = await self.find_or_create_folder("N8N Projects")
                if not self.parent_folder_id:
                    return {}
            
            # Sanitize video title for Google Drive compatibility
            safe_title = self.sanitize_folder_name(video_title)
            print(f"📁 Sanitized folder name: '{video_title}' → '{safe_title}'")
            
            video_folder_id = await self.find_or_create_folder(safe_title, self.parent_folder_id)
            if not video_folder_id:
                return {}
            folder_ids['project'] = video_folder_id
            
            subfolders = ['Video', 'Photos', 'Audio']
            for subfolder in subfolders:
                subfolder_id = await self.find_or_create_folder(subfolder, video_folder_id)
                if subfolder_id:
                    folder_ids[subfolder.lower()] = subfolder_id
            
            print(f"✅ Created project structure for: {safe_title}")
            return folder_ids
            
        except Exception as e:
            print(f"❌ Error creating project structure: {e}")
            return {}
    
    async def upload_audio_file(self, audio_base64: str, filename: str, folder_id: str) -> Optional[str]:
        """Upload audio file from base64 data"""
        if not self.use_oauth:
            print("❌ Cannot upload files with service account (no storage quota)")
            print("   Please run setup_google_drive_oauth.py to enable file uploads")
            return None
            
        try:
            audio_data = base64.b64decode(audio_base64)
            audio_stream = io.BytesIO(audio_data)
            
            file_metadata = {
                'name': filename,
                'parents': [folder_id]
            }
            
            media = MediaIoBaseUpload(
                audio_stream,
                mimetype='audio/mpeg',
                resumable=True
            )
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media
            ).execute()
            
            file_id = file.get('id')
            self.service.permissions().create(
                fileId=file_id,
                body={'role': 'reader', 'type': 'anyone'}
            ).execute()
            
            file_info = self.service.files().get(fileId=file_id, fields='webViewLink,webContentLink').execute()
            # Use webContentLink for direct download (better for audio files)
            link = file_info.get('webContentLink')
            
            print(f"✅ Uploaded audio: {filename}")
            print(f"   Link: {link}")
            return link
            
        except Exception as e:
            print(f"❌ Error uploading audio {filename}: {e}")
            return None

    async def upload_video_file(self, video_path: str, filename: str, folder_id: str) -> Optional[str]:
        """Upload video file from local path"""
        if not self.use_oauth:
            print("❌ Cannot upload files with service account (no storage quota)")
            print("   Please run setup_google_drive_oauth.py to enable file uploads")
            return None
            
        try:
            file_metadata = {
                'name': filename,
                'parents': [folder_id]
            }
            
            media = MediaIoBaseUpload(
                open(video_path, 'rb'),
                mimetype='video/mp4',
                resumable=True
            )
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media
            ).execute()
            
            file_id = file.get('id')
            self.service.permissions().create(
                fileId=file_id,
                body={'role': 'reader', 'type': 'anyone'}
            ).execute()
            
            file_info = self.service.files().get(fileId=file_id, fields='webViewLink').execute()
            link = file_info.get('webViewLink')
            
            print(f"✅ Uploaded video: {filename}")
            print(f"   Link: {link}")
            return link
            
        except Exception as e:
            print(f"❌ Error uploading video {filename}: {e}")
            return None

async def test_google_drive():
    """Test Google Drive with OAuth2"""
    print("🧪 Testing Google Drive OAuth2 Integration")
    
    # Load config
    with open('config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    # Create server instance
    server = GoogleDriveMCPServer(config)
    
    # Initialize service
    if await server.initialize_drive_service():
        print("✅ OAuth2 authentication successful")
        
        # Test folder creation
        test_folder_id = await server.find_or_create_folder("OAuth2 Test Folder")
        if test_folder_id:
            print(f"✅ Created test folder with ID: {test_folder_id}")
        else:
            print("❌ Failed to create test folder")
    else:
        print("❌ Failed to initialize Google Drive service")

if __name__ == "__main__":
    asyncio.run(test_google_drive())
