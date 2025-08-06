#!/usr/bin/env python3
"""
Production Product Category Extractor MCP Server - Using OpenAI
"""

import openai
import json
from typing import Dict, Optional

class ProductionProductCategoryExtractorMCPServer:
    def __init__(self, openai_api_key: str):
        self.client = openai.OpenAI(api_key=openai_api_key)
        self.model = "gpt-4-turbo-preview"
        
    async def extract_category(self, title: str) -> Dict:
        """Extract product category from title using OpenAI"""
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
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return {
                'category': result.get('category', 'General'),
                'subcategory': result.get('subcategory', ''),
                'keywords': result.get('keywords', [])
            }
        except Exception as e:
            print(f"❌ Error extracting category: {e}")
            return {
                'category': 'General',
                'subcategory': '',
                'keywords': []
            }