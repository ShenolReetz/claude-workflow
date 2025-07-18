#!/usr/bin/env python3
"""
Platform-Specific Content Generator
Generates optimized titles and descriptions for different platforms using existing keywords
"""

import asyncio
import json
import logging
import random
from typing import Dict, List, Optional
import re
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from mcp_servers.Test_airtable_server import AirtableMCPServer
from mcp_servers.Test_content_generation_server import ContentGenerationMCPServer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PlatformContentGenerator:
    """TEST MODE: Generate hardcoded platform-specific content"""
    
    def __init__(self, config: Dict):
        self.config = config
        
        # Initialize the hardcoded content generation server
        self.content_server = ContentGenerationMCPServer(config.get('anthropic_api_key', ''))
        
        logger.info("✅ TEST MODE: Platform Content Generator initialized with hardcoded data")
        
        # Platform-specific constraints
        self.platform_specs = {
            "youtube": {
                "title_max_chars": 100,
                "description_max_chars": 5000,
                "optimal_title_length": 70,
                "keyword_density_target": 0.02
            },
            "tiktok": {
                "title_max_chars": 100,
                "description_max_chars": 300,
                "optimal_title_length": 60,
                "keyword_density_target": 0.025
            },
            "instagram": {
                "title_max_chars": 125,
                "description_max_chars": 2200,
                "optimal_title_length": 80,
                "keyword_density_target": 0.03
            },
            "wordpress": {
                "title_max_chars": 150,
                "description_max_chars": 50000,
                "optimal_title_length": 90,
                "keyword_density_target": 0.015
            }
        }
    
    async def generate_platform_content(self, record_id: str, base_title: str, 
                                      products: List[Dict], category: str) -> Dict:
        """Generate content for all platforms"""
        
        logger.info(f"🎯 Generating platform-specific content for: {base_title}")
        
        # Store base_title for later use in _save_to_airtable
        self.base_title = base_title
        
        # Get existing keywords from Airtable
        airtable_server = AirtableMCPServer(
            api_key=self.config['airtable_api_key'],
            base_id=self.config['airtable_base_id'],
            table_name=self.config['airtable_table_name']
        )
        
        record = await airtable_server.get_record_by_id(record_id)
        if not record:
            return {'success': False, 'error': 'Record not found'}
        
        # Extract existing keywords
        youtube_keywords = record['fields'].get('YouTubeKeywords', '').split(',')
        tiktok_keywords = record['fields'].get('TikTokKeywords', '').split(',')
        instagram_hashtags = record['fields'].get('InstagramHashtags', '').split(',')
        wordpress_seo = record['fields'].get('WordPressSEO', '').split(',')
        
        # Clean keywords
        youtube_keywords = [k.strip() for k in youtube_keywords if k.strip()]
        tiktok_keywords = [k.strip() for k in tiktok_keywords if k.strip()]
        instagram_hashtags = [k.strip() for k in instagram_hashtags if k.strip()]
        wordpress_seo = [k.strip() for k in wordpress_seo if k.strip()]
        
        results = {}
        
        # Generate platform keywords
        platform_keywords = await self.content_server.generate_multi_platform_keywords(base_title, products)
        
        # Generate platform metadata using hardcoded content server
        logger.info("📹 TEST MODE: Generating platform content...")
        platform_metadata = await self.content_server.generate_platform_upload_metadata(
            base_title, products, platform_keywords, products
        )
        
        # YouTube
        youtube_data = platform_metadata.get('youtube', {})
        youtube_result = {
            'title': youtube_data.get('title', f'🔥 Top 5 {category} of 2025 - Best Reviews'),
            'description': youtube_data.get('description', 'Check out our top 5 picks!'),
            'title_length': len(youtube_data.get('title', '')),
            'description_length': len(youtube_data.get('description', '')),
            'keywords_used': len(youtube_data.get('tags', []))
        }
        results['youtube'] = youtube_result
        logger.info("✅ TEST MODE: YouTube content ready (no tokens used)")
        
        # TikTok
        tiktok_data = platform_metadata.get('tiktok', {})
        tiktok_result = {
            'title': tiktok_data.get('title', f'🔥 5 INSANE {category} #MustHave'),
            'description': tiktok_data.get('caption', 'Check these out! #Trending'),
            'title_length': len(tiktok_data.get('title', '')),
            'description_length': len(tiktok_data.get('caption', '')),
            'keywords_used': len(tiktok_data.get('hashtags', []))
        }
        results['tiktok'] = tiktok_result
        logger.info("✅ TEST MODE: TikTok content ready (no tokens used)")
        
        # Instagram
        instagram_data = platform_metadata.get('instagram', {})
        instagram_result = {
            'title': instagram_data.get('title', f'✨ Must-Have {category} 2025'),
            'caption': instagram_data.get('caption', 'Amazing finds! Link in bio!'),
            'title_length': len(instagram_data.get('title', '')),
            'caption_length': len(instagram_data.get('caption', '')),
            'hashtags_used': len(instagram_data.get('hashtags', []))
        }
        results['instagram'] = instagram_result
        logger.info("✅ TEST MODE: Instagram content ready (no tokens used)")
        
        # WordPress
        wordpress_data = platform_metadata.get('wordpress', {})
        wordpress_result = {
            'title': wordpress_data.get('title', f'Best {category} 2025: Complete Guide'),
            'content': wordpress_data.get('content', 'Comprehensive review and buying guide.'),
            'title_length': len(wordpress_data.get('title', '')),
            'content_length': len(wordpress_data.get('content', '')),
            'keywords_used': wordpress_data.get('focus_keywords', [])[:5],
            'template_used': 'hardcoded',
            'word_count': len(wordpress_data.get('content', '').split())
        }
        results['wordpress'] = wordpress_result
        logger.info(f"✅ TEST MODE: WordPress content ready ({results['wordpress']['word_count']} words, no tokens used)")
        
        # Calculate analytics
        logger.info("📊 Calculating SEO and engagement metrics...")
        analytics = await self._calculate_analytics(results, youtube_keywords + tiktok_keywords)
        results['analytics'] = analytics
        
        # Save to Airtable
        await self._save_to_airtable(record_id, results)
        
        return {
            'success': True,
            'platforms_generated': len(results) - 1,  # Subtract analytics
            'results': results
        }
    
    async def _generate_youtube_content(self, base_title: str, keywords: List[str], 
                                      products: List[Dict], category: str) -> Dict:
        """Generate YouTube-optimized title and description"""
        
        prompt = f"""Generate YouTube-optimized content for: "{base_title}"

Keywords to include: {', '.join(keywords[:8])}
Category: {category}
Products: {', '.join([p.get('title', '') for p in products[:5]])}

Generate:
1. YouTube Title (60-70 characters, engaging, includes primary keywords)
2. YouTube Description (detailed, SEO-optimized, includes all keywords naturally)

YouTube Title Requirements:
- 60-70 characters optimal
- Include primary keywords naturally
- Engaging and clickable
- Include power words like "Top", "Best", "Review"
- Numbers and emojis for engagement

YouTube Description Requirements:
- Detailed product breakdown
- Include all keywords naturally
- Call-to-action for likes/subscriptions
- Timestamps for products
- Affiliate disclosure
- 300-500 words

Format your response as:
TITLE: [YouTube title here]
DESCRIPTION: [YouTube description here]"""

        # TEST MODE: Return hardcoded YouTube content
        try:
            title = f"🎯 {base_title} - Complete Review & Buying Guide!"
            description = f"""🔥 Complete {category} buying guide! We've tested and reviewed the TOP 5 {category} so you don't have to!

⭐ What's covered in this video:
• Detailed product comparisons
• Price analysis and best deals
• Real user reviews and ratings
• Pros and cons of each product
• Our expert recommendations

🎯 Keywords: {', '.join(keywords[:10])}

🛒 Products featured:
{chr(10).join([f'• {p.get("title", "Product")} - ${p.get("price", "0")}' for p in products[:5]])}

📊 Don't forget to LIKE, SUBSCRIBE, and hit the BELL for more honest reviews!

#ProductReview #{category.replace(' ', '')} #BuyingGuide #TechReview #BestProducts2025

⚠️ Affiliate Disclaimer: This video contains affiliate links. We may earn a small commission at no extra cost to you."""
            
            return {
                'title': title,
                'description': description,
                'title_length': len(title),
                'description_length': len(description),
                'keywords_used': len([k for k in keywords if k.lower() in description.lower()])
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating YouTube content: {e}")
            return {'error': str(e)}
    
    async def _generate_tiktok_content(self, base_title: str, keywords: List[str], 
                                     products: List[Dict], category: str) -> Dict:
        """Generate TikTok-optimized title and description"""
        
        prompt = f"""Generate TikTok-optimized content for: "{base_title}"

Keywords to include: {', '.join(keywords[:6])}
Category: {category}
Products: {', '.join([p.get('title', '') for p in products[:5]])}

Generate:
1. TikTok Title (50-60 characters, engaging, trend-aware)
2. TikTok Description (short, punchy, includes hashtags)

TikTok Title Requirements:
- 50-60 characters optimal
- Trend-aware language
- Engaging and shareable
- Include relevant keywords
- Use TikTok slang/style

TikTok Description Requirements:
- Short and punchy (100-150 words)
- Include trending hashtags
- Call-to-action for engagement
- Product highlights
- Gen Z friendly language

Format your response as:
TITLE: [TikTok title here]
DESCRIPTION: [TikTok description here]"""

        # TEST MODE: Return hardcoded TikTok content
        try:
            title = f"🔥 {base_title.replace('Top 5', 'TOP 5')} YOU NEED!"
            description = f"""OMG these {category} are INSANE! 🤯 

Which one would you pick? Drop a comment! 👇

#{category.replace(' ', '')} #TechTok #ProductReview #MustHave #Viral #FYP #BestProducts #TechReview #Shopping #BuyingGuide #TechFinds

🛒 Links in bio for best deals! 💰"""
            
            return {
                'title': title,
                'description': description,
                'title_length': len(title),
                'description_length': len(description),
                'keywords_used': len([k for k in keywords if k.lower() in description.lower()])
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating TikTok content: {e}")
            return {'error': str(e)}
    
    async def _generate_instagram_content(self, base_title: str, hashtags: List[str], 
                                        products: List[Dict], category: str) -> Dict:
        """Generate Instagram-optimized title and caption"""
        
        prompt = f"""Generate Instagram-optimized content for: "{base_title}"

Hashtags to include: {', '.join(hashtags[:15])}
Category: {category}
Products: {', '.join([p.get('title', '') for p in products[:5]])}

Generate:
1. Instagram Title (70-80 characters, engaging, aesthetic)
2. Instagram Caption (engaging story, includes hashtags)

Instagram Title Requirements:
- 70-80 characters optimal
- Aesthetic and engaging
- Include relevant keywords
- Instagram-friendly language
- Visual appeal focus

Instagram Caption Requirements:
- Engaging story format
- Include product highlights
- Mix of popular and niche hashtags
- Call-to-action for engagement
- 150-300 words + hashtags

Format your response as:
TITLE: [Instagram title here]
CAPTION: [Instagram caption here]"""

        # TEST MODE: Return hardcoded Instagram content
        try:
            title = f"✨ {base_title.replace('Top 5', 'TOP 5')} Review ✨"
            
            # Create hashtags from keywords
            hashtag_list = [f"#{kw.replace(' ', '').lower()}" for kw in keywords[:10]]
            hashtag_list.extend(["#ProductReview", "#TechFinds", "#ShoppingGuide", "#TechReview"])
            hashtag_str = " ".join(hashtag_list[:15])
            
            caption = f"""🔥 Just finished testing these amazing {category}! Here's what I found:

📦 Swipe to see all 5 products in detail
⭐ Each one has been thoroughly tested
💯 Honest reviews - no bias here!
🔥 Which one caught your eye? Drop a comment!

👆 Links in bio for best deals!

{hashtag_str}

---
💬 Comment your thoughts!
❤️ Save this post for later!
📤 Share with friends who need this!"""
            
            return {
                'title': title,
                'caption': caption,
                'title_length': len(title),
                'caption_length': len(caption),
                'hashtags_used': len(hashtag_list)
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating Instagram content: {e}")
            return {'error': str(e)}
    
    async def _generate_wordpress_content(self, base_title: str, seo_keywords: List[str], 
                                        products: List[Dict], category: str, record_data: Dict = None) -> Dict:
        """Generate comprehensive WordPress blog post with all product data"""
        
        # Build comprehensive product data for the prompt
        product_details = []
        for i, product in enumerate(products[:5], 1):
            rank = 6 - i  # Countdown from 5 to 1
            
            # Get product data from various sources
            product_info = {
                'rank': rank,
                'title': product.get('title', f'Product {rank}'),
                'description': product.get('description', ''),
                'price': record_data.get(f'ProductNo{rank}Price', 'N/A') if record_data else 'N/A',
                'rating': record_data.get(f'ProductNo{rank}Rating', '4.0') if record_data else '4.0',
                'reviews': record_data.get(f'ProductNo{rank}Reviews', '0') if record_data else '0',
                'affiliate_link': record_data.get(f'ProductNo{rank}AffiliateLink', '') if record_data else '',
                'photo_url': record_data.get(f'ProductNo{rank}Photo', '') if record_data else ''
            }
            product_details.append(product_info)
        
        # Get social media links if available
        social_links = {
            'youtube_video': record_data.get('YouTubeVideoURL', '') if record_data else '',
            'tiktok_video': record_data.get('TikTokVideoURL', '') if record_data else '',
            'instagram_video': record_data.get('InstagramVideoURL', '') if record_data else ''
        }
        
        # Create comprehensive WordPress content
        prompt = f"""Generate a comprehensive WordPress blog post for: "{base_title}"

SEO Keywords (use naturally throughout): {', '.join(seo_keywords[:10])}
Category: {category}

Product Details:
{chr(10).join([f"#{p['rank']}. {p['title']} - ${p['price']} - {p['rating']}⭐ ({p['reviews']} reviews)" for p in product_details])}

Generate:
1. WordPress Title (SEO-optimized, 60-90 characters)
2. WordPress Content (comprehensive blog post with countdown format)

WordPress Title Requirements:
- 60-90 characters optimal
- Include primary SEO keywords
- SEO-friendly structure
- Include "Top 5" or countdown reference
- Engaging and click-worthy

WordPress Content Requirements:
- 1500-2000 words comprehensive blog post
- Countdown format: Start with #5 and end with #1
- For each product include:
  * Product image: [INSERT_PRODUCT_{rank}_IMAGE]
  * Product title with price in heading (e.g., "Product Name - $99.99")
  * Star rating and review count (do NOT repeat the price here)
  * Detailed description (150-200 words)
  * Pros and Cons (3-4 each)
  * Affiliate link: [INSERT_AFFILIATE_LINK_{rank}]
  * "Check Latest Price" button
- SEO optimization:
  * Use all SEO keywords naturally
  * Include H2 headers for each product
  * Meta description friendly intro
  * Include FAQ section
  * Add conclusion with social media links
- Structure:
  * Introduction (200 words)
  * Product countdown (#5 to #1)
  * Comparison table
  * FAQ section
  * Conclusion with social media links
- Include affiliate disclosure
- Professional, engaging tone
- High keyword density but natural

Social Media Integration:
- YouTube: [INSERT_YOUTUBE_VIDEO]
- TikTok: [INSERT_TIKTOK_VIDEO]  
- Instagram: [INSERT_INSTAGRAM_VIDEO]

Format your response as:
TITLE: [WordPress title here]
CONTENT: [WordPress content here with all placeholders and structure]"""

        # TEST MODE: Return hardcoded WordPress content
        try:
            title = f"{base_title} - Complete Buying Guide & Reviews [2025]"
            
            # Create basic blog content
            blog_content = f"""
<h1>{title}</h1>

<p>Looking for the best {category}? After extensive research and testing, we've compiled this comprehensive guide to help you make an informed decision. Our team has analyzed hundreds of products to bring you the top 5 {category} currently available.</p>

<h2>Quick Summary - Top 5 {category}:</h2>
<ol>
{chr(10).join([f'<li><strong>{p["title"]}</strong> - ${p["price"]} - {p["rating"]}⭐ ({p["reviews"]} reviews)</li>' for p in product_details])}
</ol>

<h2>Detailed Product Reviews:</h2>
{chr(10).join([f'''<h3>#{p["rank"]}. {p["title"]} - ${p["price"]}</h3>
<p><strong>Rating:</strong> {p["rating"]}⭐ ({p["reviews"]} reviews)</p>
<p>{p["description"]}</p>
<p><strong>Pros:</strong> Great value, excellent features, highly rated</p>
<p><strong>Cons:</strong> Limited availability, premium price point</p>
<p><a href="{p["affiliate_link"]}" class="btn btn-primary">Check Latest Price</a></p>
''' for p in product_details])}

<h2>Frequently Asked Questions</h2>
<p><strong>Q: Which {category} offers the best value?</strong><br>
A: Based on our analysis, the #{product_details[0]['rank']} product offers excellent value for money.</p>

<p><strong>Q: Are these products currently available?</strong><br>
A: Yes, all products are currently in stock and available for purchase.</p>

<h2>Conclusion</h2>
<p>After thorough testing, we recommend the #{product_details[0]['rank']} product as our top choice. Each product on this list offers unique advantages, so choose based on your specific needs and budget.</p>

<p><strong>Affiliate Disclosure:</strong> This post contains affiliate links. We may earn a small commission at no extra cost to you when you purchase through our links.</p>
"""
            
            return {
                'title': title,
                'content': blog_content,
                'title_length': len(title),
                'content_length': len(blog_content),
                'keywords_used': len([k for k in seo_keywords if k.lower() in blog_content.lower()])
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating WordPress content: {e}")
            return {'error': str(e)}
    
    async def _process_wordpress_placeholders(self, content: str, product_details: List[Dict], 
                                            social_links: Dict) -> str:
        """Replace placeholders in WordPress content with actual data"""
        
        # Replace product images
        for product in product_details:
            rank = product['rank']
            photo_url = product['photo_url']
            
            # Create HTML image tag
            if photo_url:
                image_html = f'<img src="{photo_url}" alt="{product["title"]}" style="width: 100%; max-width: 400px; height: auto; margin: 10px 0;" />'
            else:
                image_html = f'<div style="width: 100%; max-width: 400px; height: 200px; background: #f0f0f0; display: flex; align-items: center; justify-content: center; margin: 10px 0;"><p>Product Image</p></div>'
            
            content = content.replace(f'[INSERT_PRODUCT_{rank}_IMAGE]', image_html)
        
        # Replace affiliate links
        for product in product_details:
            rank = product['rank']
            affiliate_link = product['affiliate_link']
            
            # Create affiliate link HTML
            if affiliate_link:
                link_html = f'''<div style="margin: 15px 0; text-align: center;">
                    <a href="{affiliate_link}" target="_blank" rel="nofollow sponsored" style="background: #ff9900; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                        🛒 Check Latest Price on Amazon
                    </a>
                </div>'''
            else:
                link_html = '<div style="margin: 15px 0; text-align: center;"><p><em>Affiliate link not available</em></p></div>'
            
            content = content.replace(f'[INSERT_AFFILIATE_LINK_{rank}]', link_html)
        
        # Replace social media video links
        social_media_html = '<div style="margin: 30px 0; padding: 20px; background: #f8f9fa; border-radius: 8px;"><h3>🎥 Watch Our Video Reviews</h3><div style="display: flex; gap: 15px; flex-wrap: wrap; justify-content: center;">'
        
        if social_links['youtube_video']:
            social_media_html += f'<a href="{social_links["youtube_video"]}" target="_blank" style="background: #ff0000; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">📺 YouTube</a>'
        
        if social_links['tiktok_video']:
            social_media_html += f'<a href="{social_links["tiktok_video"]}" target="_blank" style="background: #000000; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">🎵 TikTok</a>'
        
        if social_links['instagram_video']:
            social_media_html += f'<a href="{social_links["instagram_video"]}" target="_blank" style="background: #e4405f; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">📸 Instagram</a>'
        
        social_media_html += '</div></div>'
        
        # Replace social media placeholders
        content = content.replace('[INSERT_YOUTUBE_VIDEO]', social_links.get('youtube_video', ''))
        content = content.replace('[INSERT_TIKTOK_VIDEO]', social_links.get('tiktok_video', ''))
        content = content.replace('[INSERT_INSTAGRAM_VIDEO]', social_links.get('instagram_video', ''))
        
        # Add social media section at the end if not already present
        if '[INSERT_SOCIAL_MEDIA_SECTION]' in content:
            content = content.replace('[INSERT_SOCIAL_MEDIA_SECTION]', social_media_html)
        elif not any(link in content for link in social_links.values() if link):
            content += f'\n\n{social_media_html}'
        
        # Add affiliate disclosure if not present
        if 'affiliate' not in content.lower():
            affiliate_disclosure = '''
            <div style="margin: 30px 0; padding: 15px; background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px;">
                <p><strong>📢 Affiliate Disclosure:</strong> This post contains affiliate links. When you click on these links and make a purchase, we may earn a small commission at no extra cost to you. This helps support our channel and allows us to continue creating helpful content. Thank you for your support!</p>
            </div>
            '''
            content += affiliate_disclosure
        
        return content
    
    async def _calculate_analytics(self, results: Dict, all_keywords: List[str]) -> Dict:
        """Calculate SEO and engagement analytics"""
        
        analytics = {}
        
        # Calculate SEO Score (0-100)
        seo_factors = []
        
        # Title optimization scores
        for platform in ['youtube', 'tiktok', 'instagram', 'wordpress']:
            if platform in results and 'title' in results[platform]:
                title = results[platform]['title']
                title_length = len(title)
                optimal_length = self.platform_specs[platform]['optimal_title_length']
                
                # Length score (closer to optimal = higher score)
                length_score = max(0, 100 - abs(title_length - optimal_length) * 2)
                
                # Keyword inclusion score
                keywords_in_title = sum(1 for k in all_keywords if k.lower() in title.lower())
                keyword_score = min(100, keywords_in_title * 25)
                
                platform_score = (length_score + keyword_score) / 2
                seo_factors.append(platform_score)
        
        analytics['SEOScore'] = round(sum(seo_factors) / len(seo_factors) if seo_factors else 0)
        
        # Title Optimization Score
        title_scores = []
        for platform in ['youtube', 'tiktok', 'instagram', 'wordpress']:
            if platform in results and 'title' in results[platform]:
                title = results[platform]['title']
                
                # Check for power words
                power_words = ['top', 'best', 'review', 'amazing', 'ultimate', 'perfect']
                power_word_score = sum(10 for word in power_words if word in title.lower())
                
                # Check for numbers
                number_score = 20 if re.search(r'\d+', title) else 0
                
                # Check for engagement words
                engagement_words = ['you', 'your', 'must', 'need', 'should', 'will']
                engagement_score = sum(5 for word in engagement_words if word in title.lower())
                
                title_score = min(100, power_word_score + number_score + engagement_score)
                title_scores.append(title_score)
        
        analytics['TitleOptimisationScore'] = round(sum(title_scores) / len(title_scores) if title_scores else 0)
        
        # Keyword Density
        total_content = ""
        for platform in results:
            if platform != 'analytics' and isinstance(results[platform], dict):
                if 'description' in results[platform]:
                    total_content += " " + results[platform]['description']
                if 'content' in results[platform]:
                    total_content += " " + results[platform]['content']
                if 'caption' in results[platform]:
                    total_content += " " + results[platform]['caption']
        
        if total_content:
            word_count = len(total_content.split())
            keyword_occurrences = sum(total_content.lower().count(k.lower()) for k in all_keywords)
            keyword_density = (keyword_occurrences / word_count) * 100 if word_count > 0 else 0
            analytics['KewordDensity'] = round(keyword_density, 2)
        else:
            analytics['KewordDensity'] = 0.0
        
        # Engagement Prediction (0-100)
        engagement_factors = []
        
        # Check for engagement elements across platforms
        for platform in results:
            if platform != 'analytics' and isinstance(results[platform], dict):
                content_to_check = ""
                if 'description' in results[platform]:
                    content_to_check += results[platform]['description']
                if 'content' in results[platform]:
                    content_to_check += results[platform]['content']
                if 'caption' in results[platform]:
                    content_to_check += results[platform]['caption']
                
                # Check for engagement elements
                engagement_elements = {
                    'questions': len(re.findall(r'\?', content_to_check)),
                    'call_to_action': len(re.findall(r'(subscribe|like|comment|share|follow)', content_to_check, re.IGNORECASE)),
                    'emotional_words': len(re.findall(r'(amazing|awesome|incredible|fantastic|perfect|love|hate|wow)', content_to_check, re.IGNORECASE)),
                    'urgency_words': len(re.findall(r'(now|today|limited|exclusive|must|need)', content_to_check, re.IGNORECASE))
                }
                
                platform_engagement = sum(min(score * 10, 25) for score in engagement_elements.values())
                engagement_factors.append(platform_engagement)
        
        analytics['EngagementPrediction'] = round(sum(engagement_factors) / len(engagement_factors) if engagement_factors else 0)
        
        return analytics
    
    async def _save_to_airtable(self, record_id: str, results: Dict) -> None:
        """Save all generated content to Airtable"""
        
        update_fields = {}
        
        # Note: NOT updating the general Title field - it should remain as the original title
        
        # Platform-specific content using exact Airtable column names
        platform_field_mapping = {
            'youtube': {'title': 'YouTubeTitle', 'description': 'YouTubeDescription'},
            'tiktok': {'title': 'TikTokTitle', 'description': 'TikTokDescription'},
            'instagram': {'title': 'InstagramTitle', 'description': 'InstagramCaption'},
            'wordpress': {'title': 'WordPressTitle', 'description': 'WordPressContent'}
        }
        
        # Add platform content using exact field names
        logger.info(f"🔍 DEBUG: Processing platforms: {list(results.keys())}")
        
        for platform, content in results.items():
            if platform == 'analytics':
                continue  # Handle analytics separately
                
            logger.info(f"🔍 DEBUG: Platform '{platform}' content keys: {list(content.keys()) if isinstance(content, dict) else 'Not a dict'}")
            
            if platform in platform_field_mapping and isinstance(content, dict):
                mapping = platform_field_mapping[platform]
                
                if 'title' in content:
                    update_fields[mapping['title']] = content['title']
                    logger.info(f"✅ Added {mapping['title']}: {content['title'][:50]}...")
                
                # Handle different content types (description, caption, content)
                description_content = content.get('description') or content.get('caption') or content.get('content')
                if description_content:
                    update_fields[mapping['description']] = description_content
                    logger.info(f"✅ Added {mapping['description']}: {description_content[:50]}...")
                else:
                    logger.warning(f"⚠️ No description content found for {platform}")
        
        # Also save YouTube title as VideoTitle for backwards compatibility
        if 'youtube' in results and isinstance(results['youtube'], dict):
            if 'title' in results['youtube']:
                update_fields['VideoTitle'] = results['youtube']['title']
                logger.info(f"✅ Updated VideoTitle: {results['youtube']['title'][:50]}...")
            if 'description' in results['youtube']:
                update_fields['VideoDescription'] = results['youtube']['description']
                logger.info(f"✅ Updated VideoDescription: {results['youtube']['description'][:50]}...")
        
        # Analytics - commented out as these fields don't exist in Airtable yet
        # if 'analytics' in results:
        #     analytics = results['analytics']
        #     update_fields['SEOScore'] = analytics['SEOScore']
        #     update_fields['TitleOptimisationScore'] = analytics['TitleOptimisationScore']
        #     update_fields['KewordDensity'] = analytics['KewordDensity']
        #     update_fields['EngagementPrediction'] = analytics['EngagementPrediction']
        
        if update_fields:
            airtable_server = AirtableMCPServer(
                api_key=self.config['airtable_api_key'],
                base_id=self.config['airtable_base_id'],
                table_name=self.config['airtable_table_name']
            )
            
            try:
                # Save all platform content at once using exact field names
                await airtable_server.update_record(record_id, update_fields)
                logger.info(f"✅ Saved {len(update_fields)} platform-specific fields to Airtable")
                
                # Check if required platform fields are populated
                required_platform_fields = [
                    'YouTubeTitle', 'TikTokTitle', 'InstagramTitle', 'WordPressTitle',
                    'YouTubeDescription', 'TikTokDescription', 'InstagramCaption', 'WordPressContent'
                ]
                
                populated_fields = [field for field in required_platform_fields if field in update_fields]
                
                # If we have at least 6 platform fields (3 platforms with titles and descriptions), set VideoProductionRDY to "Ready"
                if len(populated_fields) >= 6:
                    try:
                        await airtable_server.update_record(record_id, {'VideoProductionRDY': 'Ready'})
                        logger.info("🎬 ✅ VideoProductionRDY set to 'Ready' - platform content complete!")
                    except Exception as e:
                        logger.warning(f"⚠️ Could not update VideoProductionRDY: {e}")
                
                logger.info(f"📊 Platform fields updated: {list(update_fields.keys())}")
                
            except Exception as e:
                logger.error(f"❌ Failed to save platform content: {e}")
                # Don't fail completely, just log the error
    
    async def close(self):
        """Close the HTTP client - TEST MODE: No client to close"""
        pass


# Integration function for workflow
async def generate_platform_content_for_workflow(config: Dict, record_id: str, 
                                               base_title: str, products: List[Dict],
                                               category: str) -> Dict:
    """Generate platform-specific content and integrate into workflow"""
    
    generator = PlatformContentGenerator(config)
    
    try:
        result = await generator.generate_platform_content(
            record_id, base_title, products, category
        )
        return result
        
    finally:
        await generator.close()


# Test function
if __name__ == "__main__":
    async def test_platform_content():
        # Load config
        with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
            config = json.load(f)
        
        # Test data
        test_products = [
            {"title": "SteelSeries Arctis Nova Pro Gaming Headset"},
            {"title": "Razer BlackShark V2 Pro Wireless Headset"},
            {"title": "HyperX Cloud Alpha Gaming Headset"},
            {"title": "Logitech G Pro X Gaming Headset"},
            {"title": "Corsair Virtuoso RGB Wireless Gaming Headset"}
        ]
        
        generator = PlatformContentGenerator(config)
        
        print("🧪 Testing platform-specific content generation...")
        print("Note: This test requires existing keywords in Airtable")
        
        # This would need a real record ID with existing keywords
        # result = await generator.generate_platform_content(
        #     "test_record_id",
        #     "Top 5 Gaming Headsets That'll Transform Your Gaming Experience",
        #     test_products,
        #     "Gaming"
        # )
        
        print("✅ Platform content generator created successfully")
        print("Ready to integrate into workflow with real Airtable data")
        
        await generator.close()
    
    asyncio.run(test_platform_content())