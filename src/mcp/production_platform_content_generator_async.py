#!/usr/bin/env python3
"""
Production Platform Content Generator - Async Optimized Version
================================================================

Generates all platform content (YouTube, Instagram, TikTok, WordPress) concurrently.
Reduces generation time from ~15 seconds to ~3-4 seconds.

Key Optimizations:
- All platform content generated in parallel
- Shared keyword generation for all platforms
- Async OpenAI API calls using AsyncOpenAI client
"""

import openai
import re
import asyncio
import time
from typing import Dict, List
from datetime import datetime
import json

class ProductionPlatformContentGeneratorAsync:
    def __init__(self, openai_api_key: str):
        self.api_key = openai_api_key
        # Use async client for concurrent requests
        self.async_client = openai.AsyncOpenAI(api_key=openai_api_key)
        # Keep sync client for backward compatibility
        self.sync_client = openai.OpenAI(api_key=openai_api_key)
    
    async def generate_keyword_optimized_content_async(
        self, 
        title: str, 
        category: str, 
        products: List[Dict] = None, 
        variant_used: str = ""
    ) -> Dict:
        """Generate all platform content concurrently with keyword optimization"""
        
        start_time = time.time()
        print(f"🚀 Starting concurrent platform content generation...")
        
        # First, generate keywords (needed by all platforms)
        keywords = await self._generate_keywords_from_products_async(title, category, products, variant_used)
        
        # Create all content generation tasks to run in parallel
        tasks = [
            # Video title for intro
            self._generate_intro_video_title_async(title, keywords),
            
            # YouTube content
            self._generate_youtube_content_async(title, category, keywords, products),
            
            # Instagram content
            self._generate_instagram_content_async(title, keywords, category),
            
            # TikTok content
            self._generate_tiktok_content_async(title, keywords, category),
            
            # WordPress content
            self._generate_wordpress_content_async(title, category, keywords, products)
        ]
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        content = {}
        
        # Handle video title
        if not isinstance(results[0], Exception):
            content['video_title'] = results[0]
        else:
            print(f"⚠️ Error generating video title: {results[0]}")
            content['video_title'] = self._get_fallback_video_title(title)
        
        # Handle YouTube content
        if not isinstance(results[1], Exception):
            content.update(results[1])
        else:
            print(f"⚠️ Error generating YouTube content: {results[1]}")
            content.update(self._get_fallback_youtube_content(title))
        
        # Handle Instagram content
        if not isinstance(results[2], Exception):
            content.update(results[2])
        else:
            print(f"⚠️ Error generating Instagram content: {results[2]}")
            content.update(self._get_fallback_instagram_content(title, category))
        
        # Handle TikTok content
        if not isinstance(results[3], Exception):
            content.update(results[3])
        else:
            print(f"⚠️ Error generating TikTok content: {results[3]}")
            content.update(self._get_fallback_tiktok_content(title, category))
        
        # Handle WordPress content
        if not isinstance(results[4], Exception):
            content.update(results[4])
        else:
            print(f"⚠️ Error generating WordPress content: {results[4]}")
            content.update(self._get_fallback_wordpress_content(title))
        
        # Add keywords
        content['wordpress_keywords'] = keywords.get('seo_keywords', [])
        
        elapsed = time.time() - start_time
        print(f"✅ Generated all platform content in {elapsed:.1f} seconds (vs ~15 seconds sequential)")
        
        return content
    
    async def _generate_keywords_from_products_async(
        self, 
        title: str, 
        category: str, 
        products: List[Dict], 
        variant_used: str
    ) -> Dict[str, List[str]]:
        """Generate comprehensive keyword sets from actual scraped products"""
        
        # Extract keywords from real product data
        product_keywords = []
        brand_keywords = []
        feature_keywords = []
        
        if products:
            for product in products:
                product_title = product.get('title', '')
                product_keywords.extend(self._extract_keywords_from_text(product_title))
                brands = self._extract_brands(product_title)
                brand_keywords.extend(brands)
                features = self._extract_features(product_title)
                feature_keywords.extend(features)
        
        keyword_prompt = f"""
        Generate SEO-optimized keywords for this product review content:
        
        Title: {title}
        Category: {category}
        Search Variant Used: {variant_used}
        
        Real Products Found:
        {self._format_products_for_prompt(products)}
        
        Generate keyword sets:
        1. Primary Keywords (5)
        2. Long-tail Keywords (5)
        3. Brand Keywords (5)
        4. Feature Keywords (5)
        5. Trending Social Media Keywords (10)
        6. SEO Meta Keywords (10)
        
        Format as JSON with arrays for each category.
        """
        
        try:
            response = await self.async_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an SEO and social media keyword expert."},
                    {"role": "user", "content": keyword_prompt}
                ],
                max_completion_tokens=500
            )
            
            keywords_text = response.choices[0].message.content
            json_match = re.search(r'\{.*\}', keywords_text, re.DOTALL)
            
            if json_match:
                keywords_data = json.loads(json_match.group(0))
                return {
                    'primary_keywords': keywords_data.get('primary_keywords', [])[:5],
                    'longtail_keywords': keywords_data.get('longtail_keywords', [])[:5],
                    'brand_keywords': keywords_data.get('brand_keywords', brand_keywords)[:5],
                    'feature_keywords': keywords_data.get('feature_keywords', feature_keywords)[:5],
                    'social_keywords': keywords_data.get('trending_social_media_keywords', [])[:10],
                    'seo_keywords': keywords_data.get('seo_meta_keywords', [])[:10]
                }
        except Exception as e:
            print(f"⚠️ Keyword generation error: {e}")
            return self._get_fallback_keywords(title, category)
    
    async def _generate_intro_video_title_async(self, title: str, keywords: Dict) -> str:
        """Generate video intro title"""
        try:
            prompt = f"""Create a 7-word attention-grabbing video intro title for: {title}
            Use keywords: {', '.join(keywords.get('primary_keywords', [])[:2])}
            Make it exciting and memorable."""
            
            response = await self.async_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_completion_tokens=50
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise e
    
    async def _generate_youtube_content_async(
        self, 
        title: str, 
        category: str, 
        keywords: Dict, 
        products: List[Dict]
    ) -> Dict:
        """Generate YouTube title and description concurrently"""
        
        title_prompt = f"""Create YouTube Shorts title (max 60 chars) for: {title}
        Include keywords: {', '.join(keywords.get('primary_keywords', [])[:2])}
        Requirements: Under 60 chars, include #shorts, current year 2025, engaging"""
        
        desc_prompt = f"""Create YouTube description (2000-5000 chars) for top 5 {title} review.
        Include: Product details, timestamps, affiliate disclaimer, keywords: {', '.join(keywords.get('seo_keywords', [])[:5])}"""
        
        # Run both in parallel
        title_task = self.async_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": title_prompt}],
            max_completion_tokens=100
        )
        
        desc_task = self.async_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": desc_prompt}],
            max_completion_tokens=800
        )
        
        title_response, desc_response = await asyncio.gather(title_task, desc_task)
        
        return {
            'youtube_title': title_response.choices[0].message.content.strip()[:100],
            'youtube_description': desc_response.choices[0].message.content.strip()
        }
    
    async def _generate_instagram_content_async(
        self, 
        title: str, 
        keywords: Dict,
        category: str
    ) -> Dict:
        """Generate Instagram caption and hashtags concurrently"""
        
        caption_prompt = f"""Create Instagram caption for: {title}
        Include trending keywords: {', '.join(keywords.get('social_keywords', [])[:3])}
        Requirements: Emojis, engagement hooks, max 2200 chars"""
        
        hashtag_prompt = f"""Generate 30 Instagram hashtags for {category} product review.
        Mix popular and niche tags. Format as single line with # prefix."""
        
        # Run both in parallel
        caption_task = self.async_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": caption_prompt}],
            max_completion_tokens=400
        )
        
        hashtag_task = self.async_client.chat.completions.create(
            model="gpt-4o-mini",  # Use smaller model for hashtags
            messages=[{"role": "user", "content": hashtag_prompt}],
            max_completion_tokens=200
        )
        
        caption_response, hashtag_response = await asyncio.gather(caption_task, hashtag_task)
        
        return {
            'instagram_caption': caption_response.choices[0].message.content.strip()[:2200],
            'instagram_hashtags': hashtag_response.choices[0].message.content.strip()
        }
    
    async def _generate_tiktok_content_async(
        self, 
        title: str, 
        keywords: Dict,
        category: str
    ) -> Dict:
        """Generate TikTok caption and hashtags concurrently"""
        
        caption_prompt = f"""Create TikTok caption for: {title}
        Include keywords: {', '.join(keywords.get('social_keywords', [])[:3])}
        Requirements: Hook questions, max 150 chars"""
        
        hashtag_prompt = f"""Generate 8 viral TikTok hashtags for {category}.
        Include #fyp #viral and category-specific tags."""
        
        # Run both in parallel
        caption_task = self.async_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": caption_prompt}],
            max_completion_tokens=100
        )
        
        hashtag_task = self.async_client.chat.completions.create(
            model="gpt-4o-mini",  # Use smaller model for hashtags
            messages=[{"role": "user", "content": hashtag_prompt}],
            max_completion_tokens=100
        )
        
        caption_response, hashtag_response = await asyncio.gather(caption_task, hashtag_task)
        
        return {
            'tiktok_caption': caption_response.choices[0].message.content.strip()[:150],
            'tiktok_hashtags': hashtag_response.choices[0].message.content.strip()
        }
    
    async def _generate_wordpress_content_async(
        self, 
        title: str, 
        category: str, 
        keywords: Dict, 
        products: List[Dict]
    ) -> Dict:
        """Generate WordPress title and content concurrently"""
        
        title_prompt = f"""Create SEO blog title for: {title}
        Include keywords: {', '.join(keywords.get('primary_keywords', [])[:2])}
        Requirements: Max 60 chars, include 2025, power words"""
        
        content_prompt = f"""Create WordPress article (1500-3000 words) for top 5 {title} review.
        Include: Introduction, product comparisons, buying guide, conclusion.
        Keywords: {', '.join(keywords.get('seo_keywords', [])[:10])}"""
        
        # Run both in parallel
        title_task = self.async_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": title_prompt}],
            max_completion_tokens=100
        )
        
        content_task = self.async_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": content_prompt}],
            max_completion_tokens=2000
        )
        
        title_response, content_response = await asyncio.gather(title_task, content_task)
        
        return {
            'wordpress_title': title_response.choices[0].message.content.strip()[:60],
            'wordpress_description': content_response.choices[0].message.content.strip()
        }
    
    # Helper methods
    def _extract_keywords_from_text(self, text: str) -> List[str]:
        """Extract keywords from text"""
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        return list(set(words))[:10]
    
    def _extract_brands(self, text: str) -> List[str]:
        """Extract brand names from product title"""
        # Common patterns for brands (usually capitalized words at the beginning)
        words = text.split()
        brands = [w for w in words[:3] if w[0].isupper() and len(w) > 2]
        return brands
    
    def _extract_features(self, text: str) -> List[str]:
        """Extract product features from title"""
        feature_patterns = [
            r'adjustable', r'wireless', r'portable', r'waterproof', 
            r'rechargeable', r'smart', r'pro', r'premium', r'hd', r'4k'
        ]
        features = []
        text_lower = text.lower()
        for pattern in feature_patterns:
            if pattern in text_lower:
                features.append(pattern)
        return features
    
    def _format_products_for_prompt(self, products: List[Dict]) -> str:
        """Format products for prompt"""
        if not products:
            return "No products available"
        
        formatted = []
        for i, p in enumerate(products[:5], 1):
            formatted.append(f"{i}. {p.get('title', 'Product')} - ${p.get('price', 'N/A')}")
        return '\n'.join(formatted)
    
    # Fallback methods
    def _get_fallback_keywords(self, title: str, category: str) -> Dict:
        """Fallback keywords if generation fails"""
        return {
            'primary_keywords': [title.lower(), category.lower(), 'best', 'top', '2025'],
            'longtail_keywords': [f'best {title.lower()} 2025', f'top rated {title.lower()}'],
            'brand_keywords': [],
            'feature_keywords': [],
            'social_keywords': ['viral', 'musthave', 'trending', 'review'],
            'seo_keywords': [title.lower(), category.lower(), 'review', 'amazon', 'best']
        }
    
    def _get_fallback_video_title(self, title: str) -> str:
        """Fallback video title"""
        return f"Top 5 {title} Review"
    
    def _get_fallback_youtube_content(self, title: str) -> Dict:
        """Fallback YouTube content"""
        return {
            'youtube_title': f'{title} - Top 5 Best Picks 2025 #shorts',
            'youtube_description': f'Check out the top 5 {title} available on Amazon in 2025.'
        }
    
    def _get_fallback_instagram_content(self, title: str, category: str) -> Dict:
        """Fallback Instagram content"""
        return {
            'instagram_caption': f'🔥 Top 5 {title} you need to see! Swipe for details ➡️',
            'instagram_hashtags': f'#{category.lower()} #amazonfinds #top5 #2025 #review'
        }
    
    def _get_fallback_tiktok_content(self, title: str, category: str) -> Dict:
        """Fallback TikTok content"""
        return {
            'tiktok_caption': f'POV: You found the best {title} on Amazon 🤯',
            'tiktok_hashtags': f'#fyp #viral #{category.lower()} #amazonfinds'
        }
    
    def _get_fallback_wordpress_content(self, title: str) -> Dict:
        """Fallback WordPress content"""
        return {
            'wordpress_title': f'Best {title} 2025 - Top 5 Reviews',
            'wordpress_description': f'Comprehensive review of the top 5 {title} available in 2025.'
        }

