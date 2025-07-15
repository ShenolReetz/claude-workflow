#!/usr/bin/env python3
"""
Instagram Workflow Integration - Ready for when API is approved
"""

import asyncio
import json
import logging
import sys
sys.path.append('/home/claude-workflow')

from mcp_servers.instagram_server import InstagramMCPServer

logger = logging.getLogger(__name__)

class InstagramWorkflowIntegration:
    """Instagram integration for the main workflow"""
    
    def __init__(self, config: dict):
        self.config = config
        self.enabled = config.get('instagram_enabled', False)
        
        if self.enabled:
            self.server = InstagramMCPServer(
                app_id=config['instagram_app_id'],
                app_secret=config['instagram_app_secret'],
                access_token=config.get('instagram_access_token')
            )
        else:
            self.server = None
    
    async def upload_reel_to_instagram(self, airtable_record: dict) -> dict:
        """Upload video as Instagram Reel with platform-specific optimization"""
        
        if not self.enabled:
            logger.info("Instagram upload disabled in config")
            return {"enabled": False, "skipped": True}
        
        try:
            # Get video data from FinalVideo field
            video_url = airtable_record.get('FinalVideo')
            if not video_url:
                return {"success": False, "error": "No final video URL found"}
            
            # Generate Instagram-optimized caption
            caption = self._generate_instagram_caption(airtable_record)
            
            # Get cover image (first product image as cover)
            cover_url = self._get_cover_image(airtable_record)
            
            logger.info(f"📸 Uploading to Instagram Reels: {caption[:50]}...")
            
            # Upload reel
            result = await self.server.upload_reel(
                video_path=video_url,
                caption=caption,
                cover_url=cover_url
            )
            
            if result.get('success'):
                logger.info(f"✅ Instagram Reel upload successful: {result.get('media_id')}")
                
                return {
                    "success": True,
                    "platform": "Instagram",
                    "media_id": result.get('media_id'),
                    "instagram_url": result.get('instagram_url'),
                    "caption": caption
                }
            else:
                logger.error(f"❌ Instagram upload failed: {result.get('error')}")
                return {
                    "success": False,
                    "platform": "Instagram",
                    "error": result.get('error')
                }
                
        except Exception as e:
            logger.error(f"❌ Instagram upload error: {e}")
            return {
                "success": False,
                "platform": "Instagram",
                "error": str(e)
            }
    
    def _generate_instagram_caption(self, airtable_record: dict) -> str:
        """Generate Instagram-optimized caption with visual storytelling"""
        
        original_title = airtable_record.get('VideoTitle', 'Top 5 Products')
        
        # Extract Instagram hashtags from Airtable if available
        instagram_hashtags = airtable_record.get('InstagramHashtags', '')
        
        # Generate visually appealing caption
        base_title = original_title.replace('🔥', '').replace('🚗', '').strip()
        
        # Instagram-specific optimizations with visual storytelling
        caption_parts = []
        
        # Hook line
        caption_parts.append(f"✨ {base_title} ✨")
        caption_parts.append("")
        
        # Visual storytelling intro
        caption_parts.append("Swipe to see our top picks! 👆")
        caption_parts.append("")
        
        # Add product preview if available
        products = []
        for i in range(1, 6):
            title = airtable_record.get(f'ProductNo{i}Title')
            if title:
                products.append(f"{6-i}️⃣ {title}")
        
        if products:
            caption_parts.append("What's in this reel:")
            caption_parts.extend(products[:3])  # Show first 3
            if len(products) > 3:
                caption_parts.append(f"...and {len(products)-3} more!")
            caption_parts.append("")
        
        # Call to action
        caption_parts.append("💝 Save this post for later!")
        caption_parts.append("🔗 Links in bio for best deals")
        caption_parts.append("👇 Tell us your favorite in comments!")
        caption_parts.append("")
        
        # Add hashtags
        if instagram_hashtags:
            # Use provided hashtags
            hashtags = instagram_hashtags
        else:
            # Generate default hashtags
            hashtags = self._generate_default_hashtags(airtable_record)
        
        caption_parts.append(hashtags)
        
        # Join all parts
        caption = "\n".join(caption_parts)
        
        # Ensure caption is under Instagram's 2200 character limit
        return caption[:2200]
    
    def _generate_default_hashtags(self, airtable_record: dict) -> str:
        """Generate default Instagram hashtags"""
        
        title = airtable_record.get('VideoTitle', '').lower()
        hashtags = ["#reels", "#top5", "#productreview", "#mustave", "#shopping"]
        
        # Category-specific hashtags
        if 'gaming' in title:
            hashtags.extend(["#gaming", "#gamingsetup", "#tech", "#pcgaming"])
        elif 'car' in title or 'audio' in title:
            hashtags.extend(["#caraudio", "#bass", "#automotive", "#soundsystem"])
        elif 'laptop' in title or 'computer' in title:
            hashtags.extend(["#laptop", "#tech", "#productivity", "#workfromhome"])
        elif 'headset' in title or 'headphone' in title:
            hashtags.extend(["#headphones", "#audio", "#music", "#sound"])
        
        # Add engagement hashtags
        hashtags.extend(["#amazon", "#deals", "#affiliate", "#recommendations"])
        
        # Format as Instagram hashtags
        return " ".join(hashtags[:30])  # Instagram allows up to 30 hashtags
    
    def _get_cover_image(self, airtable_record: dict) -> str:
        """Get cover image for the reel (first product image)"""
        
        # Try to get the first available product image
        for i in range(1, 6):
            image_url = airtable_record.get(f'ProductNo{i}Photo')
            if image_url:
                return image_url
        
        # Return None if no images found
        return None
    
    async def get_reel_stats(self, media_id: str) -> dict:
        """Get Instagram Reel statistics"""
        
        if not self.enabled or not self.server:
            return {"enabled": False}
        
        try:
            result = await self.server.get_media_info(media_id)
            return result
        except Exception as e:
            logger.error(f"❌ Error getting Instagram stats: {e}")
            return {"error": str(e)}
    
    async def close(self):
        """Close Instagram server connection"""
        if self.server:
            await self.server.close()

