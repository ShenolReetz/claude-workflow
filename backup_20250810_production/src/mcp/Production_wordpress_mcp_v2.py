#!/usr/bin/env python3
"""
Production WordPress MCP V2 - Enhanced WordPress Publishing
===========================================================

Improvements:
- Proper tag ID management (create tags if they don't exist)
- Category management
- Featured image support
- Better error handling
- Retry logic
"""

import aiohttp
import base64
from typing import Dict, List, Optional, Union
import logging
import asyncio
import json

class ProductionWordPressMCPV2:
    def __init__(self, config: Dict):
        self.config = config
        self.base_url = config.get('wordpress_url', 'https://reviewch3kr.com')
        self.username = config.get('wordpress_user', '')
        self.password = config.get('wordpress_password', '')
        
        # Create basic auth header
        credentials = f"{self.username}:{self.password}"
        self.auth_header = f"Basic {base64.b64encode(credentials.encode()).decode()}"
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Cache for tag and category IDs
        self.tag_cache = {}
        self.category_cache = {}
        
        # Retry configuration
        self.max_retries = 3
        self.retry_delay = 2
    
    async def create_post(self, title: str, content: str, excerpt: str, tags: List[str], 
                         categories: Optional[List[str]] = None, featured_image_url: Optional[str] = None) -> Dict:
        """Create a WordPress post with proper tag and category handling"""
        try:
            # Convert tag names to IDs
            tag_ids = await self._get_or_create_tag_ids(tags)
            
            # Convert category names to IDs (if provided)
            category_ids = [1]  # Default category
            if categories:
                category_ids = await self._get_or_create_category_ids(categories)
            
            # Upload featured image if provided
            featured_media_id = None
            if featured_image_url:
                featured_media_id = await self._upload_featured_image(featured_image_url, title)
            
            # Build post data with proper WordPress REST API format
            post_data = {
                "title": title,
                "content": content,
                "excerpt": excerpt,
                "status": "publish",
                "tags": tag_ids,  # Use tag IDs instead of names
                "categories": category_ids,
                "comment_status": "open",
                "ping_status": "open"
            }
            
            # Add featured image if available
            if featured_media_id:
                post_data["featured_media"] = featured_media_id
            
            # Create post with retry logic
            for attempt in range(self.max_retries):
                try:
                    url = f"{self.base_url}/wp-json/wp/v2/posts"
                    
                    headers = {
                        "Authorization": self.auth_header,
                        "Content-Type": "application/json"
                    }
                    
                    async with aiohttp.ClientSession() as session:
                        async with session.post(url, headers=headers, json=post_data) as response:
                            if response.status in [200, 201]:
                                data = await response.json()
                                self.logger.info(f"✅ WordPress post created: {data.get('link', '')}")
                                
                                return {
                                    'success': True,
                                    'post_id': data.get('id'),
                                    'post_url': data.get('link', ''),
                                    'guid': data.get('guid', {}).get('rendered', '')
                                }
                            else:
                                error_text = await response.text()
                                self.logger.warning(f"WordPress API error (attempt {attempt + 1}): {response.status}")
                                self.logger.debug(f"Error details: {error_text}")
                                
                                # Parse error to provide better feedback
                                try:
                                    error_json = json.loads(error_text)
                                    error_message = error_json.get('message', 'Unknown error')
                                    
                                    # Handle specific errors
                                    if 'tags[0] is not of type integer' in error_message:
                                        self.logger.error("Tag format error - tags must be integers")
                                        # Clear tag cache and retry
                                        self.tag_cache = {}
                                        tag_ids = await self._get_or_create_tag_ids(tags)
                                        post_data['tags'] = tag_ids
                                    
                                except json.JSONDecodeError:
                                    pass
                                
                                if attempt < self.max_retries - 1:
                                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                                else:
                                    return {
                                        'success': False,
                                        'error': f'API error after {self.max_retries} attempts: {response.status}'
                                    }
                                    
                except aiohttp.ClientError as e:
                    self.logger.warning(f"Connection error (attempt {attempt + 1}): {e}")
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(self.retry_delay)
                    else:
                        raise
                        
        except Exception as e:
            self.logger.error(f"❌ Error creating WordPress post: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _get_or_create_tag_ids(self, tag_names: List[str]) -> List[int]:
        """Convert tag names to IDs, creating tags if they don't exist"""
        tag_ids = []
        
        for tag_name in tag_names:
            # Clean up the tag name
            tag_name = tag_name.strip() if isinstance(tag_name, str) else ''
            if not tag_name:
                continue
                
            # Check cache first
            if tag_name in self.tag_cache:
                tag_ids.append(self.tag_cache[tag_name])
                continue
            
            # Search for existing tag
            tag_id = await self._search_tag(tag_name)
            
            # Create tag if it doesn't exist
            if not tag_id:
                tag_id = await self._create_tag(tag_name)
            
            if tag_id:
                self.tag_cache[tag_name] = tag_id
                tag_ids.append(tag_id)
                
        return tag_ids
    
    async def _search_tag(self, tag_name: str) -> Optional[int]:
        """Search for an existing tag by name"""
        try:
            url = f"{self.base_url}/wp-json/wp/v2/tags"
            params = {"search": tag_name, "per_page": 100}
            
            headers = {
                "Authorization": self.auth_header
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        tags = await response.json()
                        for tag in tags:
                            if tag.get('name', '').lower() == tag_name.lower():
                                return tag.get('id')
            return None
            
        except Exception as e:
            self.logger.warning(f"Error searching for tag '{tag_name}': {e}")
            return None
    
    async def _create_tag(self, tag_name: str) -> Optional[int]:
        """Create a new tag"""
        try:
            url = f"{self.base_url}/wp-json/wp/v2/tags"
            
            headers = {
                "Authorization": self.auth_header,
                "Content-Type": "application/json"
            }
            
            data = {
                "name": tag_name,
                "slug": tag_name.lower().replace(' ', '-')
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data) as response:
                    if response.status in [200, 201]:
                        tag_data = await response.json()
                        self.logger.info(f"✅ Created tag: {tag_name} (ID: {tag_data.get('id')})")
                        return tag_data.get('id')
                    else:
                        self.logger.warning(f"Failed to create tag '{tag_name}': {response.status}")
                        return None
                        
        except Exception as e:
            self.logger.error(f"Error creating tag '{tag_name}': {e}")
            return None
    
    async def _get_or_create_category_ids(self, category_names: List[str]) -> List[int]:
        """Convert category names to IDs, creating categories if they don't exist"""
        category_ids = []
        
        for category_name in category_names:
            if not category_name:
                continue
                
            # Check cache first
            if category_name in self.category_cache:
                category_ids.append(self.category_cache[category_name])
                continue
            
            # Search for existing category
            category_id = await self._search_category(category_name)
            
            # Create category if it doesn't exist
            if not category_id:
                category_id = await self._create_category(category_name)
            
            if category_id:
                self.category_cache[category_name] = category_id
                category_ids.append(category_id)
                
        return category_ids if category_ids else [1]  # Default to uncategorized
    
    async def _search_category(self, category_name: str) -> Optional[int]:
        """Search for an existing category by name"""
        try:
            url = f"{self.base_url}/wp-json/wp/v2/categories"
            params = {"search": category_name, "per_page": 100}
            
            headers = {
                "Authorization": self.auth_header
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        categories = await response.json()
                        for category in categories:
                            if category.get('name', '').lower() == category_name.lower():
                                return category.get('id')
            return None
            
        except Exception as e:
            self.logger.warning(f"Error searching for category '{category_name}': {e}")
            return None
    
    async def _create_category(self, category_name: str) -> Optional[int]:
        """Create a new category"""
        try:
            url = f"{self.base_url}/wp-json/wp/v2/categories"
            
            headers = {
                "Authorization": self.auth_header,
                "Content-Type": "application/json"
            }
            
            data = {
                "name": category_name,
                "slug": category_name.lower().replace(' ', '-')
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data) as response:
                    if response.status in [200, 201]:
                        category_data = await response.json()
                        self.logger.info(f"✅ Created category: {category_name} (ID: {category_data.get('id')})")
                        return category_data.get('id')
                    else:
                        self.logger.warning(f"Failed to create category '{category_name}': {response.status}")
                        return None
                        
        except Exception as e:
            self.logger.error(f"Error creating category '{category_name}': {e}")
            return None
    
    async def _upload_featured_image(self, image_url: str, alt_text: str = "") -> Optional[int]:
        """Upload an image to WordPress media library"""
        try:
            # Download image first
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as response:
                    if response.status != 200:
                        return None
                    
                    image_data = await response.read()
                    content_type = response.headers.get('content-type', 'image/jpeg')
            
            # Upload to WordPress
            url = f"{self.base_url}/wp-json/wp/v2/media"
            
            headers = {
                "Authorization": self.auth_header,
                "Content-Type": content_type,
                "Content-Disposition": f'attachment; filename="featured-{hash(image_url)}.jpg"'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, data=image_data) as response:
                    if response.status in [200, 201]:
                        media_data = await response.json()
                        media_id = media_data.get('id')
                        
                        # Update alt text if provided
                        if alt_text and media_id:
                            await self._update_media_alt_text(media_id, alt_text)
                        
                        self.logger.info(f"✅ Uploaded featured image (ID: {media_id})")
                        return media_id
                    else:
                        self.logger.warning(f"Failed to upload featured image: {response.status}")
                        return None
                        
        except Exception as e:
            self.logger.error(f"Error uploading featured image: {e}")
            return None
    
    async def _update_media_alt_text(self, media_id: int, alt_text: str):
        """Update media alt text"""
        try:
            url = f"{self.base_url}/wp-json/wp/v2/media/{media_id}"
            
            headers = {
                "Authorization": self.auth_header,
                "Content-Type": "application/json"
            }
            
            data = {
                "alt_text": alt_text,
                "caption": alt_text
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data) as response:
                    if response.status in [200, 201]:
                        self.logger.info(f"✅ Updated media alt text")
                        
        except Exception as e:
            self.logger.warning(f"Error updating media alt text: {e}")