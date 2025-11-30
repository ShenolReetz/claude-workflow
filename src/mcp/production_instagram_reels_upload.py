#!/usr/bin/env python3
"""
Production Instagram Reels Upload Module
========================================
Uploads video content to Instagram Reels via Instagram Graph API
Requires Business or Creator account with proper permissions
"""

import asyncio
import aiohttp
import json
import logging
import time
from typing import Dict, List, Optional
from pathlib import Path
import hashlib
import re

logger = logging.getLogger(__name__)


class InstagramReelsUploader:
    """
    Instagram Reels uploader using Instagram Graph API
    Handles video upload, caption generation, and hashtag optimization
    """
    
    def __init__(self, config: Dict):
        self.config = config
        
        # Instagram API credentials
        self.access_token = config.get('instagram_access_token')
        self.instagram_id = config.get('instagram_id')
        self.app_id = config.get('instagram_app_id')
        
        # API endpoints
        self.base_url = "https://graph.facebook.com/v18.0"
        self.upload_endpoint = f"{self.base_url}/{self.instagram_id}/media"
        self.publish_endpoint = f"{self.base_url}/{self.instagram_id}/media_publish"
        
        # Hashtag configuration
        self.max_hashtags = 30
        self.base_hashtags = [
            "#amazonfinds", "#amazonmusthaves", "#amazonfavorites",
            "#amazonproducts", "#amazondeals", "#amazonshopping",
            "#onlineshopping", "#musthave", "#trending", "#viral",
            "#reels", "#reelsinstagram", "#reelsvideo", "#explorepage"
        ]
        
        logger.info("""
╔════════════════════════════════════════════════════════════╗
║  📱 INSTAGRAM REELS UPLOADER INITIALIZED                  ║
║  Platform: Instagram Reels                                ║
║  Format: 9:16 vertical video                             ║
║  Duration: 15-60 seconds                                 ║
╚════════════════════════════════════════════════════════════╝
""")
    
    async def upload_reel(self, 
                         video_path: str, 
                         record: Dict,
                         video_url: Optional[str] = None) -> Dict:
        """
        Upload video to Instagram Reels
        
        Args:
            video_path: Local path to video file
            record: Airtable record with product data
            video_url: Optional public URL if video is hosted
        
        Returns:
            Dict with upload status and reel ID
        """
        try:
            fields = record.get('fields', {})
            
            logger.info("📱 Starting Instagram Reels upload...")
            
            # Generate caption and hashtags
            caption = self._generate_caption(fields)
            hashtags = self._generate_hashtags(fields)
            full_caption = f"{caption}\n\n{' '.join(hashtags)}"
            
            # Ensure caption doesn't exceed Instagram limit (2200 chars)
            if len(full_caption) > 2200:
                full_caption = full_caption[:2197] + "..."
            
            logger.info(f"📝 Caption length: {len(full_caption)} chars")
            logger.info(f"#️⃣ Hashtags: {len(hashtags)} tags")
            
            # Step 1: Create media container
            container_id = await self._create_media_container(
                video_url or video_path,
                full_caption,
                is_url=(video_url is not None)
            )
            
            if not container_id:
                return {
                    'success': False,
                    'error': 'Failed to create media container'
                }
            
            logger.info(f"📦 Media container created: {container_id}")
            
            # Step 2: Wait for processing
            if await self._wait_for_processing(container_id):
                logger.info("✅ Media processing complete")
            else:
                return {
                    'success': False,
                    'error': 'Media processing timeout'
                }
            
            # Step 3: Publish reel
            reel_id = await self._publish_reel(container_id)
            
            if reel_id:
                logger.info(f"🎉 Reel published successfully! ID: {reel_id}")
                
                # Get reel permalink
                permalink = await self._get_reel_permalink(reel_id)
                
                return {
                    'success': True,
                    'reel_id': reel_id,
                    'permalink': permalink,
                    'caption_length': len(full_caption),
                    'hashtag_count': len(hashtags)
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to publish reel'
                }
                
        except Exception as e:
            logger.error(f"Instagram upload error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_caption(self, fields: Dict) -> str:
        """
        Generate engaging caption from product data
        """
        video_title = fields.get('VideoTitle', 'Amazing Products')
        
        # Build engaging caption
        caption_parts = [
            f"🔥 {video_title} - Top 5 Countdown!",
            "",
            "Which one is your favorite? Comment below! 👇"
        ]
        
        # Add numbered product list
        for i in range(1, 6):
            product_title = fields.get(f'ProductNo{i}Title', '')
            if product_title:
                # Truncate long titles
                if len(product_title) > 50:
                    product_title = product_title[:47] + "..."
                caption_parts.append(f"{i}️⃣ {product_title}")
        
        caption_parts.extend([
            "",
            "💡 Swipe up for links (in bio)!",
            "❤️ Double tap if you found this helpful!",
            "📤 Share with someone who needs this!",
            "",
            "Follow for daily product recommendations! 🛍️"
        ])
        
        return "\n".join(caption_parts)
    
    def _generate_hashtags(self, fields: Dict) -> List[str]:
        """
        Generate optimized hashtags for maximum reach
        """
        hashtags = self.base_hashtags.copy()
        
        # Extract category-specific hashtags
        category = fields.get('ExtractedCategory', '')
        if category:
            # Clean and format category
            category_clean = re.sub(r'[^a-zA-Z0-9\s]', '', category.lower())
            category_words = category_clean.split()[:3]
            
            for word in category_words:
                if len(word) > 3:
                    hashtags.append(f"#{word}")
                    hashtags.append(f"#{word}lover")
        
        # Add product-specific hashtags
        for i in range(1, 6):
            product_title = fields.get(f'ProductNo{i}Title', '')
            if product_title:
                # Extract key product terms
                product_words = re.findall(r'\b[A-Z][a-z]+\b', product_title)
                for word in product_words[:2]:
                    if len(word) > 4:
                        hashtags.append(f"#{word.lower()}")
        
        # Add trending hashtags
        trending = [
            "#fyp", "#foryou", "#foryoupage", "#explore",
            "#instagood", "#instagram", "#instadaily",
            "#love", "#fashion", "#style", "#shopping"
        ]
        
        hashtags.extend(trending)
        
        # Remove duplicates and limit to 30
        unique_hashtags = []
        seen = set()
        for tag in hashtags:
            tag_lower = tag.lower()
            if tag_lower not in seen and len(unique_hashtags) < self.max_hashtags:
                unique_hashtags.append(tag)
                seen.add(tag_lower)
        
        return unique_hashtags
    
    async def _create_media_container(self, 
                                     video_source: str,
                                     caption: str,
                                     is_url: bool = False) -> Optional[str]:
        """
        Create media container for reel upload
        """
        try:
            params = {
                'access_token': self.access_token,
                'caption': caption,
                'media_type': 'REELS',
                'share_to_feed': 'true',  # Also share to main feed
                'thumb_offset': '2000'  # Thumbnail at 2 seconds
            }
            
            if is_url:
                params['video_url'] = video_source
            else:
                # For local files, need to upload to a public URL first
                # This would require additional implementation
                logger.warning("Local file upload requires public URL hosting")
                return None
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.upload_endpoint, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('id')
                    else:
                        error = await response.text()
                        logger.error(f"Container creation failed: {error}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error creating media container: {e}")
            return None
    
    async def _wait_for_processing(self, 
                                  container_id: str,
                                  max_attempts: int = 60) -> bool:
        """
        Wait for Instagram to process the uploaded video
        """
        check_url = f"{self.base_url}/{container_id}"
        
        for attempt in range(max_attempts):
            try:
                async with aiohttp.ClientSession() as session:
                    params = {
                        'access_token': self.access_token,
                        'fields': 'status,status_code'
                    }
                    
                    async with session.get(check_url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            status = data.get('status_code')
                            
                            if status == 'FINISHED':
                                return True
                            elif status == 'ERROR':
                                logger.error(f"Processing error: {data}")
                                return False
                            
                            # Still processing
                            logger.info(f"⏳ Processing... ({attempt+1}/{max_attempts})")
                            
            except Exception as e:
                logger.error(f"Error checking status: {e}")
            
            await asyncio.sleep(2)  # Wait 2 seconds between checks
        
        logger.error("Processing timeout")
        return False
    
    async def _publish_reel(self, container_id: str) -> Optional[str]:
        """
        Publish the processed reel
        """
        try:
            params = {
                'access_token': self.access_token,
                'creation_id': container_id
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.publish_endpoint, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('id')
                    else:
                        error = await response.text()
                        logger.error(f"Publish failed: {error}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error publishing reel: {e}")
            return None
    
    async def _get_reel_permalink(self, reel_id: str) -> Optional[str]:
        """
        Get the permalink for the published reel
        """
        try:
            url = f"{self.base_url}/{reel_id}"
            params = {
                'access_token': self.access_token,
                'fields': 'permalink'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('permalink')
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting permalink: {e}")
            return None
    
    async def upload_video_via_hosting(self,
                                       local_video_path: str,
                                       record: Dict) -> Dict:
        """
        Upload video by first hosting it publicly
        This requires a hosting solution (e.g., temporary S3, CDN, etc.)
        """
        # TODO: Implement video hosting solution
        # Options:
        # 1. Upload to temporary S3 bucket
        # 2. Use WordPress media library URL
        # 3. Use YouTube unlisted video URL
        
        logger.warning("Video hosting implementation needed for local files")
        
        # For now, return error
        return {
            'success': False,
            'error': 'Video hosting not yet implemented'
        }


# Export function for workflow integration
async def production_upload_to_instagram(record: Dict, config: Dict) -> Dict:
    """
    Main entry point for Instagram Reels upload
    """
    try:
        uploader = InstagramReelsUploader(config)
        
        # Get video path
        fields = record.get('fields', {})
        video_path = fields.get('VideoPath_Local')
        
        if not video_path or not Path(video_path).exists():
            logger.error("Video file not found for Instagram upload")
            return {
                'success': False,
                'error': 'Video file not found'
            }
        
        # Check if we have a public URL for the video
        video_url = fields.get('VideoURL')  # If video is hosted publicly
        
        if video_url:
            # Use public URL
            result = await uploader.upload_reel(
                video_path=video_path,
                record=record,
                video_url=video_url
            )
        else:
            # Need to host video first
            result = await uploader.upload_video_via_hosting(
                local_video_path=video_path,
                record=record
            )
        
        if result.get('success'):
            logger.info("""
════════════════════════════════════════
📱 INSTAGRAM UPLOAD COMPLETE
════════════════════════════════════════
✅ Reel ID: {reel_id}
🔗 URL: {permalink}
📝 Caption: {caption_length} chars
#️⃣ Hashtags: {hashtag_count} tags
════════════════════════════════════════
""".format(**result))
        
        return result
        
    except Exception as e:
        logger.error(f"Instagram upload failed: {e}")
        return {
            'success': False,
            'error': str(e)
        }