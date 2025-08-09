#!/usr/bin/env python3
"""
Test Content Generation MCP Server - Hardcoded responses for testing
Purpose: Test content generation without consuming API tokens
"""

from typing import Dict, List, Any

class TestContentGenerationMCPServer:
    """Test Content Generation MCP Server with hardcoded responses"""
    
    def __init__(self, anthropic_api_key: str):
        self.anthropic_api_key = anthropic_api_key  # Not used in test mode
        
        # Hardcoded high-quality content responses
        self.hardcoded_responses = {
            'video_content': {
                'VideoTitle': '⭐ 5 VIRAL Camera Cleaning Brushes With THOUSANDS of 5-Star Reviews! (2025 Edition)',
                'VideoDescription': '''Discover the TOP 5 camera cleaning brushes that photographers LOVE! These Amazon bestsellers have thousands of 5-star reviews and will keep your gear spotless. From DSLR sensors to lens filters, these tools are GAME-CHANGERS! 📸✨

🎯 What You'll Learn:
• Best brush for delicate sensors
• Most popular lens cleaning tools
• Professional-grade cleaning solutions
• Money-saving cleaning kits
• Expert cleaning techniques

💡 Perfect for: Photographers, camera enthusiasts, content creators, and anyone wanting crystal-clear shots!''',
                'IntroHook': '''Are you tired of dust spots ruining your perfect shots? Today I'm revealing the TOP 5 camera cleaning brushes that have revolutionized photography maintenance!''',
                'OutroCallToAction': '''Which cleaning brush caught your eye? Drop a comment below and don't forget to subscribe for more photography gear reviews!'''
            },
            'youtube_content': {
                'YouTubeTitle': '5 Camera Cleaning Brushes That Will SAVE Your Photography (Amazon Bestsellers 2025)',
                'YouTubeDescription': '''🔥 DISCOVER the camera cleaning brushes that pros swear by! These Amazon bestsellers have helped thousands of photographers achieve crystal-clear shots.

📸 FEATURED PRODUCTS:
✅ Professional sensor cleaning brushes
✅ Lens cleaning kits with microfiber
✅ Anti-static brush sets
✅ Precision cleaning tools
✅ Complete maintenance solutions

🎯 PERFECT FOR:
• DSLR & Mirrorless cameras
• Lens cleaning & maintenance
• Sensor cleaning (safe methods)
• Filter & UV lens care
• Professional photo gear

💰 SAVE MONEY: Compare prices and find the best deals on these essential photography tools!

🔔 SUBSCRIBE for more camera gear reviews, photography tips, and equipment recommendations!

⏰ Timestamps:
0:00 - Introduction
0:10 - #5 Budget-Friendly Option
0:20 - #4 Professional Grade
0:30 - #3 Versatile All-in-One
0:40 - #2 Premium Choice
0:50 - #1 Editor's Pick

#CameraCleaning #Photography #AmazonFinds #CameraGear #PhotographyTips''',
                'YouTubeTags': 'camera cleaning, photography, camera gear, lens cleaning, DSLR maintenance, camera brushes, photography equipment, Amazon finds, camera care, professional photography'
            },
            'instagram_content': {
                'InstagramCaption': '''📸✨ CAMERA CLEANING GAME-CHANGERS! 

These 5 brushes are ESSENTIAL for any photographer! 🔥

🎯 Why photographers LOVE these:
• Crystal clear shots every time
• Thousands of 5-star reviews
• Professional results at home
• Saves $$$ on professional cleaning

💡 Swipe to see which one made #1! ➡️

Which cleaning tool do YOU need most? 👇

#CameraCleaning #Photography #CameraGear #PhotographyTips #AmazonFinds #DSLR #Mirrorless #LensCleaning #PhotoEquipment #PhotographyLife #CameraAccessories #PhotoGear #PhotographyEssentials #CameraCare #ProfessionalPhotography'''
            },
            'wordpress_content': {
                'WordPressTitle': 'The Ultimate Guide to Camera Cleaning: 5 Essential Brushes Every Photographer Needs (2025)',
                'WordPressContent': '''<h2>Keep Your Camera Gear Spotless with These Professional-Grade Cleaning Tools</h2>

<p>As a photographer, maintaining your equipment is crucial for capturing those perfect shots. Dust, fingerprints, and debris can seriously impact your image quality. After extensive research and testing, we've identified the <strong>5 best camera cleaning brushes</strong> that will keep your gear in pristine condition.</p>

<h3>Why Proper Camera Cleaning Matters</h3>
<ul>
<li>Prevents dust spots on your images</li>
<li>Extends equipment lifespan</li>
<li>Maintains resale value</li>
<li>Ensures professional image quality</li>
</ul>

<h3>Our Top 5 Camera Cleaning Brushes</h3>
<p>Each product below has been carefully selected based on customer reviews, professional recommendations, and real-world testing.</p>'''
            },
            'tiktok_content': {
                'TikTokCaption': '📸 POV: You discover the camera cleaning brushes that pros use! ✨ These 5 tools will change your photography game forever! Which one are you getting? 👇 #CameraCleaning #Photography #CameraGear #PhotographyTips #TechTok #CameraHacks #DSLR #PhotographyLife'
            }
        }
        
        print("🧪 Test Content Generation Server initialized with hardcoded responses")
    
    async def generate_video_content(self, title: str, category: str = None) -> Dict[str, Any]:
        """Generate hardcoded video content for testing"""
        print(f"📝 Generating test video content for: {title[:50]}... (no API call)")
        
        return {
            'success': True,
            'content': self.hardcoded_responses['video_content'],
            'model_used': 'test_model',
            'tokens_used': 0  # No tokens used in test mode
        }
    
    async def generate_platform_content(self, title: str, platform: str, category: str = None) -> Dict[str, Any]:
        """Generate hardcoded platform-specific content"""
        print(f"📱 Generating test {platform} content for: {title[:30]}... (no API call)")
        
        platform_key = f"{platform.lower()}_content"
        content = self.hardcoded_responses.get(platform_key, {})
        
        return {
            'success': True,
            'content': content,
            'platform': platform,
            'model_used': 'test_model',
            'tokens_used': 0
        }
    
    async def generate_product_descriptions(self, products: List[Dict], style: str = 'engaging') -> Dict[str, Any]:
        """Generate hardcoded product descriptions"""
        print(f"🛍️ Generating test descriptions for {len(products)} products (no API call)")
        
        # Hardcoded product descriptions
        descriptions = [
            "This professional-grade cleaning brush features ultra-soft bristles perfect for delicate camera sensors and lenses.",
            "An all-in-one cleaning solution with microfiber cloths, brushes, and cleaning solution for complete camera maintenance.",
            "Anti-static brush design prevents dust attraction while safely removing particles from sensitive equipment.",
            "Precision cleaning tools with ergonomic grip for detailed maintenance of professional photography gear.",
            "Complete cleaning kit with multiple brush sizes for comprehensive camera and lens care."
        ]
        
        result_descriptions = {}
        for i, product in enumerate(products[:5]):
            result_descriptions[f'product_{i+1}'] = descriptions[i % len(descriptions)]
        
        return {
            'success': True,
            'descriptions': result_descriptions,
            'style': style,
            'tokens_used': 0
        }
    
    async def optimize_for_seo(self, content: str, keywords: List[str]) -> Dict[str, Any]:
        """Return hardcoded SEO-optimized content"""
        print(f"🎯 SEO optimizing content with {len(keywords)} keywords (no API call)")
        
        return {
            'success': True,
            'optimized_content': content + " [SEO OPTIMIZED - TEST MODE]",
            'keywords_used': keywords,
            'seo_score': 95,  # Hardcoded high score
            'tokens_used': 0
        }
    
    async def generate_hashtags(self, content: str, platform: str, count: int = 20) -> List[str]:
        """Generate hardcoded hashtags for testing"""
        print(f"#️⃣ Generating {count} test hashtags for {platform} (no API call)")
        
        base_hashtags = [
            '#CameraCleaning', '#Photography', '#CameraGear', '#PhotographyTips',
            '#AmazonFinds', '#DSLR', '#Mirrorless', '#LensCleaning',
            '#PhotoEquipment', '#PhotographyLife', '#CameraAccessories',
            '#PhotoGear', '#PhotographyEssentials', '#CameraCare',
            '#ProfessionalPhotography', '#PhotographyHacks', '#CameraHacks',
            '#TechReview', '#ProductReview', '#PhotographyCommunity'
        ]
        
        return base_hashtags[:count]
    
    async def close(self):
        """Close test server (no cleanup needed)"""
        print("🧪 Test Content Generation Server closed")
        pass