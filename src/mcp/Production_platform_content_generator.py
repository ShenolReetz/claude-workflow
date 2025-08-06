#!/usr/bin/env python3
"""
Production Platform Content Generator with Advanced Keyword Optimization
========================================================================

Generates platform-specific content with:
- SEO-optimized keywords from scraped products
- Trending hashtags for each platform
- Platform-specific optimization strategies
- Real product data integration
"""

import openai
import re
from typing import Dict, List
from datetime import datetime

class ProductionPlatformContentGenerator:
    def __init__(self, openai_api_key: str):
        self.client = openai.OpenAI(api_key=openai_api_key)
    
    async def generate_keyword_optimized_content(
        self, 
        title: str, 
        category: str, 
        products: List[Dict] = None, 
        variant_used: str = ""
    ) -> Dict:
        """Generate platform content with keyword optimization based on real product data"""
        
        # Generate keywords from product data
        keywords = await self._generate_keywords_from_products(title, category, products, variant_used)
        
        # Generate platform-specific content
        content = {}
        
        # ✅ Video Title for Intro Scene (max 7 words, attention-grabbing)
        content['video_title'] = await self._generate_intro_video_title(title, keywords)
        
        # YouTube Shorts optimization
        content['youtube_title'] = await self._generate_youtube_title(title, keywords)
        content['youtube_description'] = await self._generate_youtube_description(title, category, keywords, products)
        
        # Instagram optimization
        content['instagram_caption'] = await self._generate_instagram_caption(title, keywords)
        content['instagram_hashtags'] = await self._generate_instagram_hashtags(category, keywords)
        
        # TikTok optimization  
        content['tiktok_caption'] = await self._generate_tiktok_caption(title, keywords)
        content['tiktok_hashtags'] = await self._generate_tiktok_hashtags(category, keywords)
        
        # WordPress/Blog SEO optimization
        content['wordpress_title'] = await self._generate_seo_title(title, keywords)
        content['wordpress_description'] = await self._generate_seo_description(title, category, keywords, products)
        content['wordpress_keywords'] = keywords['seo_keywords']
        
        return content
    
    async def _generate_keywords_from_products(
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
                # Extract from product titles
                product_title = product.get('title', '')
                product_keywords.extend(self._extract_keywords_from_text(product_title))
                
                # Extract brands
                brands = self._extract_brands(product_title)
                brand_keywords.extend(brands)
                
                # Extract features
                features = self._extract_features(product_title)
                feature_keywords.extend(features)
        
        # Create comprehensive keyword prompt
        keyword_prompt = f"""
        Generate SEO-optimized keywords for this product review content:
        
        Title: {title}
        Category: {category}
        Search Variant Used: {variant_used}
        
        Real Products Found:
        {self._format_products_for_prompt(products)}
        
        Generate keyword sets for:
        1. Primary Keywords (high search volume)
        2. Long-tail Keywords (specific, less competitive)
        3. Brand Keywords (from actual products)
        4. Feature Keywords (product characteristics)
        5. Trending Social Media Keywords
        6. SEO Meta Keywords
        
        Format as JSON with arrays for each category.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an SEO and social media keyword expert. Generate high-performing keywords based on real product data."},
                    {"role": "user", "content": keyword_prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            # Parse JSON response
            import json
            keywords_text = response.choices[0].message.content
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', keywords_text, re.DOTALL)
            if json_match:
                keywords_data = json.loads(json_match.group(0))
                return {
                    'primary_keywords': keywords_data.get('primary_keywords', []),
                    'longtail_keywords': keywords_data.get('longtail_keywords', []),
                    'brand_keywords': keywords_data.get('brand_keywords', brand_keywords),
                    'feature_keywords': keywords_data.get('feature_keywords', feature_keywords),
                    'social_keywords': keywords_data.get('trending_social_media_keywords', []),
                    'seo_keywords': keywords_data.get('seo_meta_keywords', [])
                }
            
        except Exception as e:
            print(f"⚠️ Keyword generation error: {e}")
        
        # Fallback keyword generation
        return self._generate_fallback_keywords(title, category, variant_used)
    
    async def _generate_intro_video_title(self, title: str, keywords: Dict) -> str:
        """Generate attention-grabbing video title for intro scene (max 7 words)"""
        
        primary_kw = keywords.get('primary_keywords', [])[:2]
        
        intro_title_prompt = f"""
        Create a SHORT, attention-grabbing title for the intro scene of: {title}
        
        Requirements:
        - MAXIMUM 7 words only
        - Must stay relevant to original title
        - Use power words and emotional triggers
        - Include excitement hooks like "Must See!", "Amazing!", "Insane!"
        - Include numbers if possible
        - Make it exciting and clickable
        - Include these key terms: {', '.join(primary_kw)}
        
        Examples of PERFECT 7-word intro titles with hooks:
        - "Top 5 Gaming Chairs - Must See!"
        - "Best Phone Cases - Amazing Deals!"
        - "Kitchen Gadgets Everyone Needs - Insane!"
        - "Camera Cleaning Brushes - Must Have!"
        - "Webcam Stands You Need - Incredible!"
        
        Original title: {title}
        Create the perfect 7-word intro title with excitement hook:
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert at creating short, punchy video titles that grab attention instantly. Always stay under 7 words and keep it relevant."},
                    {"role": "user", "content": intro_title_prompt}
                ],
                temperature=0.8,
                max_tokens=50
            )
            
            generated_title = response.choices[0].message.content.strip()
            
            # Clean up the response (remove quotes, extra text)
            generated_title = generated_title.replace('"', '').replace("'", '').strip()
            
            # Count words and truncate if needed
            words = generated_title.split()
            if len(words) > 7:
                generated_title = ' '.join(words[:7])
            
            # Fallback if empty
            if not generated_title or len(words) == 0:
                raise Exception("Empty title generated")
            
            return generated_title
            
        except Exception as e:
            print(f"⚠️ Intro title generation error: {e}")
            # Intelligent fallback based on original title
            return self._create_fallback_intro_title(title)
    
    def _create_fallback_intro_title(self, title: str) -> str:
        """Create fallback intro title with excitement hooks when AI generation fails"""
        
        # Excitement hooks to choose from
        excitement_hooks = ["Must See!", "Amazing!", "Incredible!", "Must Have!", "Insane!", "Wow!"]
        
        # Extract key elements from original title
        words = title.split()
        
        # Look for "Top X" pattern
        if 'top' in title.lower() and any(word.isdigit() for word in words):
            number = next((word for word in words if word.isdigit()), '5')
            # Find the main product/category
            product_words = [word for word in words if word.lower() not in ['top', 'most', 'popular', 'best', 'on', 'amazon', '2025', '2024']][:1]
            base_title = f"Top {number} {' '.join(product_words)}"
            # Add excitement hook if we have room (7 words max)
            base_words = base_title.split()
            if len(base_words) <= 5:  # Room for 2-word hook
                return f"{base_title} - Must See!"
            elif len(base_words) <= 6:  # Room for 1-word hook
                return f"{base_title} Amazing!"
            else:
                return base_title
        
        # Look for "Best X" pattern  
        elif 'best' in title.lower():
            product_words = [word for word in words if word.lower() not in ['best', 'most', 'popular', 'on', 'amazon', '2025', '2024']][:2]
            base_title = f"Best {' '.join(product_words)}"
            # Add excitement hook if we have room
            base_words = base_title.split()
            if len(base_words) <= 5:
                return f"{base_title} - Must Have!"
            elif len(base_words) <= 6:
                return f"{base_title} Amazing!"
            else:
                return base_title
        
        # Generic pattern - take first few meaningful words + hook
        else:
            meaningful_words = [word for word in words if word.lower() not in ['most', 'popular', 'on', 'amazon', '2025', '2024']][:3]
            base_title = ' '.join(meaningful_words)
            base_words = base_title.split()
            if len(base_words) <= 5:
                return f"{base_title} - Incredible!"
            elif len(base_words) <= 6:
                return f"{base_title} Wow!"
            else:
                return ' '.join(base_words[:7])
    
    async def _generate_youtube_title(self, title: str, keywords: Dict) -> str:
        """Generate YouTube Shorts optimized title"""
        primary_kw = keywords['primary_keywords'][:2] if keywords['primary_keywords'] else []
        
        prompt = f"""
        Create a YouTube Shorts title (max 60 characters) for: {title}
        
        Include these high-performing keywords: {', '.join(primary_kw)}
        
        Requirements:
        - Under 60 characters
        - Include #shorts
        - Clickable and engaging
        - Include current year (2025)
        - Use numbers and emotional triggers
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a YouTube optimization expert. Create viral, clickable titles."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=100
            )
            
            generated_title = response.choices[0].message.content.strip()
            # Ensure #shorts is included
            if '#shorts' not in generated_title.lower():
                generated_title += ' #shorts'
            
            return generated_title[:60]  # Enforce character limit
            
        except Exception as e:
            return f"Top 5 {title.split()[-1]} 2025 #shorts"
    
    async def _generate_youtube_description(
        self, 
        title: str, 
        category: str, 
        keywords: Dict, 
        products: List[Dict]
    ) -> str:
        """Generate YouTube description with SEO keywords"""
        
        description_prompt = f"""
        Create a YouTube Shorts description for: {title}
        Category: {category}
        
        Include:
        - These SEO keywords naturally: {', '.join(keywords.get('seo_keywords', [])[:5])}
        - Product mentions from real data
        - Amazon affiliate disclaimer
        - Call to action (subscribe, like)
        - Relevant hashtags
        
        Real products to mention:
        {self._format_products_for_description(products)}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Create engaging YouTube descriptions with natural keyword integration."},
                    {"role": "user", "content": description_prompt}
                ],
                temperature=0.6,
                max_tokens=300
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            # Fallback description
            return f"""🔥 Best {title} revealed! Check out these amazing products:

{self._format_products_for_description(products)}

💡 Links in bio - As an Amazon Associate I earn from qualifying purchases.

👍 Like if this helped! Subscribe for more reviews!

#{' #'.join(keywords.get('social_keywords', [])[:5])}"""
    
    async def _generate_instagram_caption(self, title: str, keywords: Dict) -> str:
        """Generate Instagram caption with trending hashtags"""
        
        social_kw = keywords.get('social_keywords', [])[:3]
        
        caption_prompt = f"""
        Create an Instagram caption for: {title}
        
        Include:
        - These trending keywords: {', '.join(social_kw)}
        - Emojis and engagement hooks
        - Call to action
        - Story/swipe prompts
        - Max 2200 characters
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Create viral Instagram captions with natural keyword integration."},
                    {"role": "user", "content": caption_prompt}
                ],
                temperature=0.8,
                max_tokens=300
            )
            
            return response.choices[0].message.content.strip()[:2200]
            
        except Exception as e:
            return f"🔥 {title} revealed! Swipe for details ➡️\n\n✨ Which one is your favorite? Comment below! 👇\n\n🛒 Links in bio"
    
    async def _generate_instagram_hashtags(self, category: str, keywords: Dict) -> str:
        """Generate Instagram hashtags optimized for reach"""
        
        hashtag_prompt = f"""
        Generate 25-30 Instagram hashtags for {category} product reviews.
        
        Mix:
        - 5 high-competition hashtags (1M+ posts)
        - 15 medium-competition hashtags (100K-1M posts) 
        - 10 low-competition hashtags (10K-100K posts)
        
        Include these keywords: {', '.join(keywords.get('social_keywords', []))}
        
        Return as single string with # symbols.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an Instagram hashtag expert. Generate hashtag mixes for maximum reach."},
                    {"role": "user", "content": hashtag_prompt}
                ],
                temperature=0.5,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            # Fallback hashtags
            return f"#amazonfinds #{category.lower()} #review #top5 #shopping #deals #2025 #viral #fyp #explore"
    
    async def _generate_tiktok_caption(self, title: str, keywords: Dict) -> str:
        """Generate TikTok caption with trending elements"""
        
        social_kw = keywords.get('social_keywords', [])[:3]
        
        caption_prompt = f"""
        Create a TikTok caption for: {title}
        
        Include:
        - These trending keywords: {', '.join(social_kw)}
        - Hook questions and engagement
        - Current TikTok trends 
        - Call to action
        - Max 150 characters
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Create viral TikTok captions with trending elements."},
                    {"role": "user", "content": caption_prompt}
                ],
                temperature=0.9,
                max_tokens=100
            )
            
            return response.choices[0].message.content.strip()[:150]
            
        except Exception as e:
            return f"Which one would you choose? 🤔 {title} revealed! 🔥"
    
    async def _generate_tiktok_hashtags(self, category: str, keywords: Dict) -> str:
        """Generate TikTok hashtags for maximum reach"""
        
        hashtag_prompt = f"""
        Generate 15-20 TikTok hashtags for {category} product reviews.
        
        Focus on:
        - Trending TikTok hashtags (#fyp, #viral, #foryoupage)
        - Product review hashtags
        - Category-specific tags
        - These keywords: {', '.join(keywords.get('social_keywords', []))}
        
        Return as single string with # symbols.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a TikTok hashtag expert. Generate hashtags for maximum viral reach."},
                    {"role": "user", "content": hashtag_prompt}
                ],
                temperature=0.5,
                max_tokens=150
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"#fyp #viral #foryoupage #{category.lower()} #amazonfinds #review #musthave #2025"
    
    async def _generate_seo_title(self, title: str, keywords: Dict) -> str:
        """Generate SEO-optimized WordPress title"""
        
        primary_kw = keywords.get('primary_keywords', [])[:2]
        longtail_kw = keywords.get('longtail_keywords', [])[:1]
        
        seo_prompt = f"""
        Create an SEO-optimized blog title for: {title}
        
        Include:
        - These primary keywords: {', '.join(primary_kw)}
        - This long-tail keyword: {', '.join(longtail_kw)}
        - Current year (2025)
        - Numbers and power words
        - Max 60 characters for search engines
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an SEO expert. Create search-optimized titles that rank well."},
                    {"role": "user", "content": seo_prompt}
                ],
                temperature=0.4,
                max_tokens=100
            )
            
            return response.choices[0].message.content.strip()[:60]
            
        except Exception as e:
            return f"Best {title} - Complete 2025 Review Guide"
    
    async def _generate_seo_description(
        self, 
        title: str, 
        category: str, 
        keywords: Dict, 
        products: List[Dict]
    ) -> str:
        """Generate SEO meta description"""
        
        seo_kw = keywords.get('seo_keywords', [])[:5]
        
        description_prompt = f"""
        Create an SEO meta description for: {title}
        Category: {category}
        
        Include:
        - These SEO keywords: {', '.join(seo_kw)}
        - Compelling call to action
        - Current year (2025)
        - Max 160 characters for Google
        
        Real products mentioned:
        {self._format_products_for_description(products)}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Create compelling SEO meta descriptions that drive clicks from search results."},
                    {"role": "user", "content": description_prompt}
                ],
                temperature=0.4,
                max_tokens=100
            )
            
            return response.choices[0].message.content.strip()[:160]
            
        except Exception as e:
            return f"Discover the best {title.lower()} in 2025! Compare top {category.lower()} products, prices, and reviews. Find your perfect match today."
    
    def _extract_keywords_from_text(self, text: str) -> List[str]:
        """Extract meaningful keywords from product titles"""
        # Remove common words and extract meaningful terms
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'can', 'may', 'might', 'must'}
        
        # Clean and split text
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return list(set(keywords))
    
    def _extract_brands(self, text: str) -> List[str]:
        """Extract brand names from product titles"""
        # Common tech brands patterns
        brand_patterns = [
            r'\b[A-Z][a-zA-Z]+\b',  # Capitalized words
            r'\b[A-Z&]{2,}\b'       # All caps brand names
        ]
        
        brands = []
        for pattern in brand_patterns:
            matches = re.findall(pattern, text)
            brands.extend(matches)
        
        return list(set(brands))
    
    def _extract_features(self, text: str) -> List[str]:
        """Extract product features from titles"""
        feature_keywords = []
        
        # Look for feature patterns
        feature_patterns = [
            r'\b\d+[a-zA-Z]*\b',     # Numbers with units (15W, 4K, etc.)
            r'\b[a-zA-Z]*proof\b',   # waterproof, dustproof
            r'\b[a-zA-Z]*less\b',    # wireless, cordless
            r'\b[a-zA-Z]*able\b'     # portable, adjustable
        ]
        
        for pattern in feature_patterns:
            matches = re.findall(pattern, text.lower())
            feature_keywords.extend(matches)
        
        return list(set(feature_keywords))
    
    def _format_products_for_prompt(self, products: List[Dict]) -> str:
        """Format products for AI prompts"""
        if not products:
            return "No specific products available"
        
        formatted = []
        for i, product in enumerate(products[:5], 1):
            formatted.append(f"{i}. {product.get('title', 'Unknown')} - {product.get('rating', 'N/A')} stars - {product.get('reviews', 'N/A')} reviews")
        
        return '\n'.join(formatted)
    
    def _format_products_for_description(self, products: List[Dict]) -> str:
        """Format products for descriptions"""
        if not products:
            return "Amazing products featured in this video!"
        
        formatted = []
        for i, product in enumerate(products[:3], 1):  # Top 3 for descriptions
            title = product.get('title', 'Great Product')[:40]
            formatted.append(f"#{i}: {title}...")
        
        return '\n'.join(formatted)
    
    def _generate_fallback_keywords(self, title: str, category: str, variant_used: str) -> Dict[str, List[str]]:
        """Generate basic keywords when AI fails"""
        base_words = title.lower().split()
        category_words = category.lower().split()
        variant_words = variant_used.lower().split()
        
        return {
            'primary_keywords': base_words[:3] + category_words,
            'longtail_keywords': [f"best {title.lower()}", f"{category.lower()} review", f"top {variant_used.lower()}"],
            'brand_keywords': [],
            'feature_keywords': [],
            'social_keywords': ['viral', 'trending', 'musthave', 'amazonfinds', '2025'],
            'seo_keywords': base_words + category_words + ['review', 'best', 'top', '2025']
        }

# Main function for workflow integration
async def production_generate_platform_content_for_workflow(
    title: str, 
    category: str, 
    config: Dict,
    products: List[Dict] = None,
    variant_used: str = ""
) -> Dict:
    """Enhanced platform content generation with keyword optimization"""
    
    generator = ProductionPlatformContentGenerator(config.get('openai_api_key'))
    return await generator.generate_keyword_optimized_content(title, category, products, variant_used)