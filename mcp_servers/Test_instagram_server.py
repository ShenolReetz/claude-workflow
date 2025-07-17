#!/usr/bin/env python3
"""
Instagram MCP Server - Handles Instagram Reels uploads and management
"""

import asyncio
import httpx
import json
import logging
from typing import Dict, Any, Optional
import os
from datetime import datetime
import tempfile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InstagramMCPServer:
    """Instagram Basic Display API and Instagram Graph API integration for Reels uploads"""
    
    def __init__(self, app_id: str, app_secret: str, access_token: Optional[str] = None):
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = access_token
        self.api_base_url = "https://graph.instagram.com"
        self.graph_api_url = "https://graph.facebook.com/v18.0"
        self.client = httpx.AsyncClient(timeout=86400)
        
    async def authenticate(self, auth_code: Optional[str] = None) -> Dict[str, Any]:
        """Authenticate with Instagram OAuth2"""
        if auth_code:
            # Exchange auth code for access token
            auth_url = f"{self.graph_api_url}/oauth/access_token"
            
            data = {
                "client_id": self.app_id,
                "client_secret": self.app_secret,
                "grant_type": "authorization_code",
                "redirect_uri": "http://localhost:8080/callback",
                "code": auth_code
            }
            
            response = await self.client.post(auth_url, data=data)
            
            if response.status_code == 200:
                result = response.json()
                self.access_token = result.get("access_token")
                logger.info("✅ Instagram authentication successful")
                
                # Get long-lived token
                long_lived_token = await self._get_long_lived_token(self.access_token)
                if long_lived_token:
                    self.access_token = long_lived_token
                    result["long_lived_token"] = long_lived_token
                
                return result
            else:
                logger.error(f"❌ Instagram auth failed: {response.text}")
                return {"error": response.text}
        else:
            # Return auth URL for user to visit
            auth_url = (
                f"https://api.instagram.com/oauth/authorize?"
                f"client_id={self.app_id}"
                f"&redirect_uri=http://localhost:8080/callback"
                f"&scope=user_profile,user_media"
                f"&response_type=code"
            )
            return {"auth_url": auth_url}
    
    async def _get_long_lived_token(self, short_token: str) -> Optional[str]:
        """Exchange short-lived token for long-lived token"""
        try:
            url = f"{self.graph_api_url}/access_token"
            params = {
                "grant_type": "ig_exchange_token",
                "client_secret": self.app_secret,
                "access_token": short_token
            }
            
            response = await self.client.get(url, params=params)
            
            if response.status_code == 200:
                result = response.json()
                return result.get("access_token")
            else:
                logger.warning(f"Failed to get long-lived token: {response.text}")
                return None
        except Exception as e:
            logger.warning(f"Error getting long-lived token: {e}")
            return None
    
    async def upload_reel(self, video_path: str, caption: str, 
                         cover_url: Optional[str] = None) -> Dict[str, Any]:
        """Upload video as Instagram Reel"""
        if not self.access_token:
            return {"success": False, "error": "Not authenticated"}
        
        try:
            # Get Instagram Business Account ID
            user_id = await self._get_instagram_user_id()
            if not user_id:
                return {"success": False, "error": "Could not get Instagram user ID"}
            
            # Download video if it's a URL
            if video_path.startswith('http'):
                logger.info(f"📥 Downloading video from: {video_path}")
                video_url = video_path
            else:
                # Upload video to a temporary hosting service or use direct file
                return {"success": False, "error": "Local file upload not implemented - need video URL"}
            
            # Step 1: Create media container
            logger.info("📤 Creating Instagram Reel container...")
            
            container_data = {
                "media_type": "REELS",
                "video_url": video_url,
                "caption": caption[:2200],  # Instagram limit
                "access_token": self.access_token
            }
            
            # Add cover image if provided
            if cover_url:
                container_data["cover_url"] = cover_url
            
            container_response = await self.client.post(
                f"{self.api_base_url}/{user_id}/media",
                data=container_data
            )
            
            if container_response.status_code != 200:
                logger.error(f"❌ Instagram container creation failed: {container_response.text}")
                return {"success": False, "error": container_response.text}
            
            container_result = container_response.json()
            container_id = container_result.get("id")
            
            if not container_id:
                return {"success": False, "error": "No container ID received"}
            
            # Step 2: Check container status
            logger.info("⏳ Checking container status...")
            
            status_url = f"{self.api_base_url}/{container_id}"
            status_params = {
                "fields": "status_code,status",
                "access_token": self.access_token
            }
            
            # Wait for container to be ready
            max_attempts = 60  # 5 minutes max
            for attempt in range(max_attempts):
                await asyncio.sleep(5)
                
                status_response = await self.client.get(status_url, params=status_params)
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status_code = status_data.get("status_code")
                    
                    logger.info(f"📊 Container status: {status_code} (attempt {attempt + 1})")
                    
                    if status_code == "FINISHED":
                        break
                    elif status_code == "ERROR":
                        return {"success": False, "error": "Container processing failed"}
                else:
                    logger.warning(f"Status check failed: {status_response.text}")
            
            # Step 3: Publish media
            logger.info("🚀 Publishing Instagram Reel...")
            
            publish_data = {
                "creation_id": container_id,
                "access_token": self.access_token
            }
            
            publish_response = await self.client.post(
                f"{self.api_base_url}/{user_id}/media_publish",
                data=publish_data
            )
            
            if publish_response.status_code == 200:
                publish_result = publish_response.json()
                media_id = publish_result.get("id")
                
                logger.info("✅ Instagram Reel upload successful!")
                
                return {
                    "success": True,
                    "media_id": media_id,
                    "container_id": container_id,
                    "instagram_url": f"https://www.instagram.com/reel/{media_id}/"
                }
            else:
                logger.error(f"❌ Instagram publish failed: {publish_response.text}")
                return {"success": False, "error": publish_response.text}
            
        except Exception as e:
            logger.error(f"❌ Instagram upload error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _get_instagram_user_id(self) -> Optional[str]:
        """Get Instagram Business Account ID"""
        try:
            # First get Facebook Page ID
            me_url = f"{self.graph_api_url}/me"
            me_params = {
                "fields": "accounts",
                "access_token": self.access_token
            }
            
            me_response = await self.client.get(me_url, params=me_params)
            
            if me_response.status_code != 200:
                logger.error(f"Failed to get user info: {me_response.text}")
                return None
            
            me_data = me_response.json()
            accounts = me_data.get("accounts", {}).get("data", [])
            
            if not accounts:
                logger.error("No Facebook pages found")
                return None
            
            # Get Instagram Business Account from first page
            page_id = accounts[0]["id"]
            page_access_token = accounts[0]["access_token"]
            
            ig_url = f"{self.graph_api_url}/{page_id}"
            ig_params = {
                "fields": "instagram_business_account",
                "access_token": page_access_token
            }
            
            ig_response = await self.client.get(ig_url, params=ig_params)
            
            if ig_response.status_code == 200:
                ig_data = ig_response.json()
                ig_account = ig_data.get("instagram_business_account")
                if ig_account:
                    return ig_account.get("id")
            
            logger.error("No Instagram Business Account found")
            return None
            
        except Exception as e:
            logger.error(f"Error getting Instagram user ID: {e}")
            return None
    
    async def get_media_info(self, media_id: str) -> Dict[str, Any]:
        """Get information about uploaded media"""
        if not self.access_token:
            return {"error": "Not authenticated"}
        
        try:
            url = f"{self.api_base_url}/{media_id}"
            params = {
                "fields": "id,media_type,media_url,permalink,caption,timestamp,like_count,comments_count",
                "access_token": self.access_token
            }
            
            response = await self.client.get(url, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": response.text}
                
        except Exception as e:
            return {"error": str(e)}
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Test function
async def test_instagram_server():
    """Test Instagram server functionality"""
    server = InstagramMCPServer(
        app_id="YOUR_APP_ID",
        app_secret="YOUR_APP_SECRET"
    )
    
    # Get auth URL
    auth_result = await server.authenticate()
    print(f"Visit this URL to authenticate: {auth_result.get('auth_url')}")
    
    await server.close()

if __name__ == "__main__":
    asyncio.run(test_instagram_server())