# Integration function for workflow_runner.py
async def upload_to_instagram(config: dict, airtable_record: dict) -> dict:
    """Upload video to Instagram - integration point for main workflow"""
    
    instagram_integration = InstagramWorkflowIntegration(config)
    
    try:
        result = await instagram_integration.upload_reel_to_instagram(airtable_record)
        return result
    finally:
        await instagram_integration.close()

# Test function
async def test_instagram_integration():
    """Test Instagram integration with sample data"""
    
    print("📸 Testing Instagram Workflow Integration")
    print("=" * 50)
    
    # Load config
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    # Sample Airtable record
    test_record = {
        'VideoTitle': '🔥 Top 5 Gaming Headsets You NEED in 2025! 🎮',
        'VideoURL': 'https://example.com/test-video.mp4',
        'InstagramHashtags': '#gaming #headsets #tech #reels #top5 #mustbuy #gamingsetup',
        'ProductNo1Title': 'SteelSeries Arctis Nova Pro',
        'ProductNo1Photo': 'https://example.com/headset1.jpg',
        'ProductNo2Title': 'Razer BlackShark V2 Pro',
        'ProductNo2Photo': 'https://example.com/headset2.jpg',
        'record_id': 'test123'
    }
    
    integration = InstagramWorkflowIntegration(config)
    
    if not integration.enabled:
        print("⚠️  Instagram is disabled in config")
        print("📝 To enable:")
        print("   1. Get app approval from Instagram/Facebook")
        print("   2. Complete authentication flow")
        print("   3. Set instagram_enabled: true in config")
        return
    
    # Test caption generation
    caption = integration._generate_instagram_caption(test_record)
    print(f"📝 Generated Instagram caption:")
    print(f"   Length: {len(caption)}/2200 characters")
    print(f"   Preview: {caption[:200]}...")
    
    # Test cover image selection
    cover = integration._get_cover_image(test_record)
    print(f"🖼️  Cover image: {cover}")
    
    # Test upload (will fail without proper auth, but shows the flow)
    print(f"\n🧪 Testing upload flow...")
    result = await integration.upload_reel_to_instagram(test_record)
    print(f"📊 Result: {result}")
    
    await integration.close()

if __name__ == "__main__":
    asyncio.run(test_instagram_integration())