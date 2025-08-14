#!/usr/bin/env python3
"""
Production Product Category Extractor MCP Server - Using OpenAI
"""

import openai
import json
import sys
from typing import Dict, Optional

# Add path for imports
sys.path.append('/home/claude-workflow')

class ProductionProductCategoryExtractorMCPServer:
    def __init__(self, openai_api_key: str):
        self.client = openai.OpenAI(api_key=openai_api_key)
        self.model = "gpt-4o"  # Use gpt-4o for category extraction, fallback to gpt-4o-mini
        
    async def extract_category(self, title: str) -> Dict:
        """Extract product category from title using OpenAI with caching"""
        # Try to get from cache first
        try:
            from src.utils.cache_manager import get_cache_manager, CacheManager
            cache = await get_cache_manager()
            cache_key = f"category:{title}"
            cached_result = await cache.get(CacheManager.CATEGORY_PRODUCTS, cache_key)
            if cached_result:
                print(f"✅ Category cache hit for: {title[:30]}...")
                return cached_result
        except Exception as e:
            print(f"Cache check failed (continuing without cache): {e}")
        
        try:
            prompt = f"""Analyze this product title and determine its category: "{title}"
            
            Return ONLY a valid JSON object with:
            - category: Main product category (e.g., Electronics, Home & Kitchen, Beauty, etc.)
            - subcategory: Specific subcategory
            - keywords: 5 relevant category keywords
            
            Example response:
            {{"category": "Electronics", "subcategory": "Cameras", "keywords": ["camera", "photography", "video", "action", "recording"]}}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at categorizing products. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            extracted = {
                'category': result.get('category', 'General'),
                'subcategory': result.get('subcategory', ''),
                'keywords': result.get('keywords', [])
            }
            
            # Cache the result for future use
            try:
                from src.utils.cache_manager import get_cache_manager, CacheManager
                cache = await get_cache_manager()
                await cache.set(
                    CacheManager.CATEGORY_PRODUCTS, 
                    f"category:{title}", 
                    extracted, 
                    CacheManager.TTL_DAY  # Cache for 24 hours
                )
                print(f"✅ Cached category for: {title[:30]}...")
            except:
                pass  # Continue even if caching fails
            
            return extracted
        except Exception as e:
            print(f"❌ Error extracting category: {e}")
            return {
                'category': 'General',
                'subcategory': '',
                'keywords': []
            }