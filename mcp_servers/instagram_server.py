#!/usr/bin/env python3
"""
Instagram MCP Server - Production Version
Instagram API integration for Reels upload and management
"""

import asyncio
import json
import logging
import httpx
import urllib.parse
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InstagramMCPServer:
    """Instagram MCP Server for Reels upload and management"""
    
    def __init__(self, app_id: str, app_secret: str, access_token: str = None):
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = access_token
        self.base_url = "https://graph.facebook.com/v18.0"
        self.client = httpx.AsyncClient(timeout=300)
        
        logger.info("📱 Instagram MCP Server initialized")
        
    async def generate_auth_url(self, redirect_uri: str) -> str:
        """Generate Instagram OAuth authorization URL"""
        
        params = {
            'client_id': self.app_id,
            'redirect_uri': redirect_uri,
            'scope': 'instagram_content_publish,pages_read_engagement,pages_show_list',
            'response_type': 'code'
        }
        
        auth_url = f"https://www.facebook.com/dialog/oauth?{urllib.parse.urlencode(params)}"
        logger.info(f"📱 Generated Instagram auth URL: {auth_url}")
        return auth_url
    
    async def exchange_code_for_token(self, code: str, redirect_uri: str) -> dict:
        """Exchange authorization code for access token"""
        
        try:
            params = {
                'client_id': self.app_id,
                'client_secret': self.app_secret,
                'redirect_uri': redirect_uri,
                'code': code
            }
            
            response = await self.client.get(
                f"{self.base_url}/oauth/access_token",
                params=params
            )
            
            result = response.json()
            
            if response.status_code == 200 and result.get('access_token'):
                # Exchange for long-lived token
                long_lived_token = await self._get_long_lived_token(result['access_token'])
                return {
                    'success': True,
                    'access_token': result['access_token'],
                    'long_lived_token': long_lived_token,
                    'token_type': result.get('token_type', 'bearer')
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', {}).get('message', 'Token exchange failed')
                }
                
        except Exception as e:
            logger.error(f"❌ Token exchange failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _get_long_lived_token(self, short_lived_token: str) -> Optional[str]:
        """Exchange short-lived token for long-lived token"""
        
        try:
            params = {
                'grant_type': 'fb_exchange_token',
                'client_id': self.app_id,
                'client_secret': self.app_secret,
                'fb_exchange_token': short_lived_token
            }
            
            response = await self.client.get(
                f"{self.base_url}/oauth/access_token",
                params=params
            )
            
            result = response.json()
            
            if response.status_code == 200:
                return result.get('access_token')
            else:
                logger.warning(f"⚠️ Long-lived token exchange failed: {result}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Long-lived token exchange error: {str(e)}")
            return None
    
    async def get_instagram_account_id(self) -> Optional[str]:
        """Get Instagram Business Account ID"""
        
        if not self.access_token:
            logger.error("❌ No access token available")
            return None
        
        try:
            # Get pages connected to the Facebook account
            response = await self.client.get(
                f"{self.base_url}/me/accounts",
                params={'access_token': self.access_token}
            )
            
            result = response.json()
            
            if response.status_code == 200 and result.get('data'):
                for page in result['data']:
                    page_id = page['id']
                    page_token = page['access_token']
                    
                    # Check if this page has an Instagram account
                    ig_response = await self.client.get(
                        f"{self.base_url}/{page_id}",
                        params={
                            'fields': 'instagram_business_account',
                            'access_token': page_token
                        }
                    )
                    
                    ig_result = ig_response.json()
                    
                    if ig_result.get('instagram_business_account'):
                        instagram_account_id = ig_result['instagram_business_account']['id']
                        logger.info(f"📱 Found Instagram account: {instagram_account_id}")
                        return instagram_account_id
            
            logger.warning("⚠️ No Instagram Business Account found")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting Instagram account: {str(e)}")
            return None
    
    async def create_media_container(self, video_url: str, caption: str, cover_url: str = None, is_private: bool = True) -> dict:
        """Create Instagram media container for Reel"""
        
        instagram_account_id = await self.get_instagram_account_id()
        if not instagram_account_id:
            return {
                'success': False,
                'error': 'No Instagram Business Account found'
            }
        
        try:
            # Note: Instagram API doesn't support private post creation via API
            # Privacy is controlled by account settings in Instagram app
            if is_private:
                logger.info("🔒 Private mode requested - Note: Instagram API uploads follow account privacy settings")
            
            # Prepare media container data
            container_data = {
                'media_type': 'REELS',
                'video_url': video_url,
                'caption': caption,
                'access_token': self.access_token
            }
            
            # Add cover image if provided
            if cover_url:
                container_data['cover_url'] = cover_url
            
            # Create media container
            response = await self.client.post(
                f"{self.base_url}/{instagram_account_id}/media",
                data=container_data
            )
            
            result = response.json()
            
            if response.status_code == 200 and result.get('id'):
                logger.info(f"📱 Media container created: {result['id']}")
                return {
                    'success': True,
                    'container_id': result['id'],
                    'instagram_account_id': instagram_account_id
                }
            else:
                logger.error(f"❌ Failed to create media container: {result}")
                return {
                    'success': False,
                    'error': result.get('error', {}).get('message', 'Container creation failed')
                }
                
        except Exception as e:
            logger.error(f"❌ Error creating media container: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def publish_media_container(self, container_id: str, instagram_account_id: str) -> dict:
        """Publish Instagram media container"""
        
        try:
            response = await self.client.post(
                f"{self.base_url}/{instagram_account_id}/media_publish",
                data={
                    'creation_id': container_id,
                    'access_token': self.access_token
                }
            )
            
            result = response.json()
            
            if response.status_code == 200 and result.get('id'):
                media_id = result['id']
                
                # Get media information including permalink
                media_info = await self.get_media_info(media_id)
                
                logger.info(f"📱 Instagram Reel published: {media_id}")
                return {
                    'success': True,
                    'media_id': media_id,
                    'permalink': media_info.get('permalink', ''),
                    'media_url': f"https://www.instagram.com/reel/{media_id}/"
                }
            else:
                logger.error(f"❌ Failed to publish media: {result}")
                return {
                    'success': False,
                    'error': result.get('error', {}).get('message', 'Media publish failed')
                }
                
        except Exception as e:
            logger.error(f"❌ Error publishing media: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_media_info(self, media_id: str) -> dict:
        """Get Instagram media information"""
        
        try:
            response = await self.client.get(
                f"{self.base_url}/{media_id}",
                params={
                    'fields': 'id,media_type,media_url,permalink,caption,timestamp',
                    'access_token': self.access_token
                }
            )
            
            result = response.json()
            
            if response.status_code == 200:
                return result
            else:
                logger.error(f"❌ Failed to get media info: {result}")
                return {}
                
        except Exception as e:
            logger.error(f"❌ Error getting media info: {str(e)}")
            return {}
    
    async def upload_reel(self, video_url: str, caption: str, cover_url: str = None, is_private: bool = True) -> dict:
        """Complete Instagram Reel upload process"""
        
        logger.info(f"📱 Starting Instagram Reel upload")
        logger.info(f"   🎥 Video URL: {video_url}")
        logger.info(f"   📝 Caption: {caption[:100]}...")
        
        try:
            # Step 1: Create media container
            container_result = await self.create_media_container(video_url, caption, cover_url, is_private)
            
            if not container_result.get('success'):
                return container_result
            
            container_id = container_result['container_id']
            instagram_account_id = container_result['instagram_account_id']
            
            # Step 2: Wait for media processing
            logger.info("⏳ Waiting for media processing...")
            await asyncio.sleep(30)  # Wait for Instagram to process the video
            
            # Step 3: Publish media container
            publish_result = await self.publish_media_container(container_id, instagram_account_id)
            
            if publish_result.get('success'):
                logger.info(f"✅ Instagram Reel uploaded successfully: {publish_result.get('permalink', 'N/A')}")
            
            return publish_result
            
        except Exception as e:
            logger.error(f"❌ Instagram upload failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def check_container_status(self, container_id: str) -> dict:
        """Check the status of a media container"""
        
        try:
            response = await self.client.get(
                f"{self.base_url}/{container_id}",
                params={
                    'fields': 'status_code,status',
                    'access_token': self.access_token
                }
            )
            
            result = response.json()
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'status_code': result.get('status_code'),
                    'status': result.get('status', 'unknown')
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', {}).get('message', 'Status check failed')
                }
                
        except Exception as e:
            logger.error(f"❌ Error checking container status: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()