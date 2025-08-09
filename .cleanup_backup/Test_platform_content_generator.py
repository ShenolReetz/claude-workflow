#!/usr/bin/env python3
"""
Test Platform-Specific Content Generator
Hardcoded responses for testing - no API usage
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional
import re
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

# from mcp_servers.Test_airtable_server_v2 import TestAirtableMCPServerV2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestPlatformContentGenerator:
    """Test version with hardcoded platform-specific content generation"""
    
    def __init__(self, config: Dict):
        self.config = config
        # No actual HTTP client needed for test mode
        
        print("🧪 TEST MODE: Platform Content Generator using hardcoded responses")
        logger.info("🧪 Test Platform Content Generator initialized")
        
        # Platform-specific constraints (same as production)
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
                "optimal_title_length": 100,
                "keyword_density_target": 0.03
            },
            "wordpress": {
                "title_max_chars": 150,
                "description_max_chars": 160,
                "optimal_title_length": 120,
                "keyword_density_target": 0.015
            }
        }
    
    async def generate_platform_content(self, 
                                      platform: str, 
                                      base_title: str, 
                                      keywords: List[str], 
                                      products: List[Dict]) -> Dict:
        """Generate hardcoded platform-specific content"""
        
        logger.info(f"📱 Test: Generating {platform} content for: {base_title[:50]}...")
        print(f"🧪 TEST: Generating {platform.upper()} content")
        
        try:
            # Simulate processing delay
            await asyncio.sleep(0.2)
            
            # Generate hardcoded platform-specific content
            if platform == "youtube":
                content = await self._generate_youtube_content(base_title, keywords, products)
            elif platform == "tiktok":
                content = await self._generate_tiktok_content(base_title, keywords, products)
            elif platform == "instagram":
                content = await self._generate_instagram_content(base_title, keywords, products)
            elif platform == "wordpress":
                content = await self._generate_wordpress_content(base_title, keywords, products)
            else:
                # Default content for unknown platforms
                content = {
                    'title': f"{base_title} - {platform.title()} Edition",
                    'description': f"Discover the best {base_title.lower()} content for {platform}!",
                    'tags': keywords[:10]
                }
            
            logger.info(f"✅ Test: {platform.title()} content generated successfully")
            print(f"🧪 TEST: {platform.upper()} content generated - Title: {len(content['title'])} chars")
            
            return {
                'success': True,
                'platform': platform,
                'content': content,
                'character_counts': {
                    'title': len(content['title']),
                    'description': len(content['description'])
                },
                'test_mode': True,
                'api_usage': 0  # No API tokens used in test mode
            }
            
        except Exception as e:
            logger.error(f"❌ Test error generating {platform} content: {str(e)}")
            return {
                'success': False,
                'platform': platform,
                'error': str(e),
                'test_mode': True
            }
    
    async def _generate_youtube_content(self, base_title: str, keywords: List[str], products: List[Dict]) -> Dict:
        """Generate hardcoded YouTube-specific content"""
        
        # Extract product category from title
        category = self._extract_category(base_title)
        
        title = f"Top 5 {category.title()} with THOUSANDS of Reviews (2025 Amazon Finds)"
        
        description = f"""🔥 Discover the TOP 5 {category} that are absolutely crushing it on Amazon right now!

⭐ What You'll Learn:
• Best {category} with 4.5+ star ratings
• Honest reviews from real customers  
• Why these products are trending in 2025
• Direct Amazon links (affiliate)

🎯 Products Featured:
1. Premium {category} - 4.8 stars, 2000+ reviews
2. Best Value {category} - 4.7 stars, 1800+ reviews
3. Professional Grade {category} - 4.6 stars, 1400+ reviews
4. Advanced {category} - 4.5 stars, 980+ reviews
5. Budget-Friendly {category} - 4.4 stars, 750+ reviews

💡 Why Trust This List?
✅ Real Amazon data & reviews
✅ Updated weekly for 2025
✅ Tested by our expert team

🔔 Subscribe for more Amazon finds!
👍 Like if this helped you decide!

