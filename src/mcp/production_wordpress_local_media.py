#!/usr/bin/env python3
"""
Production WordPress with Local Media Upload
============================================
This version uploads local media files to WordPress Media Library
and embeds them directly in the post content.
"""

import aiohttp
import base64
from typing import Dict, List, Optional
import logging
import asyncio
import json
import os
from pathlib import Path
import mimetypes

logger = logging.getLogger(__name__)


class ProductionWordPressLocalMedia:
    def __init__(self, config: Dict):
        self.config = config
        self.base_url = config.get('wordpress_url', 'https://reviewch3kr.com')
        self.username = config.get('wordpress_user', '')
        self.password = config.get('wordpress_password', '')
        
        # Create basic auth header
        credentials = f"{self.username}:{self.password}"
        self.auth_header = f"Basic {base64.b64encode(credentials.encode()).decode()}"
        
        # Local storage paths
        self.media_base_path = Path("/home/claude-workflow/media_storage")
        
        self.logger = logging.getLogger(__name__)
        
    async def create_post_with_local_media(self, record: Dict, config: Dict) -> Dict:
        """
        Create WordPress post with local media files
        Uploads all local media to WordPress and embeds in content
        """
        try:
            fields = record.get('fields', {})
            record_id = record.get('record_id', 'unknown')
            
            # Step 1: Upload all local media files to WordPress
            self.logger.info("📤 Uploading local media to WordPress...")
            media_urls = await self._upload_all_local_media(record_id, fields)
            
            # Step 2: Build enhanced content with embedded media
            content = await self._build_content_with_media(fields, media_urls)
            
            # Step 3: Prepare post data
            title = fields.get('WordPressTitle', fields.get('VideoTitle', 'Amazing Products'))
            
            # Build excerpt from first product
            excerpt = f"Discover the top 5 {fields.get('VideoTitle', 'products')} that will amaze you!"
            
            # Get tags from products
            tags = self._extract_tags(fields)
            
            # Step 4: Create the WordPress post
            post_data = {
                "title": title,
                "content": content,
                "excerpt": excerpt,
                "status": "publish",
                "tags": await self._get_or_create_tag_ids(tags),
                "categories": [1],  # Default category
                "comment_status": "open",
                "ping_status": "open"
            }
            
            # Set featured image (use first product image)
            if media_urls.get('product1_image'):
                featured_media_id = media_urls.get('product1_image_id')
                if featured_media_id:
                    post_data["featured_media"] = featured_media_id
            
            # Create the post
            url = f"{self.base_url}/wp-json/wp/v2/posts"
            headers = {
                "Authorization": self.auth_header,
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=post_data) as response:
                    if response.status in [200, 201]:
                        data = await response.json()
                        
                        self.logger.info(f"""
✅ WordPress Post Created Successfully!
- Post URL: {data.get('link', '')}
- Post ID: {data.get('id')}
- Media Uploaded: {len(media_urls)} files
""")
                        
                        # Update record with WordPress URL
                        if 'fields' not in record:
                            record['fields'] = {}
                        record['fields']['WordPressURL'] = data.get('link', '')
                        
                        return {
                            'success': True,
                            'post_id': data.get('id'),
                            'post_url': data.get('link', ''),
                            'media_uploaded': len(media_urls),
                            'updated_record': record
                        }
                    else:
                        error_text = await response.text()
                        self.logger.error(f"WordPress error: {error_text}")
                        return {
                            'success': False,
                            'error': f'WordPress API error: {response.status}',
                            'updated_record': record
                        }
                        
        except Exception as e:
            self.logger.error(f"❌ Error creating WordPress post: {e}")
            return {
                'success': False,
                'error': str(e),
                'updated_record': record
            }
    
    async def _upload_all_local_media(self, record_id: str, fields: Dict) -> Dict:
        """
        Upload all local media files to WordPress Media Library
        Returns dict with WordPress URLs for each media file
        """
        media_urls = {}
        
        # Find today's media directory
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        record_path = self.media_base_path / today
        
        # Define all media files to upload
        media_files = [
            # Images
            ('intro_image', f"images/{record_id}/intro.jpg", 'IntroPhoto'),
            ('outro_image', f"images/{record_id}/outro.jpg", 'OutroPhoto'),
            ('product1_image', f"images/{record_id}/product1.jpg", 'ProductNo1Photo'),
            ('product2_image', f"images/{record_id}/product2.jpg", 'ProductNo2Photo'),
            ('product3_image', f"images/{record_id}/product3.jpg", 'ProductNo3Photo'),
            ('product4_image', f"images/{record_id}/product4.jpg", 'ProductNo4Photo'),
            ('product5_image', f"images/{record_id}/product5.jpg", 'ProductNo5Photo'),
            
            # Audio files (optional - WordPress can embed audio players)
            ('intro_audio', f"audio/{record_id}/intro.mp3", 'IntroMp3'),
            ('product1_audio', f"audio/{record_id}/product1.mp3", 'Product1Mp3'),
            
            # Video file if exists
            ('final_video', f"videos/countdown_{record_id}.mp4", 'FinalVideo')
        ]
        
        for key, relative_path, field_name in media_files:
            file_path = record_path / relative_path
            
            # Check multiple possible locations
            if not file_path.exists():
                # Try without date subdirectory
                file_path = self.media_base_path / relative_path
            
            if not file_path.exists():
                # Try with different naming patterns
                if 'video' in key:
                    # Look for any video file for this record
                    video_pattern = f"countdown_{record_id}*.mp4"
                    video_dir = self.media_base_path / "videos"
                    if video_dir.exists():
                        for video_file in video_dir.glob(video_pattern):
                            file_path = video_file
                            break
            
            if file_path.exists():
                self.logger.info(f"📤 Uploading {key}: {file_path.name}")
                
                try:
                    # Upload to WordPress
                    wp_media = await self._upload_to_wordpress_media(file_path, key)
                    
                    if wp_media.get('success'):
                        media_urls[key] = wp_media['url']
                        media_urls[f"{key}_id"] = wp_media['media_id']
                        
                        # Also update the record field with WordPress URL
                        if field_name and field_name in fields:
                            fields[field_name] = wp_media['url']
                        
                        self.logger.info(f"✅ Uploaded {key} to WordPress: {wp_media['url']}")
                    else:
                        self.logger.warning(f"⚠️ Failed to upload {key}: {wp_media.get('error')}")
                        
                except Exception as e:
                    self.logger.warning(f"⚠️ Error uploading {key}: {e}")
            else:
                self.logger.debug(f"File not found: {file_path}")
        
        return media_urls
    
    async def _upload_to_wordpress_media(self, file_path: Path, media_key: str) -> Dict:
        """
        Upload a single file to WordPress Media Library
        """
        try:
            # Read file
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # Determine mime type
            mime_type, _ = mimetypes.guess_type(str(file_path))
            if not mime_type:
                if file_path.suffix == '.mp3':
                    mime_type = 'audio/mpeg'
                elif file_path.suffix == '.mp4':
                    mime_type = 'video/mp4'
                else:
                    mime_type = 'application/octet-stream'
            
            # Prepare upload
            url = f"{self.base_url}/wp-json/wp/v2/media"
            headers = {
                "Authorization": self.auth_header,
                "Content-Type": mime_type,
                "Content-Disposition": f'attachment; filename="{file_path.name}"'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, data=file_data) as response:
                    if response.status in [200, 201]:
                        data = await response.json()
                        return {
                            'success': True,
                            'media_id': data.get('id'),
                            'url': data.get('source_url', ''),
                            'guid': data.get('guid', {}).get('rendered', '')
                        }
                    else:
                        error_text = await response.text()
                        return {
                            'success': False,
                            'error': f'Upload failed: {response.status}'
                        }
                        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _build_content_with_media(self, fields: Dict, media_urls: Dict) -> str:
        """
        Build rich WordPress content with embedded media
        """
        content_parts = []
        
        # Add video at the top if available
        if media_urls.get('final_video'):
            content_parts.append(f"""
<!-- wp:video {{"id":0}} -->
<figure class="wp-block-video">
    <video controls src="{media_urls['final_video']}"></video>
    <figcaption>Watch our countdown of the top 5 products!</figcaption>
</figure>
<!-- /wp:video -->
""")
        
        # Add intro section with image
        if media_urls.get('intro_image'):
            content_parts.append(f"""
<!-- wp:image {{"sizeSlug":"large"}} -->
<figure class="wp-block-image size-large">
    <img src="{media_urls['intro_image']}" alt="Introduction"/>
</figure>
<!-- /wp:image -->
""")
        
        # Add intro text
        intro_text = fields.get('WordPressContent', '')
        if not intro_text:
            intro_text = f"Discover the amazing {fields.get('VideoTitle', 'products')} we've found for you!"
        
        content_parts.append(f"""
<!-- wp:paragraph -->
<p>{intro_text}</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>Top 5 Products Countdown</h2>
<!-- /wp:heading -->
""")
        
        # Add each product with rich formatting
        for i in range(5, 0, -1):  # Countdown from 5 to 1
            product_title = fields.get(f'ProductNo{i}Title', f'Product {i}')
            product_desc = fields.get(f'ProductNo{i}Description', '')
            product_price = fields.get(f'ProductNo{i}Price', '')
            product_rating = fields.get(f'ProductNo{i}Rating', '')
            product_reviews = fields.get(f'ProductNo{i}Reviews', '')
            product_link = fields.get(f'ProductNo{i}AffiliateLink', '')
            
            # Product section
            content_parts.append(f"""
<!-- wp:heading {{"level":3}} -->
<h3>#{6-i}. {product_title}</h3>
<!-- /wp:heading -->
""")
            
            # Product image
            if media_urls.get(f'product{i}_image'):
                content_parts.append(f"""
<!-- wp:image {{"sizeSlug":"medium","linkDestination":"custom"}} -->
<figure class="wp-block-image size-medium">
    <a href="{product_link}" target="_blank" rel="noopener noreferrer">
        <img src="{media_urls[f'product{i}_image']}" alt="{product_title}"/>
    </a>
</figure>
<!-- /wp:image -->
""")
            
            # Product details
            content_parts.append(f"""
<!-- wp:paragraph -->
<p><strong>Price:</strong> ${product_price}<br/>
<strong>Rating:</strong> ⭐ {product_rating}/5 ({product_reviews} reviews)</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>{product_desc}</p>
<!-- /wp:paragraph -->

<!-- wp:buttons -->
<div class="wp-block-buttons">
    <div class="wp-block-button">
        <a class="wp-block-button__link" href="{product_link}" target="_blank" rel="noopener noreferrer">
            🛒 Check Price on Amazon
        </a>
    </div>
</div>
<!-- /wp:buttons -->

<!-- wp:separator -->
<hr class="wp-block-separator"/>
<!-- /wp:separator -->
""")
        
        # Add outro section
        if media_urls.get('outro_image'):
            content_parts.append(f"""
<!-- wp:image {{"sizeSlug":"large"}} -->
<figure class="wp-block-image size-large">
    <img src="{media_urls['outro_image']}" alt="Thanks for reading!"/>
</figure>
<!-- /wp:image -->
""")
        
        # Add call to action
        content_parts.append("""
<!-- wp:paragraph -->
<p><strong>Thanks for checking out our top picks!</strong> Click any of the links above to see current prices and availability on Amazon.</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p><em>Note: As an Amazon Associate, we earn from qualifying purchases.</em></p>
<!-- /wp:paragraph -->
""")
        
        return '\n'.join(content_parts)
    
    def _extract_tags(self, fields: Dict) -> List[str]:
        """Extract tags from product data"""
        tags = []
        
        # Add main category as tag
        if fields.get('Category'):
            tags.append(fields['Category'])
        
        # Add subcategory
        if fields.get('SubCategory'):
            tags.append(fields['SubCategory'])
        
        # Add product-specific tags
        for i in range(1, 6):
            title = fields.get(f'ProductNo{i}Title', '')
            if title:
                # Extract key words from title (simple approach)
                words = title.lower().split()
                for word in words[:3]:  # Take first 3 words
                    if len(word) > 4 and word not in tags:
                        tags.append(word)
        
        # Limit to 10 tags
        return tags[:10]
    
    async def _get_or_create_tag_ids(self, tag_names: List[str]) -> List[int]:
        """Convert tag names to IDs, creating tags if they don't exist"""
        tag_ids = []
        
        for tag_name in tag_names:
            tag_name = tag_name.strip()
            if not tag_name:
                continue
            
            try:
                # Check if tag exists
                url = f"{self.base_url}/wp-json/wp/v2/tags"
                params = {"search": tag_name, "per_page": 1}
                
                headers = {"Authorization": self.auth_header}
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers, params=params) as response:
                        if response.status == 200:
                            tags = await response.json()
                            
                            if tags:
                                # Tag exists
                                tag_ids.append(tags[0]['id'])
                            else:
                                # Create new tag
                                create_url = f"{self.base_url}/wp-json/wp/v2/tags"
                                tag_data = {"name": tag_name}
                                
                                async with session.post(create_url, headers=headers, json=tag_data) as create_response:
                                    if create_response.status in [200, 201]:
                                        new_tag = await create_response.json()
                                        tag_ids.append(new_tag['id'])
                                        
            except Exception as e:
                self.logger.warning(f"Error handling tag '{tag_name}': {e}")
        
        return tag_ids


# Export main function
async def production_publish_to_wordpress_local(record: Dict, config: Dict) -> Dict:
    """Main entry point for WordPress publishing with local media"""
    publisher = ProductionWordPressLocalMedia(config)
    return await publisher.create_post_with_local_media(record, config)