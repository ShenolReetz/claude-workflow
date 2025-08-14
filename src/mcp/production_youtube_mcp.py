#!/usr/bin/env python3
"""
Production YouTube MCP - Upload to YouTube with Robust Authentication
"""

from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError
from typing import Dict, List, Optional
import json
import os
import aiohttp
import tempfile
import logging
import asyncio
import time

# Import authentication manager
import sys
sys.path.append('/home/claude-workflow')
from src.utils.youtube_auth_manager import YouTubeAuthManager

class ProductionYouTubeMCP:
    def __init__(self, config: Dict):
        self.config = config
        self.auth_manager = YouTubeAuthManager(config)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Retry configuration
        self.max_retries = 3
        self.retry_delay = 5  # seconds
        
    async def upload_video(self, video_url: str, title: str, description: str, tags: List[str]) -> Dict:
        """Upload video to YouTube with robust error handling"""
        try:
            # Get authenticated YouTube service
            youtube = self.auth_manager.get_youtube_service()
            
            # First, download the video file
            video_path = await self._download_video(video_url)
            if not video_path:
                return {
                    'success': False,
                    'error': 'Failed to download video for upload'
                }
            
            # Prepare video metadata
            body = {
                'snippet': {
                    'title': title[:100],  # YouTube title limit
                    'description': description[:5000],  # YouTube description limit
                    'tags': tags[:30] if tags else [],  # YouTube tags limit
                    'categoryId': self.config.get('youtube_category', '28'),  # Science & Technology
                    'defaultLanguage': 'en',
                    'defaultAudioLanguage': 'en'
                },
                'status': {
                    'privacyStatus': self.config.get('youtube_privacy', 'public'),
                    'madeForKids': False,
                    'selfDeclaredMadeForKids': False
                }
            }
            
            # Upload with retries
            for attempt in range(self.max_retries):
                try:
                    self.logger.info(f"Uploading video to YouTube (attempt {attempt + 1}/{self.max_retries})...")
                    
                    # Call the YouTube API
                    media = MediaFileUpload(
                        video_path,
                        chunksize=-1,
                        resumable=True,
                        mimetype='video/mp4'
                    )
                    
                    request = youtube.videos().insert(
                        part=','.join(body.keys()),
                        body=body,
                        media_body=media
                    )
                    
                    # Execute upload with resumable support
                    response = None
                    while response is None:
                        status, response = request.next_chunk()
                        if status:
                            progress = int(status.progress() * 100)
                            self.logger.info(f"Upload progress: {progress}%")
                    
                    # Clean up temp file
                    if os.path.exists(video_path):
                        os.remove(video_path)
                    
                    video_id = response.get('id')
                    video_url = f"https://www.youtube.com/watch?v={video_id}"
                    
                    self.logger.info(f"✅ Video uploaded successfully: {video_url}")
                    
                    return {
                        'success': True,
                        'video_id': video_id,
                        'video_url': video_url,
                        'response': response
                    }
                    
                except HttpError as e:
                    self.logger.warning(f"YouTube API error (attempt {attempt + 1}): {e}")
                    
                    if e.resp.status == 401:
                        # Try to refresh authentication
                        self.logger.info("Refreshing authentication...")
                        self.auth_manager.creds = None
                        youtube = self.auth_manager.get_youtube_service()
                    
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(self.retry_delay * (attempt + 1))
                    else:
                        raise
                        
                except Exception as e:
                    self.logger.error(f"Upload error (attempt {attempt + 1}): {e}")
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(self.retry_delay)
                    else:
                        raise
            
            
        except Exception as e:
            self.logger.error(f"❌ Error uploading to YouTube: {e}")
            # Clean up temp file if it exists
            if 'video_path' in locals() and os.path.exists(video_path):
                os.remove(video_path)
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _download_video(self, video_url: str) -> Optional[str]:
        """Download video from URL to temp file"""
        try:
            # Handle local file paths
            if video_url.startswith('file://') or video_url.startswith('/'):
                local_path = video_url.replace('file://', '') if video_url.startswith('file://') else video_url
                if os.path.exists(local_path):
                    self.logger.info(f"✅ Using local video file: {local_path}")
                    return local_path
                else:
                    self.logger.error(f"Local file not found: {local_path}")
                    return None
            
            # Handle different URL types (Google Drive, JSON2Video, direct URL, etc.)
            if 'drive.google.com' in video_url:
                # Extract file ID from Google Drive URL
                if '/file/d/' in video_url:
                    file_id = video_url.split('/file/d/')[1].split('/')[0]
                elif 'id=' in video_url:
                    file_id = video_url.split('id=')[1].split('&')[0]
                else:
                    self.logger.error(f"Cannot extract file ID from URL: {video_url}")
                    return None
                
                # Use Google Drive direct download URL
                download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
            elif 'cloudfront.net' in video_url or 'json2video.com' in video_url:
                # JSON2Video CloudFront URLs - download directly with appropriate headers
                download_url = video_url
                self.logger.info(f"Detected JSON2Video/CloudFront URL")
            else:
                download_url = video_url
            
            # Download video to temp file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            temp_path = temp_file.name
            
            # Add headers to handle CloudFront/JSON2Video URLs
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'video/mp4,video/*;q=0.9,*/*;q=0.8',
                'Referer': 'https://app.json2video.com/'
            }
            
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(download_url, allow_redirects=True) as response:
                    if response.status == 200:
                        total_size = int(response.headers.get('Content-Length', 0))
                        downloaded = 0
                        
                        with open(temp_path, 'wb') as f:
                            async for chunk in response.content.iter_chunked(8192):
                                f.write(chunk)
                                downloaded += len(chunk)
                                if total_size > 0 and downloaded % (total_size // 10) == 0:
                                    progress = (downloaded / total_size) * 100
                                    self.logger.info(f"Download progress: {progress:.0f}%")
                        
                        self.logger.info(f"✅ Video downloaded to {temp_path} ({downloaded / 1024 / 1024:.1f} MB)")
                        return temp_path
                    elif response.status == 403:
                        # For 403 errors, try waiting and retrying (video might still be processing)
                        self.logger.warning(f"Got 403 error. Video might still be processing. Waiting 30s...")
                        await asyncio.sleep(30)
                        
                        # Retry once
                        async with session.get(download_url, allow_redirects=True) as retry_response:
                            if retry_response.status == 200:
                                with open(temp_path, 'wb') as f:
                                    async for chunk in retry_response.content.iter_chunked(8192):
                                        f.write(chunk)
                                self.logger.info(f"✅ Video downloaded on retry to {temp_path}")
                                return temp_path
                            else:
                                self.logger.error(f"Failed to download video after retry: HTTP {retry_response.status}")
                                # As fallback, return None to skip YouTube upload but continue workflow
                                return None
                    else:
                        self.logger.error(f"Failed to download video: HTTP {response.status}")
                        return None
                        
        except Exception as e:
            self.logger.error(f"Error downloading video: {e}")
            return None
    
    async def test_authentication(self) -> bool:
        """Test YouTube authentication"""
        return self.auth_manager.test_authentication()