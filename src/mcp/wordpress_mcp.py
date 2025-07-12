# src/mcp/wordpress_mcp.py
import requests
import json
import base64
import logging
from typing import Dict, Optional
import asyncio

logger = logging.getLogger(__name__)

class WordPressMCP:
    """WordPress MCP for automated blog post creation"""
    
    def __init__(self, config: Dict):
        self.base_url = config.get('wordpress_url', 'https://reviewch3kr.com')
        self.username = config.get('wordpress_user', '')
        self.password = config.get('wordpress_password', '')
        self.enabled = config.get('wordpress_enabled', True)
        
        # Create auth header
        credentials = f"{self.username}:{self.password}"
        self.auth_header = f"Basic {base64.b64encode(credentials.encode()).decode()}"
        
        # API endpoints
        self.posts_endpoint = f"{self.base_url}/wp-json/wp/v2/posts"
        self.categories_endpoint = f"{self.base_url}/wp-json/wp/v2/categories"
        
    async def create_review_post(self, airtable_data: Dict) -> Dict:
        """Create a WordPress post from Airtable data"""
        
        if not self.enabled:
            logger.info("WordPress publishing is disabled")
            return {"enabled": False}
            
        try:
            # Generate post content
            content = self._generate_post_content(airtable_data)
            
            # Get or create category
            category_id = await self._get_or_create_category("Product Reviews")
            
            # Create post data with homepage visibility fixes
            post_data = {
                'title': airtable_data.get('VideoTitle', 'Product Review'),
                'content': content,
                'status': 'publish',
                'categories': [category_id],
                'excerpt': airtable_data.get('VideoDescription', '')[:155] + '...',  # SEO-friendly excerpt length
                'format': 'standard',  # Ensure standard post format
                'type': 'post',  # Explicitly set as blog post
                'comment_status': 'open',  # Enable comments for engagement
                'ping_status': 'open',  # Enable pingbacks
                'sticky': False,  # Don't make sticky by default
                'template': '',  # Use default template
                'meta': {
                    '_thumbnail_id': 0,  # Will be updated if featured image is set
                    'post_views_count': '0'  # Initialize view counter
                }
            }
            
            # Make API request
            headers = {
                'Authorization': self.auth_header,
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                self.posts_endpoint,
                headers=headers,
                json=post_data
            )
            
            if response.status_code == 201:
                result = response.json()
                logger.info(f"Successfully created WordPress post: {result['link']}")
                
                # Additional homepage visibility steps
                post_id = result['id']
                await self._enhance_post_visibility(post_id, airtable_data)
                
                return {
                    'success': True,
                    'post_id': post_id,
                    'post_url': result['link'],
                    'status': result['status']
                }
            else:
                logger.error(f"Failed to create post: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f"Status {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            logger.error(f"Error creating WordPress post: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_post_content(self, data: Dict) -> str:
        """Generate formatted post content with affiliate links"""
        
        # Start with introduction
        content = f"""
        <div class="review-intro">
            <p>{data.get('VideoDescription', '')}</p>
        </div>
        
        <h2>Our Top 5 Picks</h2>
        """
        
        # Add products
        for i in range(1, 6):
            title = data.get(f'ProductNo{i}Title')
            description = data.get(f'ProductNo{i}Description')
            affiliate_link = data.get(f'ProductNo{i}AffiliateLink')
            
            if title:
                content += f"""
                <div class="product-item" style="border: 2px solid #f0f0f0; padding: 25px; margin: 25px 0; border-radius: 8px; background: #fafafa;">
                    <h3 style="color: #ff6b00;">#{i}. {title}</h3>
                    <p>{description or 'Great product with excellent features.'}</p>
                    <a href="{affiliate_link}" 
                       class="amazon-button" 
                       style="display: inline-block; background: #FF9900; color: white; padding: 12px 30px; text-decoration: none; border-radius: 4px; font-weight: bold; margin-top: 15px;"
                       target="_blank" 
                       rel="nofollow noopener sponsored">
                       Check Price on Amazon
                    </a>
                </div>
                """
        
        # Add video section if available
        video_url = data.get('VideoURL') or data.get('GoogleDriveURL')
        if video_url:
            content += f"""
            <div class="video-section" style="margin: 40px 0;">
                <h2>Video Review</h2>
                <p>Watch our detailed video review:</p>
                <a href="{video_url}" target="_blank" class="video-link" style="color: #ff6b00;">Watch Video Review</a>
            </div>
            """
        
        # Add affiliate disclosure
        content += """
        <div class="affiliate-disclosure" style="background: #f0f0f0; padding: 20px; border-radius: 5px; margin-top: 40px;">
            <p><strong>Disclosure:</strong> As an Amazon Associate, we earn from qualifying purchases. 
            This doesn't affect the price you pay and helps us continue providing honest reviews.</p>
        </div>
        """
        
        return content
    
    async def _get_or_create_category(self, category_name: str) -> int:
        """Get category ID or create if doesn't exist"""
        
        # First, try to get existing category
        headers = {'Authorization': self.auth_header}
        response = requests.get(
            f"{self.categories_endpoint}?search={category_name}",
            headers=headers
        )
        
        if response.status_code == 200:
            categories = response.json()
            if categories:
                return categories[0]['id']
        
        # Create new category
        category_data = {
            'name': category_name,
            'slug': category_name.lower().replace(' ', '-')
        }
        
        response = requests.post(
            self.categories_endpoint,
            headers={
                'Authorization': self.auth_header,
                'Content-Type': 'application/json'
            },
            json=category_data
        )
        
        if response.status_code == 201:
            return response.json()['id']
        else:
            # Default to uncategorized
            return 1
    
    async def _enhance_post_visibility(self, post_id: int, airtable_data: Dict) -> None:
        """Enhance post visibility on homepage"""
        try:
            # Add tags for better categorization
            await self._add_post_tags(post_id, airtable_data)
            
            # Set featured image if video thumbnail available
            await self._set_featured_image(post_id, airtable_data)
            
            # Update post meta for SEO
            await self._update_post_meta(post_id, airtable_data)
            
        except Exception as e:
            logger.warning(f"Error enhancing post visibility: {e}")
    
    async def _add_post_tags(self, post_id: int, airtable_data: Dict) -> None:
        """Add relevant tags to improve categorization"""
        tags = []
        
        # Extract tags from video title
        title = airtable_data.get('VideoTitle', '')
        if 'top 5' in title.lower():
            tags.extend(['top 5', 'best products', 'reviews'])
        if 'gaming' in title.lower():
            tags.extend(['gaming', 'tech'])
        if 'laptop' in title.lower():
            tags.extend(['laptops', 'computers'])
        if '2024' in title:
            tags.append('2024')
        
        # Add category-specific tags
        tags.extend(['affiliate', 'amazon', 'product review'])
        
        if tags:
            # Create tags via API
            for tag_name in tags[:10]:  # Limit to 10 tags
                await self._create_or_get_tag(tag_name)
    
    async def _create_or_get_tag(self, tag_name: str) -> int:
        """Create or get existing tag"""
        try:
            tags_endpoint = f"{self.base_url}/wp-json/wp/v2/tags"
            headers = {'Authorization': self.auth_header}
            
            # Check if tag exists
            response = requests.get(
                f"{tags_endpoint}?search={tag_name}",
                headers=headers
            )
            
            if response.status_code == 200:
                tags = response.json()
                if tags:
                    return tags[0]['id']
            
            # Create new tag
            tag_data = {
                'name': tag_name,
                'slug': tag_name.lower().replace(' ', '-')
            }
            
            response = requests.post(
                tags_endpoint,
                headers={
                    'Authorization': self.auth_header,
                    'Content-Type': 'application/json'
                },
                json=tag_data
            )
            
            if response.status_code == 201:
                return response.json()['id']
                
        except Exception as e:
            logger.warning(f"Error creating tag {tag_name}: {e}")
        
        return 0
    
    async def _set_featured_image(self, post_id: int, airtable_data: Dict) -> None:
        """Set featured image from video thumbnail or default"""
        # This would require uploading an image to WordPress media library
        # For now, we'll skip this but leave the structure for future implementation
        pass
    
    async def _update_post_meta(self, post_id: int, airtable_data: Dict) -> None:
        """Update post metadata for better SEO and homepage visibility"""
        try:
            meta_endpoint = f"{self.base_url}/wp-json/wp/v2/posts/{post_id}"
            
            # Update with SEO-friendly meta
            meta_data = {
                'meta': {
                    '_yoast_wpseo_title': airtable_data.get('VideoTitle', ''),
                    '_yoast_wpseo_metadesc': airtable_data.get('VideoDescription', '')[:160],
                    '_yoast_wpseo_focuskw': 'product review',
                    'post_views_count': '0'
                }
            }
            
            response = requests.post(
                meta_endpoint,
                headers={
                    'Authorization': self.auth_header,
                    'Content-Type': 'application/json'
                },
                json=meta_data
            )
            
            if response.status_code == 200:
                logger.info(f"Updated post meta for post {post_id}")
            
        except Exception as e:
            logger.warning(f"Error updating post meta: {e}")

# Integration function for workflow_runner.py
async def publish_to_wordpress(config: Dict, airtable_record: Dict) -> Dict:
    """Publish Airtable record to WordPress"""
    
    wp_mcp = WordPressMCP(config)
    result = await wp_mcp.create_review_post(airtable_record)
    
    if result.get('success'):
        logger.info(f"Published to WordPress: {result['post_url']}")
    else:
        logger.error(f"WordPress publishing failed: {result.get('error')}")
    
    return result
