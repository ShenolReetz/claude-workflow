#!/usr/bin/env python3
"""
TikTok Workflow Integration - Ready for when API is approved
"""

import asyncio
import json
import logging
import sys
sys.path.append('/home/claude-workflow')

from mcp_servers.Test_tiktok_server import TikTokMCPServer

logger = logging.getLogger(__name__)

class TikTokWorkflowIntegration:
    """TikTok integration for the main workflow"""
    
    def __init__(self, config: dict):
        self.config = config
        self.enabled = config.get('tiktok_enabled', False)
        
        if self.enabled:
            self.server = TikTokMCPServer(
                client_id=config['tiktok_client_id'],
                client_secret=config['tiktok_client_secret'],
                access_token=config.get('tiktok_access_token')
            )
        else:
            self.server = None
    
    async def upload_video_to_tiktok(self, airtable_record: dict) -> dict:
        """Upload video to TikTok with platform-specific optimization"""
        
        if not self.enabled:
            logger.info("TikTok upload disabled in config")
            return {"enabled": False, "skipped": True}
        
        try:
            # Get video data
            video_url = airtable_record.get('VideoURL') or airtable_record.get('GoogleDriveURL')
            if not video_url:
                return {"success": False, "error": "No video URL found"}
            
            # Generate TikTok-optimized title and description
            title = self._generate_tiktok_title(airtable_record)
            
            logger.info(f"📱 Uploading to TikTok: {title}")
            
            # Upload video
            result = await self.server.upload_video(
                video_path=video_url,
                title=title,
                privacy_level=self.config.get('tiktok_privacy', 'PRIVATE')
            )
            
            if result.get('success'):
                logger.info(f"✅ TikTok upload successful: {result.get('video_id')}")
                
                return {
                    "success": True,
                    "platform": "TikTok",
                    "video_id": result.get('video_id'),
                    "publish_id": result.get('publish_id'),
                    "status": result.get('status'),
                    "title": title
                }
            else:
                logger.error(f"❌ TikTok upload failed: {result.get('error')}")
                return {
                    "success": False,
                    "platform": "TikTok",
                    "error": result.get('error')
                }
                
        except Exception as e:
            logger.error(f"❌ TikTok upload error: {e}")
            return {
                "success": False,
                "platform": "TikTok",
                "error": str(e)
            }
    
    def _generate_tiktok_title(self, airtable_record: dict) -> str:
        """Generate TikTok-optimized title with trending elements"""
        
        original_title = airtable_record.get('VideoTitle', 'Top 5 Products')
        
        # Extract TikTok keywords from Airtable if available
        tiktok_keywords = airtable_record.get('TikTokKeywords', '')
        
        # Generate Gen Z optimized title
        base_title = original_title.replace('🔥', '').replace('🚗', '').strip()
        
        # TikTok-specific optimizations
        tiktok_title = f"POV: You need these products! {base_title[:80]} #fyp #viral"
        
        # Add trending hashtags if available
        if tiktok_keywords:
            keywords_list = tiktok_keywords.split(',')[:3]  # Max 3 keywords
            hashtags = ' '.join([f"#{kw.strip().replace(' ', '')}" for kw in keywords_list])
            tiktok_title = f"{base_title[:100]} {hashtags} #fyp"
        
        # Ensure title is under TikTok's 150 character limit
        return tiktok_title[:150]
    
    async def check_upload_status(self, publish_id: str) -> dict:
        """Check the status of a TikTok upload"""
        
        if not self.enabled or not self.server:
            return {"enabled": False}
        
        try:
            result = await self.server.get_video_status(publish_id)
            return result
        except Exception as e:
            logger.error(f"❌ Error checking TikTok status: {e}")
            return {"error": str(e)}
    
    async def close(self):
        """Close TikTok server connection"""
        if self.server:
            await self.server.close()

# Integration function for workflow_runner.py
async def upload_to_tiktok(config: dict, airtable_record: dict) -> dict:
    """Upload video to TikTok - integration point for main workflow"""
    
    tiktok_integration = TikTokWorkflowIntegration(config)
    
    try:
        result = await tiktok_integration.upload_video_to_tiktok(airtable_record)
        return result
    finally:
        await tiktok_integration.close()

# Test function
async def test_tiktok_integration():
    """Test TikTok integration with sample data"""
    
    print("📱 Testing TikTok Workflow Integration")
    print("=" * 50)
    
    # Load config
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    # Sample Airtable record
    test_record = {
        'VideoTitle': '🔥 Top 5 Gaming Headsets You NEED in 2025! 🎮',
        'VideoURL': 'https://example.com/test-video.mp4',
        'TikTokKeywords': 'gaming, headsets, tech, viral',
        'record_id': 'test123'
    }
    
    integration = TikTokWorkflowIntegration(config)
    
    if not integration.enabled:
        print("⚠️  TikTok is disabled in config")
        print("📝 To enable:")
        print("   1. Get app approval from TikTok")
        print("   2. Complete authentication flow")
        print("   3. Set tiktok_enabled: true in config")
        return
    
    # Test title generation
    title = integration._generate_tiktok_title(test_record)
    print(f"📝 Generated TikTok title: {title}")
    print(f"   Length: {len(title)}/150 characters")
    
    # Test upload (will fail without proper auth, but shows the flow)
    print(f"\n🧪 Testing upload flow...")
    result = await integration.upload_video_to_tiktok(test_record)
    print(f"📊 Result: {result}")
    
    await integration.close()

if __name__ == "__main__":
    asyncio.run(test_tiktok_integration())