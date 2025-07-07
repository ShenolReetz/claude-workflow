#!/usr/bin/env python3
"""
TikTok MCP Agent - Orchestrates TikTok video uploads in the workflow
"""

import asyncio
import json
import logging
import os
from typing import Dict, Any, Optional
from pathlib import Path

# Add parent directory to path for imports
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_servers.tiktok_server import TikTokMCPServer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TikTokMCP:
    """TikTok integration for the workflow"""
    
    def __init__(self, client_id: str = None, client_secret: str = None, 
                 access_token: str = None, token_path: str = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.token_path = token_path or '/home/claude-workflow/config/tiktok_token.json'
        
        # Load saved token if exists
        self._load_token()
        
        # Initialize server
        self.server = TikTokMCPServer(
            client_id=self.client_id,
            client_secret=self.client_secret,
            access_token=self.access_token
        )
        
        logger.info("✅ TikTok MCP initialized")
    
    def _load_token(self):
        """Load saved access token"""
        if os.path.exists(self.token_path):
            try:
                with open(self.token_path, 'r') as f:
                    token_data = json.load(f)
                    self.access_token = token_data.get('access_token')
                    logger.info("✅ Loaded saved TikTok token")
            except Exception as e:
                logger.warning(f"Could not load token: {e}")
    
    def _save_token(self, token_data: Dict[str, Any]):
        """Save access token for future use"""
        try:
            with open(self.token_path, 'w') as f:
                json.dump(token_data, f, indent=2)
            logger.info("✅ Saved TikTok token")
        except Exception as e:
            logger.error(f"Could not save token: {e}")
    
    async def authenticate(self, auth_code: Optional[str] = None) -> Dict[str, Any]:
        """Authenticate with TikTok"""
        result = await self.server.authenticate(auth_code)
        
        # Save token if authentication successful
        if result.get('access_token'):
            self._save_token(result)
            self.access_token = result['access_token']
        
        return result
    
    async def upload_video(self, video_path: str, title: str, 
                          description: str = "", tags: list = None,
                          privacy_status: str = "PRIVATE") -> Dict[str, Any]:
        """Upload video to TikTok with metadata"""
        try:
            # Prepare title with description and hashtags
            full_title = f"{title}\n\n{description}"
            
            # Add hashtags
            if tags:
                hashtags = ' '.join([f"#{tag}" for tag in tags[:10]])  # TikTok recommends 3-10 hashtags
                full_title += f"\n\n{hashtags}"
            
            # Common viral hashtags for product videos
            default_hashtags = "#amazonfinds #tiktokmademebuyit #musthave #2025 #viral #foryou"
            if default_hashtags not in full_title:
                full_title += f"\n{default_hashtags}"
            
            # Trim to TikTok's limit (150 chars for title, but description can be 2200)
            full_title = full_title[:2200]
            
            logger.info(f"📹 Uploading to TikTok: {title}")
            
            # Upload video
            result = await self.server.upload_video(
                video_path=video_path,
                title=full_title,
                privacy_level=privacy_status.upper()
            )
            
            if result.get('success'):
                # Get video URL (might not be immediately available)
                video_id = result.get('video_id')
                video_url = f"https://www.tiktok.com/@yourusername/video/{video_id}" if video_id else None
                
                return {
                    'success': True,
                    'video_id': video_id,
                    'publish_id': result.get('publish_id'),
                    'url': video_url,
                    'status': result.get('status', 'PROCESSING')
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Unknown error')
                }
                
        except Exception as e:
            logger.error(f"❌ TikTok upload error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def check_upload_status(self, publish_id: str) -> Dict[str, Any]:
        """Check if video has been published"""
        return await self.server.get_video_status(publish_id)
    
    async def close(self):
        """Close connections"""
        await self.server.close()


# Integration function for workflow
async def run_tiktok_upload(config: Dict[str, Any], video_url: str, 
                           pending_title: Dict[str, Any]) -> Dict[str, Any]:
    """Run TikTok upload from workflow"""
    
    # Check if TikTok is enabled
    if not config.get('tiktok_enabled', False):
        logger.info("TikTok upload disabled in config")
        return {'success': False, 'error': 'TikTok disabled'}
    
    try:
        # Initialize TikTok MCP
        tiktok = TikTokMCP(
            client_id=config.get('tiktok_client_id'),
            client_secret=config.get('tiktok_client_secret'),
            token_path=config.get('tiktok_token', '/home/claude-workflow/config/tiktok_token.json')
        )
        
        # Prepare content
        title = pending_title.get('VideoTitle', pending_title.get('Title', 'Check out these products!'))
        
        # Build description with products
        description = "Amazing products you need to see!\n\n"
        
        for i in range(1, 6):
            product_title = pending_title.get(f'ProductNo{i}Title', '')
            if product_title:
                description += f"#{i} {product_title}\n"
        
        description += "\n🔗 Links in bio!"
        
        # Prepare tags
        tags = ['amazonfinds', 'musthave', 'top5', 'review', '2025', 'viral']
        
        # Extract more tags from keywords if available
        keywords = pending_title.get('Keywords', '')
        if keywords:
            keyword_list = [k.strip() for k in keywords.split(',')][:5]
            tags.extend([k.replace(' ', '') for k in keyword_list])
        
        # Upload video
        result = await tiktok.upload_video(
            video_path=video_url,
            title=title,
            description=description,
            tags=tags,
            privacy_status=config.get('tiktok_privacy', 'PRIVATE')
        )
        
        await tiktok.close()
        
        return result
        
    except Exception as e:
        logger.error(f"❌ TikTok upload error: {e}")
        return {'success': False, 'error': str(e)}


# Test function
async def test_tiktok_upload():
    """Test TikTok upload"""
    config = {
        'tiktok_enabled': True,
        'tiktok_client_id': 'YOUR_CLIENT_ID',
        'tiktok_client_secret': 'YOUR_CLIENT_SECRET'
    }
    
    test_title = {
        'VideoTitle': '5 INSANE Gadgets You Need!',
        'ProductNo1Title': 'Smart Watch Pro',
        'ProductNo2Title': 'Wireless Earbuds X',
        'Keywords': 'gadgets, tech, smart home'
    }
    
    result = await run_tiktok_upload(
        config,
        'https://example.com/test-video.mp4',
        test_title
    )
    
    print(f"Result: {result}")

if __name__ == "__main__":
    asyncio.run(test_tiktok_upload())
