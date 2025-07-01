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
            
            # Create post data
            post_data = {
                'title': airtable_data.get('VideoTitle', 'Product Review'),
                'content': content,
                'status': 'publish',
                'categories': [category_id],
                'excerpt': airtable_data.get('VideoDescription', '')
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
                return {
                    'success': True,
                    'post_id': result['id'],
                    'post_url': result['link']
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