#Amazon #ProductReview #{category.replace(' ', '')} #Shopping #2025"""

        return {
            'title': title[:100],  # YouTube title limit
            'description': description[:5000],  # YouTube description limit
            'tags': keywords[:15],
            'category': 'Howto & Style',
            'visibility': 'public'
        }
    
    async def _generate_tiktok_content(self, base_title: str, keywords: List[str], products: List[Dict]) -> Dict:
        """Generate hardcoded TikTok-specific content"""
        
        category = self._extract_category(base_title)
        
        title = f"5 VIRAL {category.upper()} Everyone's Buying on Amazon! 🔥"
        
        description = f"""These {category} are going VIRAL on Amazon! 🤯

✨ All have 4.5+ stars & 1000+ reviews
🛒 Links in bio!

#Amazon #ProductReview #{category.replace(' ', '')} #Viral #Shopping #2025 #amazonfinds #musthave"""

        return {
            'title': title[:100],  # TikTok title limit
            'description': description[:300],  # TikTok description limit  
            'hashtags': [f"#{kw.lower().replace(' ', '')}" for kw in keywords[:10]],
            'trending_sounds': ['trending_sound_1', 'viral_audio_2024'],
            'effects': ['trending_effect_1', 'popular_filter_2025']
        }
    
    async def _generate_instagram_content(self, base_title: str, keywords: List[str], products: List[Dict]) -> Dict:
        """Generate hardcoded Instagram-specific content"""
        
        category = self._extract_category(base_title)
        
        title = f"⭐ 5 VIRAL {category.title()} With THOUSANDS of 5-Star Reviews!"
        
        description = f"""🔥 The {category} that are absolutely CRUSHING IT on Amazon right now! 

✨ What makes these special:
• 4.5+ star ratings across the board
• Thousands of verified reviews  
• Trending hard in 2025
• Ships with Prime

💫 Swipe to see why everyone's obsessed ➡️

🛒 Shop these (link in bio!)

Follow @amazonfinds2025 for daily finds! 

#{' #'.join([kw.lower().replace(' ', '') for kw in keywords[:20]])}
#amazonfinds #musthave #viral #shopping #productreview #2025finds"""

        return {
            'title': title[:125],  # Instagram title limit
            'description': description[:2200],  # Instagram description limit
            'hashtags': [f"#{kw.lower().replace(' ', '')}" for kw in keywords[:30]],
            'story_stickers': ['poll', 'quiz', 'swipe_up'],
            'reel_format': '9:16_vertical'
        }
    
    async def _generate_wordpress_content(self, base_title: str, keywords: List[str], products: List[Dict]) -> Dict:
        """Generate hardcoded WordPress SEO content"""
        
        category = self._extract_category(base_title)
        
        title = f"Top 5 {category.title()} with Best Amazon Reviews (2025 Updated)"
        
        description = f"Discover the top-rated {category} on Amazon with 4.5+ stars and thousands of reviews. Updated for 2025 with honest reviews and direct purchase links."
        
        return {
            'title': title[:150],  # WordPress SEO title limit
            'description': description[:160],  # Meta description limit
            'keywords': keywords[:15],
            'slug': f"best-{category.lower().replace(' ', '-')}-amazon-2025",
            'category': 'Product Reviews',
            'tags': keywords[:10]
        }
    
    def _extract_category(self, title: str) -> str:
        """Extract product category from title"""
        # Simple extraction for test mode
        title_lower = title.lower()
        
        # Common categories
        categories = {
            'gaming headset': 'Gaming Headsets',
            'car amp': 'Car Amplifiers', 
            'marine sub': 'Marine Subwoofers',
            'monitor': 'Computer Monitors',
            'power strip': 'Power Strips',
            'camera stabilizer': 'Camera Stabilizers',
            'kitchen knife': 'Kitchen Knives',
            'bluetooth speaker': 'Bluetooth Speakers',
            'phone case': 'Phone Cases'
        }
        
        for keyword, category in categories.items():
            if keyword in title_lower:
                return category
        
        # Default extraction
        words = title_lower.split()
        meaningful_words = [w for w in words if w not in ['top', 'best', '5', 'insane', 'new', '2025']][:2]
        return ' '.join(meaningful_words).title() if meaningful_words else 'Products'
    
    async def generate_all_platform_content(self, 
                                          base_title: str, 
                                          keywords: List[str], 
                                          products: List[Dict]) -> Dict:
        """Generate content for all platforms"""
        
        logger.info(f"🚀 Test: Generating content for all platforms: {base_title[:50]}...")
        print(f"🧪 TEST: Generating content for all platforms")
        
        platforms = ['youtube', 'tiktok', 'instagram', 'wordpress']
        results = {}
        
        for platform in platforms:
            result = await self.generate_platform_content(platform, base_title, keywords, products)
            results[platform] = result
        
        # Summary
        successful_platforms = sum(1 for r in results.values() if r['success'])
        total_chars = sum(r.get('character_counts', {}).get('title', 0) + 
                         r.get('character_counts', {}).get('description', 0) 
                         for r in results.values() if r['success'])
        
        logger.info(f"✅ Test: Generated content for {successful_platforms}/{len(platforms)} platforms")
        print(f"🧪 TEST: All platform content generated - {successful_platforms}/{len(platforms)} successful")
        
        return {
            'success': True,
            'platforms': results,
            'summary': {
                'successful_platforms': successful_platforms,
                'total_platforms': len(platforms),
                'total_characters': total_chars
            },
            'test_mode': True,
            'api_usage': 0
        }

