#!/usr/bin/env python3
"""
Production YouTube Upload - LOCAL VIDEO FILE
============================================
Uploads video directly from local storage to YouTube.
No need to download from Google Drive.
"""

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from typing import Dict, Optional
import logging
import os
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


async def production_upload_to_youtube_local(record: Dict, config: Dict) -> Dict:
    """
    Upload local video file to YouTube
    """
    try:
        fields = record.get('fields', {})
        record_id = record.get('record_id', 'unknown')
        
        # Find the local video file
        video_path = fields.get('FinalVideo', '')
        
        # If it's a URL, we need to find the local file
        if not video_path or video_path.startswith('http'):
            # Look for video in local storage
            video_path = find_local_video(record_id)
        
        if not video_path or not Path(video_path).exists():
            return {
                'success': False,
                'error': f'Local video file not found: {video_path}',
                'updated_record': record
            }
        
        logger.info(f"📺 Uploading local video to YouTube: {video_path}")
        
        # Get YouTube credentials
        youtube_service = get_youtube_service(config)
        if not youtube_service:
            return {
                'success': False,
                'error': 'Failed to authenticate with YouTube',
                'updated_record': record
            }
        
        # Prepare video metadata
        title = fields.get('YouTubeTitle', fields.get('VideoTitle', 'Amazing Products'))
        description = fields.get('YouTubeDescription', '')
        tags = fields.get('YouTubeTags', '').split(',') if fields.get('YouTubeTags') else []
        
        # Clean up tags
        tags = [tag.strip() for tag in tags if tag.strip()][:500]  # YouTube limit
        
        # Create request body
        request_body = {
            'snippet': {
                'title': title[:100],  # YouTube title limit
                'description': description[:5000],  # YouTube description limit
                'tags': tags,
                'categoryId': '22'  # People & Blogs
            },
            'status': {
                'privacyStatus': 'public',
                'selfDeclaredMadeForKids': False
            }
        }
        
        # Create media upload
        media = MediaFileUpload(
            video_path,
            chunksize=-1,
            resumable=True,
            mimetype='video/mp4'
        )
        
        # Execute upload
        request = youtube_service.videos().insert(
            part='snippet,status',
            body=request_body,
            media_body=media
        )
        
        logger.info("⬆️ Starting YouTube upload...")
        response = request.execute()
        
        if response:
            video_id = response.get('id')
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            logger.info(f"✅ YouTube upload successful: {video_url}")
            
            # Update record with YouTube URL
            fields['YouTubeURL'] = video_url
            fields['YouTubeVideoId'] = video_id
            fields['YouTubeUploadTime'] = datetime.now().isoformat()
            
            record['fields'] = fields
            
            # Get video file size for stats
            file_size_mb = Path(video_path).stat().st_size / (1024 * 1024)
            
            return {
                'success': True,
                'video_id': video_id,
                'video_url': video_url,
                'updated_record': record,
                'file_size_mb': round(file_size_mb, 2),
                'local_file': video_path
            }
        else:
            return {
                'success': False,
                'error': 'No response from YouTube API',
                'updated_record': record
            }
            
    except Exception as e:
        logger.error(f"❌ YouTube upload failed: {e}")
        return {
            'success': False,
            'error': str(e),
            'updated_record': record
        }


def find_local_video(record_id: str) -> Optional[str]:
    """Find local video file for a record"""
    try:
        # Check common locations
        base_paths = [
            Path("/home/claude-workflow/media_storage"),
            Path("/tmp/remotion-renders"),
            Path("/home/claude-workflow/media_storage/videos")
        ]
        
        # Look for video with record ID
        for base_path in base_paths:
            if base_path.exists():
                # Direct path
                pattern = f"countdown_{record_id}*.mp4"
                for video_file in base_path.glob(pattern):
                    if video_file.exists():
                        logger.info(f"Found local video: {video_file}")
                        return str(video_file)
                
                # Check in subdirectories
                for video_file in base_path.rglob(pattern):
                    if video_file.exists():
                        logger.info(f"Found local video: {video_file}")
                        return str(video_file)
        
        # Check today's directory
        today = datetime.now().strftime("%Y-%m-%d")
        today_path = Path(f"/home/claude-workflow/media_storage/{today}/videos")
        if today_path.exists():
            pattern = f"countdown_{record_id}*.mp4"
            for video_file in today_path.glob(pattern):
                if video_file.exists():
                    logger.info(f"Found local video: {video_file}")
                    return str(video_file)
        
        logger.warning(f"No local video found for record {record_id}")
        return None
        
    except Exception as e:
        logger.error(f"Error finding local video: {e}")
        return None


def get_youtube_service(config: Dict):
    """Get authenticated YouTube service"""
    try:
        # Get credentials from config or token file
        token_path = '/home/claude-workflow/config/youtube_token.json'
        
        if Path(token_path).exists():
            import json
            with open(token_path, 'r') as f:
                token_data = json.load(f)
            
            credentials = Credentials(
                token=token_data.get('access_token'),
                refresh_token=token_data.get('refresh_token'),
                token_uri='https://oauth2.googleapis.com/token',
                client_id=config.get('youtube_client_id'),
                client_secret=config.get('youtube_client_secret'),
                scopes=['https://www.googleapis.com/auth/youtube.upload']
            )
            
            # Build YouTube service
            youtube = build('youtube', 'v3', credentials=credentials)
            return youtube
        else:
            logger.error("YouTube token file not found")
            return None
            
    except Exception as e:
        logger.error(f"Failed to create YouTube service: {e}")
        return None