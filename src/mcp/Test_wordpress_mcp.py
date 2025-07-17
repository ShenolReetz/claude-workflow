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
        """Generate formatted post content with product photos, countdown format, and pros/cons"""
        
        # Start with introduction
        intro_text = data.get('VideoDescription', 'Check out our top 5 picks for the best products!')
        content = f"""
        <div class="review-intro" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; text-align: center;">
            <h2 style="color: white; margin-bottom: 15px; font-size: 2.2em;">🔥 Our Top 5 Countdown 🔥</h2>
            <p style="font-size: 1.2em; margin: 0;">{intro_text}</p>
        </div>
        
        <div class="countdown-container">
        """
        
        # Generate products in countdown order (5 to 1)
        products_data = []
        for i in range(1, 6):
            title = data.get(f'ProductNo{i}Title')
            if title:
                products_data.append({
                    'rank': i,
                    'title': title,
                    'description': data.get(f'ProductNo{i}Description', ''),
                    'image_url': data.get(f'ProductNo{i}ImageURL', ''),
                    'affiliate_link': data.get(f'ProductNo{i}AffiliateLink', ''),
                    'review_count': data.get(f'ProductNo{i}ReviewCount', ''),
                    'rating': data.get(f'ProductNo{i}Rating', 4.0)
                })
        
        # Display in countdown order (5->1)
        for countdown_pos, product in enumerate(reversed(products_data), 1):
            countdown_number = 6 - countdown_pos  # 5, 4, 3, 2, 1
            is_winner = countdown_number == 1
            
            # Generate pros and cons from description
            pros, cons = self._extract_pros_cons(product['description'])
            
            # Special styling for winner
            border_color = "#FFD700" if is_winner else "#e0e0e0"
            bg_gradient = "linear-gradient(135deg, #FFD700, #FFA500)" if is_winner else "linear-gradient(135deg, #f8f9fa, #e9ecef)"
            winner_badge = "🏆 WINNER!" if is_winner else ""
            
            content += f"""
            <div class="product-countdown-item" style="border: 3px solid {border_color}; margin: 40px 0; border-radius: 15px; overflow: hidden; box-shadow: 0 8px 25px rgba(0,0,0,0.1); background: {bg_gradient};">
                
                <!-- Countdown Header -->
                <div class="countdown-header" style="background: {'#FFD700' if is_winner else '#667eea'}; color: {'#000' if is_winner else '#fff'}; padding: 20px; text-align: center; position: relative;">
                    <div style="font-size: 4em; font-weight: bold; line-height: 1;">#{countdown_number}</div>
                    {f'<div style="background: #FF4444; color: white; padding: 8px 20px; border-radius: 25px; display: inline-block; margin-top: 10px; font-weight: bold;">{winner_badge}</div>' if winner_badge else ''}
                </div>
                
                <!-- Product Content -->
                <div class="product-content" style="padding: 30px; background: white;">
                    
                    <!-- Product Image and Title Row -->
                    <div style="display: flex; gap: 30px; align-items: flex-start; margin-bottom: 25px; flex-wrap: wrap;">
                        
                        <!-- Product Image -->
                        <div class="product-image" style="flex: 0 0 300px; text-align: center;">
                            {f'<img src="{product["image_url"]}" alt="{product["title"]}" style="max-width: 100%; height: auto; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.2);" />' if product["image_url"] else '<div style="width: 300px; height: 200px; background: #f0f0f0; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: #666;">📷 Image Coming Soon</div>'}
                            
                            <!-- Rating and Reviews -->
                            <div style="margin-top: 15px; text-align: center;">
                                <div class="rating" style="color: #FFD700; font-size: 1.5em; margin-bottom: 5px;">
                                    {'⭐' * int(float(product.get('rating', 4.0)))}{'☆' * (5 - int(float(product.get('rating', 4.0))))}
                                    <span style="color: #333; font-size: 0.8em; margin-left: 10px;">{product.get('rating', 4.0)}/5</span>
                                </div>
                                {f'<div style="color: #666; font-size: 0.9em;">📝 {product["review_count"]} Reviews</div>' if product.get('review_count') else ''}
                            </div>
                        </div>
                        
                        <!-- Product Details -->
                        <div class="product-details" style="flex: 1; min-width: 300px;">
                            <h3 style="color: #333; font-size: 1.8em; margin-bottom: 15px; line-height: 1.2;">{product['title']}</h3>
                            <p style="color: #555; font-size: 1.1em; line-height: 1.6; margin-bottom: 20px;">{product['description']}</p>
                        </div>
                    </div>
                    
                    <!-- Pros and Cons Section -->
                    <div class="pros-cons" style="display: flex; gap: 20px; margin: 25px 0; flex-wrap: wrap;">
                        
                        <!-- Pros -->
                        <div class="pros" style="flex: 1; min-width: 250px; background: #e8f5e8; padding: 20px; border-radius: 10px; border-left: 5px solid #28a745;">
                            <h4 style="color: #28a745; margin-bottom: 15px; display: flex; align-items: center;">
                                <span style="margin-right: 10px;">✅</span> PROS
                            </h4>
                            <ul style="margin: 0; padding-left: 20px; color: #2d5a2d;">
                                {self._format_list_items(pros)}
                            </ul>
                        </div>
                        
                        <!-- Cons -->
                        <div class="cons" style="flex: 1; min-width: 250px; background: #fdeaea; padding: 20px; border-radius: 10px; border-left: 5px solid #dc3545;">
                            <h4 style="color: #dc3545; margin-bottom: 15px; display: flex; align-items: center;">
                                <span style="margin-right: 10px;">❌</span> CONS
                            </h4>
                            <ul style="margin: 0; padding-left: 20px; color: #5a2d2d;">
                                {self._format_list_items(cons)}
                            </ul>
                        </div>
                    </div>
                    
                    <!-- Call to Action -->
                    <div class="cta-section" style="text-align: center; margin-top: 30px;">
                        <a href="{product['affiliate_link']}" 
                           class="amazon-button" 
                           style="display: inline-block; background: {'#FF4444' if is_winner else '#FF9900'}; color: white; padding: 18px 40px; text-decoration: none; border-radius: 50px; font-weight: bold; font-size: 1.2em; box-shadow: 0 4px 15px rgba(0,0,0,0.2); transition: all 0.3s ease;"
                           target="_blank" 
                           rel="nofollow noopener sponsored">
                           {'🏆 GET THE WINNER ON AMAZON' if is_winner else '🛒 CHECK PRICE ON AMAZON'}
                        </a>
                        <div style="margin-top: 10px; font-size: 0.9em; color: #666;">
                            💰 Best Price Guaranteed | ⚡ Fast Prime Shipping
                        </div>
                    </div>
                </div>
            </div>
            """
        
        # Close countdown container
        content += """
        </div>
        """
        
        # Add video section if available
        video_url = data.get('VideoURL') or data.get('GoogleDriveURL')
        if video_url:
            content += f"""
            <div class="video-section" style="margin: 50px 0; text-align: center; background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); padding: 40px; border-radius: 15px;">
                <h2 style="color: #333; margin-bottom: 20px;">🎬 Watch Our Video Review</h2>
                <p style="font-size: 1.2em; margin-bottom: 25px; color: #555;">See all these products in action and get our detailed analysis!</p>
                <a href="{video_url}" target="_blank" 
                   style="display: inline-block; background: #FF4444; color: white; padding: 18px 40px; text-decoration: none; border-radius: 50px; font-weight: bold; font-size: 1.2em; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
                   🎥 WATCH FULL REVIEW
                </a>
            </div>
            """
        
        # Add affiliate disclosure
        content += """
        <div class="affiliate-disclosure" style="background: linear-gradient(135deg, #f0f2f5, #e6e9ed); padding: 30px; border-radius: 15px; margin-top: 50px; border-left: 5px solid #667eea;">
            <h3 style="color: #333; margin-bottom: 15px; display: flex; align-items: center;">
                <span style="margin-right: 10px;">💡</span> Important Disclosure
            </h3>
            <p style="color: #555; line-height: 1.6; margin: 0;">
                <strong>Amazon Associate Disclosure:</strong> We earn from qualifying purchases made through our affiliate links. 
                This doesn't affect the price you pay and helps us continue providing honest, unbiased reviews. 
                All opinions are our own based on thorough testing and research.
            </p>
        </div>
        """
        
        return content
    
    def _extract_pros_cons(self, description: str) -> tuple:
        """Extract pros and cons from product description"""
        # Simple extraction based on common patterns
        pros = []
        cons = []
        
        if not description:
            # Default pros/cons if no description
            pros = ["High quality build", "Great performance", "Good value for money"]
            cons = ["Price point may be high", "Limited color options"]
            return pros, cons
        
        # Look for positive keywords
        positive_keywords = [
            'excellent', 'great', 'outstanding', 'powerful', 'fast', 'reliable', 
            'durable', 'efficient', 'premium', 'high-quality', 'versatile',
            'lightweight', 'compact', 'wireless', 'advanced', 'innovative'
        ]
        
        # Look for potential negative aspects
        negative_keywords = [
            'expensive', 'heavy', 'bulky', 'limited', 'short battery',
            'noisy', 'complex', 'fragile', 'slow', 'compatibility issues'
        ]
        
        # Extract sentences and categorize
        sentences = description.split('. ')
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            # Check for positive aspects
            for keyword in positive_keywords:
                if keyword in sentence_lower:
                    feature = sentence.strip()
                    if feature and feature not in pros and len(pros) < 4:
                        pros.append(feature)
                    break
        
        # Add generic pros if none found
        if not pros:
            if 'wireless' in description.lower():
                pros.append("Wireless connectivity")
            if 'battery' in description.lower():
                pros.append("Long battery life")
            if 'performance' in description.lower():
                pros.append("Excellent performance")
            if not pros:
                pros = ["High quality construction", "Reliable performance", "Great value"]
        
        # Generate appropriate cons based on product type
        description_lower = description.lower()
        if 'premium' in description_lower or 'high-end' in description_lower:
            cons.append("Higher price point")
        if 'wireless' in description_lower:
            cons.append("Requires charging")
        if 'gaming' in description_lower:
            cons.append("May be overkill for casual use")
        
        # Default cons if none generated
        if not cons:
            cons = ["Price may be steep for some", "Limited color options"]
        
        return pros[:3], cons[:2]  # Limit to 3 pros, 2 cons
    
    def _format_list_items(self, items: list) -> str:
        """Format list items as HTML"""
        if not items:
            return "<li>None specified</li>"
        
        return "".join([f"<li>{item}</li>" for item in items])
    
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