async def test_generate_platform_content_for_workflow(title: str, category: str, config: Dict) -> Dict:
    """Test function expected by Test_workflow_runner.py"""
    print(f"🧪 TEST: Generating platform content for: {title[:50]}... (no API calls)")
    
    # Simulate processing delay
    await asyncio.sleep(0.1)
    
    # Return hardcoded multi-platform content
    return {
        'success': True,
        'youtube_title': f'5 {category} Products That Will CHANGE Your Life (Amazon Bestsellers 2025)',
        'youtube_description': f'🔥 DISCOVER the {category.lower()} products that pros swear by! These Amazon bestsellers have helped thousands achieve amazing results.',
        'youtube_tags': f'{category.lower()}, amazon finds, product review, 2025 bestsellers',
        'instagram_caption': f'📸✨ {category.upper()} GAME-CHANGERS!\n\nThese 5 products are ESSENTIAL! 🔥\n\n#Amazon #ProductReview #{category}',
        'wordpress_title': f'The Ultimate {category} Guide: 5 Essential Products You Need (2025)',
        'wordpress_content': f'<h2>Best {category} Products on Amazon</h2><p>After extensive research, we\'ve identified the top 5 {category.lower()} products.</p>',
        'tiktok_caption': f'📸 POV: You discover the {category.lower()} products that pros use! ✨ #ProductReview #{category} #AmazonFinds',
        'platforms_generated': ['YouTube', 'Instagram', 'WordPress', 'TikTok'],
        'seo_optimized': True,
        'engagement_score': 95,
        'api_calls_used': 0,
        'processing_time': '0.1s'
    }

# Test function
if __name__ == "__main__":
    async def test_generator():
        config = {
            'anthropic_api_key': 'test-key'
        }
        
        generator = TestPlatformContentGenerator(config)
        
        test_data = {
            'base_title': "Top 5 Gaming Headsets",
            'keywords': ['gaming', 'headsets', 'audio', 'pc gaming', 'esports'],
            'products': [
                {'title': 'Gaming Headset 1', 'rating': 4.8},
                {'title': 'Gaming Headset 2', 'rating': 4.7},
                {'title': 'Gaming Headset 3', 'rating': 4.6},
                {'title': 'Gaming Headset 4', 'rating': 4.5},
                {'title': 'Gaming Headset 5', 'rating': 4.4}
            ]
        }
        
        print("🧪 Testing Platform Content Generator")
        print("=" * 50)
        
        result = await generator.generate_all_platform_content(
            test_data['base_title'],
            test_data['keywords'], 
            test_data['products']
        )
        
        print(f"\n📊 Test Result: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
        print(f"🧪 Platforms: {result['summary']['successful_platforms']}/{result['summary']['total_platforms']}")
        print(f"🧪 API Usage: {result['api_usage']} tokens")
        
    asyncio.run(test_generator())