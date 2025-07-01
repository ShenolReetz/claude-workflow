import os
import logging
from typing import Dict, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import httpx

logger = logging.getLogger(__name__)

class YouTubeMCP:
    """YouTube upload MCP - fixed for headless servers"""
    
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    
    def __init__(self, credentials_path: str, token_path: str = None):
        self.credentials_path = credentials_path
        self.token_path = token_path or credentials_path.replace('credentials.json', 'token.json')
        self.youtube = None
        self._initialize_youtube()
    
    def _initialize_youtube(self):
        """Initialize YouTube API client"""
        creds = None
        
        # Load token
        if os.path.exists(self.token_path):
            try:
                creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)
            except Exception as e:
                logger.error(f"Error loading token: {e}")
        
        # Check if valid
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    # Save refreshed token
                    with open(self.token_path, 'w') as token:
                        token.write(creds.to_json())
                except Exception as e:
                    logger.error(f"Token refresh failed: {e}")
                    raise Exception("YouTube token expired. Please run: python3 youtube_auth_console.py")
            else:
                raise Exception("No YouTube authentication found. Please run: python3 youtube_auth_console.py")
        
        self.youtube = build('youtube', 'v3', credentials=creds)
        logger.info("✅ YouTube API initialized")
    
    async def upload_video(self, video_path: str, title: str, description: str, 
                          tags: list = None, category_id: str = "22", 
                          privacy_status: str = "private") -> Dict:
        """Upload video to YouTube"""
        try:
            # Download if URL
            if video_path.startswith('http'):
                logger.info(f"📥 Downloading video from: {video_path}")
                local_path = await self._download_video(video_path)
            else:
                local_path = video_path
            
            # Prepare metadata
            body = {
                'snippet': {
                    'title': title[:100],  # YouTube limit
                    'description': description[:5000],  # YouTube limit
                    'tags': tags or [],
                    'categoryId': category_id
                },
                'status': {
                    'privacyStatus': privacy_status,
                    'selfDeclaredMadeForKids': False
                }
            }
            
            # Upload
            logger.info(f"📤 Uploading: {title}")
            media = MediaFileUpload(local_path, chunksize=-1, resumable=True, mimetype='video/mp4')
            
            request = self.youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = None
            error = None
            retry = 0
            
            while response is None:
                try:
                    status, response = request.next_chunk()
                    if status:
                        progress = int(status.progress() * 100)
                        logger.info(f"📊 Upload progress: {progress}%")
                except Exception as e:
                    error = e
                    retry += 1
                    if retry > 3:
                        raise e
                    logger.warning(f"Retry {retry}/3: {e}")
            
            video_id = response['id']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            logger.info(f"✅ Upload complete: {video_url}")
            
            # Cleanup
            if video_path.startswith('http') and os.path.exists(local_path):
                os.remove(local_path)
            
            return {
                'success': True,
                'video_id': video_id,
                'video_url': video_url,
                'title': title
            }
            
        except Exception as e:
            logger.error(f"❌ Upload failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _download_video(self, url: str) -> str:
        """Download video from URL to temp file"""
        import tempfile
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()
            
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
                tmp.write(response.content)
                return tmp.name
