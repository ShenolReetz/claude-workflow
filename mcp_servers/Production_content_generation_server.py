#!/usr/bin/env python3
"""
Production Content Generation MCP Server - Using OpenAI GPT-5-mini
==============================================================
Updated to use the latest GPT-5 model for enhanced content generation
"""

import openai
import asyncio
from typing import Dict, List, Optional
import json
import sys
import logging

sys.path.append('/home/claude-workflow')

from src.utils.api_resilience_manager import APIResilienceManager

class ProductionContentGenerationMCPServer:
    def __init__(self, openai_api_key: str):
        self.api_key = openai_api_key
        openai.api_key = openai_api_key
        
        # Use latest GPT-5 models for optimal content generation
        self.model = "gpt-5"  # Top GPT-5 for content generation
        self.fallback_model = "gpt-5-mini"  # GPT-5-mini fallback
        self.nano_model = "gpt-5-nano"  # GPT-5-nano for simple tasks
        
        self.client = openai.OpenAI(api_key=openai_api_key)
        
        # Initialize resilience manager
        config = {'openai_api_key': openai_api_key}
        self.api_manager = APIResilienceManager(config)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("🚀 Content Generation Server initialized with GPT-5-mini")
        
    async def generate_seo_keywords(self, title: str, category: str) -> List[str]:
        """Generate SEO keywords using OpenAI GPT-4"""
        try:
            prompt = f"""Generate 20 highly relevant SEO keywords for a product review video about "{title}" in the {category} category.
            Focus on:
            - High search volume terms
            - Buyer intent keywords
            - Long-tail keywords
            - Product-specific features
            Return as a JSON array of strings."""
            
            response = await self._call_openai(prompt)
            keywords = json.loads(response)
            return keywords[:20]
        except Exception as e:
            print(f"❌ Error generating keywords: {e}")
            # Fallback keywords
            return [title.lower(), category.lower(), "review", "best", "amazon", "2025", "top rated"]
    
    async def optimize_title(self, base_title: str, keywords: List[str]) -> str:
        """Optimize title for social media using OpenAI"""
        try:
            prompt = f"""Optimize this title for maximum engagement on social media: "{base_title}"
            
            Use these keywords where relevant: {', '.join(keywords[:5])}
            
            Requirements:
            - Maximum 60 characters
            - Include power words (Best, Top, Ultimate, etc.)
            - Add current year (2025)
            - Make it catchy and clickable
            - Include emoji if appropriate
            
            Return only the optimized title, nothing else."""
            
            response = await self._call_openai(prompt)
            return response.strip()[:100]
        except Exception as e:
            print(f"❌ Error optimizing title: {e}")
            return f"Top 5 {base_title} - Best Picks 2025"
    
    async def generate_countdown_script(self, title: str, products: List[Dict]) -> Dict:
        """Generate countdown script for video narration"""
        try:
            intro_prompt = f"""Write a 5-second engaging intro for a video about "{title}".
            Make it exciting and hook the viewer immediately.
            Maximum 20 words."""
            
            intro = await self._call_openai(intro_prompt)
            
            product_scripts = {}
            for i, product in enumerate(products[:5], 1):
                rank = 6 - i  # Countdown from 5 to 1
                product_prompt = f"""Write a 7-second product description for:
                Product: {product.get('name', f'Product {rank}')}
                Price: ${product.get('price', 'N/A')}
                Rating: {product.get('rating', 'N/A')}/5
                
                Requirements:
                - Start with "Number {rank}"
                - Highlight key features
                - Mention value proposition
                - Maximum 30 words
                - Make it persuasive"""
                
                script = await self._call_openai(product_prompt)
                product_scripts[f'product{rank}_script'] = script.strip()
            
            outro_prompt = f"""Write a 5-second outro for the video.
            Include a call-to-action to check the description for links.
            Maximum 15 words."""
            
            outro = await self._call_openai(outro_prompt)
            
            return {
                'intro_script': intro.strip(),
                'outro_script': outro.strip(),
                **product_scripts
            }
        except Exception as e:
            print(f"❌ Error generating scripts: {e}")
            return self._get_fallback_scripts(title, products)
    
    async def generate_platform_content(self, title: str, category: str, keywords: List[str]) -> Dict:
        """Generate platform-specific content"""
        try:
            # YouTube content
            youtube_prompt = f"""Create YouTube Shorts content for "{title}":
            1. Title (max 100 chars, include #shorts)
            2. Description (500 chars, include timestamps and affiliate disclaimer)
            Use keywords: {', '.join(keywords[:5])}
            Return as JSON with keys: title, description"""
            
            youtube_response = await self._call_openai(youtube_prompt)
            youtube_content = json.loads(youtube_response)
            
            # Instagram content
            instagram_prompt = f"""Create Instagram Reel content for "{title}":
            1. Caption (max 300 chars)
            2. Include 10 relevant hashtags
            Make it engaging and use emojis.
            Return as JSON with keys: caption, hashtags (as array)"""
            
            instagram_response = await self._call_openai(instagram_prompt)
            instagram_content = json.loads(instagram_response)
            
            # WordPress content
            wordpress_prompt = f"""Create WordPress blog post intro for "{title}" product review:
            1. SEO title (max 60 chars)
            2. Meta description (max 160 chars)
            3. Opening paragraph (max 200 words)
            Return as JSON with keys: title, meta_description, intro"""
            
            wordpress_response = await self._call_openai(wordpress_prompt)
            wordpress_content = json.loads(wordpress_response)
            
            return {
                'youtube_title': youtube_content.get('title', f'{title} #shorts'),
                'youtube_description': youtube_content.get('description', ''),
                'instagram_caption': instagram_content.get('caption', ''),
                'instagram_hashtags': instagram_content.get('hashtags', []),
                'wordpress_title': wordpress_content.get('title', title),
                'wordpress_meta': wordpress_content.get('meta_description', ''),
                'wordpress_intro': wordpress_content.get('intro', '')
            }
        except Exception as e:
            print(f"❌ Error generating platform content: {e}")
            return self._get_fallback_platform_content(title)
    
    async def generate_product_descriptions(self, products: List[Dict]) -> List[Dict]:
        """Generate enhanced product descriptions"""
        enhanced_products = []
        for product in products[:5]:
            try:
                prompt = f"""Create a compelling 50-word product description for:
                Name: {product.get('name', 'Product')}
                Price: ${product.get('price', 'N/A')}
                Rating: {product.get('rating', 'N/A')}/5
                
                Focus on benefits and unique features.
                Make it persuasive and concise."""
                
                description = await self._call_openai(prompt)
                product['enhanced_description'] = description.strip()
                enhanced_products.append(product)
            except Exception as e:
                print(f"❌ Error enhancing product {product.get('name')}: {e}")
                product['enhanced_description'] = product.get('description', '')[:200]
                enhanced_products.append(product)
        
        return enhanced_products
    
    async def _call_openai(self, prompt: str, temperature: float = 0.7) -> str:
        """Make API call to OpenAI with GPT-5 and automatic fallback"""
        try:
            # Try GPT-5 first
            try:
                self.logger.info("Calling GPT-5 for content generation...")
                response = self.client.chat.completions.create(
                    model=self.model,  # GPT-5
                    messages=[
                        {"role": "system", "content": "You are a professional content creator specializing in product reviews and SEO optimization. Use your advanced capabilities to create highly engaging and converting content."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature,
                    max_tokens=500
                )
                self.logger.info("✅ GPT-5 response received successfully")
                return response.choices[0].message.content
                
            except openai.NotFoundError as e:
                # GPT-5 not available, fallback to GPT-4
                self.logger.warning(f"GPT-5 not available, falling back to GPT-4: {e}")
                response = self.client.chat.completions.create(
                    model=self.fallback_model,  # GPT-4-turbo
                    messages=[
                        {"role": "system", "content": "You are a professional content creator specializing in product reviews and SEO optimization."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature,
                    max_tokens=500
                )
                self.logger.info("✅ GPT-4 fallback response received")
                return response.choices[0].message.content
                
        except Exception as e:
            self.logger.error(f"❌ OpenAI API error: {e}")
            # Use resilience manager for additional fallback
            return await self.api_manager._use_openai_fallback(prompt)
    
    def _get_fallback_scripts(self, title: str, products: List[Dict]) -> Dict:
        """Fallback scripts if API fails"""
        scripts = {
            'intro_script': f"Discover the top 5 {title} that everyone's talking about!",
            'outro_script': "Thanks for watching! Check the links below."
        }
        
        for i in range(1, 6):
            rank = 6 - i
            if i <= len(products):
                product = products[i-1]
                scripts[f'product{rank}_script'] = f"Number {rank}: {product.get('name', 'Amazing product')} - Rated {product.get('rating', '4.5')} stars with incredible value!"
            else:
                scripts[f'product{rank}_script'] = f"Number {rank}: Top-rated product with amazing features!"
        
        return scripts
    
    def _get_fallback_platform_content(self, title: str) -> Dict:
        """Fallback platform content if API fails"""
        return {
            'youtube_title': f'Top 5 {title} - Best Picks 2025 #shorts',
            'youtube_description': f'Discover the best {title} on Amazon! Check timestamps below.\n\n⏱️ Timestamps:\n0:00 Intro\n0:05 Products\n0:55 Outro\n\nAs an Amazon Associate I earn from qualifying purchases.',
            'instagram_caption': f'🔥 Top 5 {title} you need to see! Swipe for details ➡️ Link in bio for more! #amazonfinds #musthave',
            'instagram_hashtags': ['amazonfinds', 'review', 'top5', 'musthave', 'viral', 'trending'],
            'wordpress_title': f'Best {title} - Top 5 Picks',
            'wordpress_meta': f'Discover the best {title} with our comprehensive review of the top 5 products.',
            'wordpress_intro': f'Looking for the best {title}? We\'ve researched and tested the top products to bring you our top 5 recommendations.'
        }