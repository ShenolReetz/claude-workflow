#!/usr/bin/env python3
"""
TikTok MCP Server - Production Version
TikTok API integration for video upload and management
"""

import asyncio
import json
import logging
import httpx
import urllib.parse
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TikTokMCPServer:
    """TikTok MCP Server for video upload and management"""
    
    def __init__(self, client_id: str, client_secret: str, access_token: str = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.base_url = "https://open-api.tiktok.com"
        self.client = httpx.AsyncClient(timeout=300)
        
        logger.info("📱 TikTok MCP Server initialized")
        
    async def generate_auth_url(self, redirect_uri: str, state: str = "random_state") -> str:
        """Generate TikTok OAuth authorization URL"""
        
        params = {
            'client_key': self.client_id,
            'scope': 'video.upload,user.info.basic',
            'response_type': 'code',
            'redirect_uri': redirect_uri,
            'state': state
        }
        
        auth_url = f"https://www.tiktok.com/auth/authorize/?{urllib.parse.urlencode(params)}"
        logger.info(f"📱 Generated TikTok auth URL: {auth_url}")
        return auth_url
    
    async def exchange_code_for_token(self, code: str, redirect_uri: str) -> dict:
        """Exchange authorization code for access token"""
        
        try:
            data = {
                'client_key': self.client_id,
                'client_secret': self.client_secret,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': redirect_uri
            }
            
            response = await self.client.post(
                f"{self.base_url}/oauth/access_token/",
                data=data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            result = response.json()
            
            if response.status_code == 200 and result.get('data', {}).get('access_token'):
                token_data = result['data']
                return {
                    'success': True,
                    'access_token': token_data['access_token'],
                    'refresh_token': token_data.get('refresh_token'),
                    'expires_in': token_data.get('expires_in'),
                    'token_type': token_data.get('token_type', 'bearer'),
                    'scope': token_data.get('scope')
                }
            else:
                return {
                    'success': False,
                    'error': result.get('message', 'Token exchange failed'),
                    'error_code': result.get('error_code')
                }
                
        except Exception as e:
            logger.error(f"❌ Token exchange failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def refresh_access_token(self, refresh_token: str) -> dict:
        """Refresh TikTok access token"""
        
        try:
            data = {
                'client_key': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token
            }
            
            response = await self.client.post(
                f"{self.base_url}/oauth/refresh_token/",
                data=data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            result = response.json()
            
            if response.status_code == 200 and result.get('data', {}).get('access_token'):
                token_data = result['data']
                return {
                    'success': True,
                    'access_token': token_data['access_token'],
                    'refresh_token': token_data.get('refresh_token'),
                    'expires_in': token_data.get('expires_in')
                }
            else:
                return {
                    'success': False,
                    'error': result.get('message', 'Token refresh failed')
                }
                
        except Exception as e:
            logger.error(f"❌ Token refresh failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_user_info(self) -> dict:
        """Get TikTok user information"""
        
        if not self.access_token:
            return {
                'success': False,
                'error': 'No access token available'
            }
        
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            response = await self.client.get(
                f"{self.base_url}/user/info/",
                headers=headers
            )
            
            result = response.json()
            
            if response.status_code == 200 and result.get('data'):
                user_data = result['data']['user']
                return {
                    'success': True,
                    'user_id': user_data.get('open_id'),
                    'username': user_data.get('display_name'),
                    'avatar_url': user_data.get('avatar_url')
                }
            else:
                return {
                    'success': False,
                    'error': result.get('message', 'Failed to get user info')
                }
                
        except Exception as e:
            logger.error(f"❌ Error getting user info: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def upload_video(self, video_url: str, caption: str, privacy_level: str = "PRIVATE") -> dict:
        """Upload video to TikTok"""
        
        if not self.access_token:
            return {
                'success': False,
                'error': 'No access token available'
            }
        
        logger.info(f"📱 Starting TikTok video upload")
        logger.info(f"   🎥 Video URL: {video_url}")
        logger.info(f"   📝 Caption: {caption[:100]}...")
        logger.info(f"   🔒 Privacy: {privacy_level}")
        
        try:
            # First, we need to download the video to upload it
            # TikTok API requires multipart upload
            video_response = await self.client.get(video_url)
            
            if video_response.status_code != 200:
                return {
                    'success': False,
                    'error': f'Failed to download video: {video_response.status_code}'
                }
            
            video_content = video_response.content
            
            # Prepare upload data
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            
            files = {
                'video': ('video.mp4', video_content, 'video/mp4')
            }
            
            data = {
                'post_info': json.dumps({
                    'title': caption[:150],  # TikTok has 150 character limit
                    'privacy_level': privacy_level,
                    'disable_duet': False,
                    'disable_comment': False,
                    'disable_stitch': False,
                    'video_cover_timestamp_ms': 1000
                })
            }
            
            # Upload video
            response = await self.client.post(
                f"{self.base_url}/video/upload/",
                headers=headers,
                files=files,
                data=data
            )
            
            result = response.json()
            
            if response.status_code == 200 and result.get('data'):
                upload_data = result['data']
                
                logger.info(f"✅ TikTok video uploaded successfully")
                
                return {
                    'success': True,
                    'publish_id': upload_data.get('publish_id'),
                    'upload_url': upload_data.get('upload_url', ''),
                    'status': 'uploaded'
                }
            else:
                logger.error(f"❌ TikTok upload failed: {result}")
                return {
                    'success': False,
                    'error': result.get('message', 'Upload failed'),
                    'error_code': result.get('error_code')
                }
                
        except Exception as e:
            logger.error(f"❌ TikTok upload failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def check_upload_status(self, publish_id: str) -> dict:
        """Check TikTok video upload status"""
        
        if not self.access_token:
            return {
                'success': False,
                'error': 'No access token available'
            }
        
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            params = {
                'publish_id': publish_id
            }
            
            response = await self.client.get(
                f"{self.base_url}/video/query/",
                headers=headers,
                params=params
            )
            
            result = response.json()
            
            if response.status_code == 200 and result.get('data', {}).get('videos'):
                video_data = result['data']['videos'][0]
                
                return {
                    'success': True,
                    'status': video_data.get('status'),
                    'video_id': video_data.get('video_id'),
                    'share_url': video_data.get('share_url', ''),
                    'embed_url': video_data.get('embed_url', ''),
                    'create_time': video_data.get('create_time')
                }
            else:
                return {
                    'success': False,
                    'error': result.get('message', 'Failed to check status')
                }
                
        except Exception as e:
            logger.error(f"❌ Error checking upload status: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def wait_for_upload_completion(self, publish_id: str, max_wait_minutes: int = 10) -> dict:
        """Wait for TikTok upload to complete and return final status"""
        
        logger.info(f"⏳ Waiting for TikTok upload completion: {publish_id}")
        
        max_attempts = max_wait_minutes * 2  # Check every 30 seconds
        
        for attempt in range(max_attempts):
            status_result = await self.check_upload_status(publish_id)
            
            if not status_result.get('success'):
                return status_result
            
            status = status_result.get('status', '').lower()
            
            if status == 'published':
                logger.info(f"✅ TikTok video published successfully")
                return {
                    'success': True,
                    'status': 'published',
                    'video_id': status_result.get('video_id'),
                    'share_url': status_result.get('share_url', ''),
                    'video_url': status_result.get('share_url', '')
                }
            elif status in ['failed', 'blocked', 'under_review']:
                logger.error(f"❌ TikTok upload failed with status: {status}")
                return {
                    'success': False,
                    'status': status,
                    'error': f'Upload failed with status: {status}'
                }
            
            logger.info(f"⏳ TikTok upload status: {status} - Attempt {attempt + 1}/{max_attempts}")
            await asyncio.sleep(30)  # Wait 30 seconds between checks
        
        return {
            'success': False,
            'error': f'Upload timeout after {max_wait_minutes} minutes',
            'status': 'timeout'
        }
    
    async def upload_video_complete(self, video_url: str, caption: str, privacy_level: str = "PRIVATE") -> dict:
        """Complete TikTok video upload with status monitoring"""
        
        # Step 1: Upload video
        upload_result = await self.upload_video(video_url, caption, privacy_level)
        
        if not upload_result.get('success'):
            return upload_result
        
        publish_id = upload_result.get('publish_id')
        
        if not publish_id:
            return {
                'success': False,
                'error': 'No publish ID returned from upload'
            }
        
        # Step 2: Wait for completion
        completion_result = await self.wait_for_upload_completion(publish_id)
        
        return completion_result
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()