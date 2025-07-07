#!/usr/bin/env python3
"""
TikTok MCP Server - Handles TikTok video uploads and management
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

class TikTokMCPServer:
    """TikTok API integration for video uploads"""
    
    def __init__(self, client_id: str, client_secret: str, access_token: Optional[str] = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.api_base_url = "https://open.tiktokapis.com/v2"
        self.upload_url = "https://open-upload.tiktokapis.com/video/upload/"
        self.client = httpx.AsyncClient(timeout=300.0)
        
    async def authenticate(self, auth_code: Optional[str] = None) -> Dict[str, Any]:
        """Authenticate with TikTok OAuth2"""
        if auth_code:
            # Exchange auth code for access token
            auth_url = "https://open.tiktokapis.com/v2/oauth/token/"
            
            data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": auth_code,
                "grant_type": "authorization_code"
            }
            
            response = await self.client.post(auth_url, data=data)
            
            if response.status_code == 200:
                result = response.json()
                self.access_token = result.get("access_token")
                logger.info("✅ TikTok authentication successful")
                return result
            else:
                logger.error(f"❌ TikTok auth failed: {response.text}")
                return {"error": response.text}
        else:
            # Return auth URL for user to visit
            auth_url = (
                f"https://www.tiktok.com/v2/auth/authorize?"
                f"client_id={self.client_id}"
                f"&response_type=code"
                f"&scope=video.upload,video.publish"
                f"&redirect_uri=http://localhost:8080/callback"
            )
            return {"auth_url": auth_url}
    
    async def upload_video(self, video_path: str, title: str, 
                          privacy_level: str = "PRIVATE") -> Dict[str, Any]:
        """Upload video to TikTok"""
        if not self.access_token:
            return {"success": False, "error": "Not authenticated"}
        
        try:
            # Download video if it's a URL
            if video_path.startswith('http'):
                logger.info(f"📥 Downloading video from: {video_path}")
                video_data = await self._download_video(video_path)
            else:
                with open(video_path, 'rb') as f:
                    video_data = f.read()
            
            # Step 1: Initialize upload
            init_data = {
                "post_info": {
                    "title": title[:150],  # TikTok limit
                    "privacy_level": privacy_level,
                    "disable_duet": False,
                    "disable_comment": False,
                    "disable_stitch": False,
                    "video_cover_timestamp_ms": 1000
                },
                "source_info": {
                    "source": "FILE_UPLOAD",
                    "video_size": len(video_data)
                }
            }
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            # Initialize upload
            init_response = await self.client.post(
                f"{self.api_base_url}/post/publish/video/init/",
                headers=headers,
                json=init_data
            )
            
            if init_response.status_code != 200:
                logger.error(f"❌ TikTok init failed: {init_response.text}")
                return {"success": False, "error": init_response.text}
            
            init_result = init_response.json()
            upload_url = init_result.get("data", {}).get("upload_url")
            publish_id = init_result.get("data", {}).get("publish_id")
            
            if not upload_url:
                return {"success": False, "error": "No upload URL received"}
            
            # Step 2: Upload video
            logger.info("📤 Uploading video to TikTok...")
            
            upload_headers = {
                "Content-Type": "video/mp4",
                "Content-Length": str(len(video_data))
            }
            
            upload_response = await self.client.put(
                upload_url,
                headers=upload_headers,
                content=video_data
            )
            
            if upload_response.status_code not in [200, 201]:
                logger.error(f"❌ TikTok upload failed: {upload_response.text}")
                return {"success": False, "error": upload_response.text}
            
            # Step 3: Check upload status
            status_response = await self.client.get(
                f"{self.api_base_url}/post/publish/status/fetch/",
                headers=headers,
                params={"publish_id": publish_id}
            )
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                logger.info("✅ TikTok upload successful!")
                
                return {
                    "success": True,
                    "publish_id": publish_id,
                    "status": status_data.get("data", {}).get("status"),
                    "video_id": status_data.get("data", {}).get("share_id")
                }
            else:
                return {"success": False, "error": status_response.text}
            
        except Exception as e:
            logger.error(f"❌ TikTok upload error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _download_video(self, url: str) -> bytes:
        """Download video from URL"""
        response = await self.client.get(url)
        response.raise_for_status()
        return response.content
    
    async def get_video_status(self, publish_id: str) -> Dict[str, Any]:
        """Check video publishing status"""
        if not self.access_token:
            return {"error": "Not authenticated"}
        
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        
        response = await self.client.get(
            f"{self.api_base_url}/post/publish/status/fetch/",
            headers=headers,
            params={"publish_id": publish_id}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.text}
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Test function
async def test_tiktok_server():
    """Test TikTok server functionality"""
    server = TikTokMCPServer(
        client_id="YOUR_CLIENT_ID",
        client_secret="YOUR_CLIENT_SECRET"
    )
    
    # Get auth URL
    auth_result = await server.authenticate()
    print(f"Visit this URL to authenticate: {auth_result.get('auth_url')}")
    
    await server.close()

if __name__ == "__main__":
    asyncio.run(test_tiktok_server())