# Wrapper function for backward compatibility
async def production_generate_platform_content_for_workflow_async(
    title: str,
    category: str,
    config: Dict,
    products: List[Dict] = None,
    variant_used: str = ""
) -> Dict:
    """Async wrapper for workflow integration"""
    
    generator = ProductionPlatformContentGeneratorAsync(config.get('openai_api_key'))
    
    # Generate all content concurrently
    content = await generator.generate_keyword_optimized_content_async(
        title=title,
        category=category,
        products=products,
        variant_used=variant_used
    )
    
    # Format for Airtable fields
    return {
        'VideoTitle': content.get('video_title', ''),
        'VideoDescription': f"Top 5 {title} Review",
        'YouTubeTitle': content.get('youtube_title', ''),
        'YouTubeDescription': content.get('youtube_description', ''),
        'InstagramCaption': content.get('instagram_caption', ''),
        'InstagramHashtags': content.get('instagram_hashtags', ''),
        'TikTokCaption': content.get('tiktok_caption', ''),
        'TikTokHashtags': content.get('tiktok_hashtags', ''),
        'WordPressTitle': content.get('wordpress_title', ''),
        'WordPressContent': content.get('wordpress_description', ''),
        'UniversalKeywords': ', '.join(content.get('wordpress_keywords', [])) if content.get('wordpress_keywords') else title.lower()
    }

# Keep original name for compatibility
production_generate_platform_content_for_workflow = production_generate_platform_content_for_workflow_async