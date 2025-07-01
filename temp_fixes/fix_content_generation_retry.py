#!/usr/bin/env python3
"""
Fix the content generation server with proper retry logic
"""

# Read the content generation server
with open('mcp_servers/content_generation_server.py', 'r') as f:
    content = f.read()

# Create the properly structured file with retry logic
fixed_content = '''import json
import asyncio
import time
from typing import Dict, List, Optional
from anthropic import AsyncAnthropic
import logging
from functools import wraps

logger = logging.getLogger(__name__)

def retry_on_overload(max_retries=3, base_delay=5):
    """Decorator to retry on Anthropic overload errors"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if "529" in str(e) or "overloaded" in str(e).lower():
                        if attempt < max_retries - 1:
                            delay = base_delay * (2 ** attempt)  # Exponential backoff
                            logger.warning(f"Anthropic API overloaded, retrying in {delay} seconds... (attempt {attempt + 1}/{max_retries})")
                            await asyncio.sleep(delay)
                        else:
                            logger.error(f"Max retries reached for Anthropic API")
                            raise
                    else:
                        raise
            return None
        return wrapper
    return decorator

class ContentGenerationMCPServer:
    def __init__(self, api_key: str):
        self.client = AsyncAnthropic(api_key=api_key)
        
    @retry_on_overload(max_retries=3, base_delay=5)
    async def generate_seo_keywords(self, title: str) -> List[str]:
        """Generate SEO keywords for a given title"""
        try:
            prompt = f"""Generate 20 SEO keywords for this YouTube video title: "{title}"
            
            Return ONLY a comma-separated list of keywords, nothing else.
            Focus on terms people would search for on YouTube."""
            
            response = await self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=300,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            
            keywords = response.content[0].text.strip().split(',')
            keywords = [k.strip() for k in keywords if k.strip()]
            
            return keywords[:20]  # Ensure we return exactly 20
            
        except Exception as e:
            logger.error(f"Error generating keywords: {e}")
            raise
    
    @retry_on_overload(max_retries=3, base_delay=5)
    async def generate_social_media_title(self, title: str) -> str:
        """Generate an optimized social media title"""
        try:
            prompt = f"""Optimize this title for social media engagement: "{title}"
            
            Make it:
            - Attention-grabbing with emojis
            - Under 60 characters
            - Include power words (BEST, INSANE, AMAZING, etc.)
            - Add relevant emojis at start and end
            
            Return ONLY the optimized title, nothing else."""
            
            response = await self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=100,
                temperature=0.8,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            logger.error(f"Error generating social media title: {e}")
            raise
    
    @retry_on_overload(max_retries=3, base_delay=5)
    async def generate_countdown_script(self, title: str) -> Dict:
        """Generate a countdown script for top 5 products"""
        try:
            prompt = f"""Create a YouTube-style countdown script for: "{title}"
            
            Generate EXACTLY 5 products in countdown order (5 to 1).
            
            For each product provide:
            1. Product name (specific model/brand)
            2. Description (2-3 sentences highlighting key features)
            
            Format as JSON:
            {{
                "products": [
                    {{
                        "number": 5,
                        "title": "Product Name",
                        "description": "Description here"
                    }},
                    ... continue for all 5 products
                ]
            }}
            
            Make it engaging and informative. Return ONLY valid JSON."""
            
            response = await self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1500,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse JSON response
            text = response.content[0].text.strip()
            # Try to extract JSON if wrapped in other text
            import re
            json_match = re.search(r'\\{.*\\}', text, re.DOTALL)
            if json_match:
                text = json_match.group()
                
            result = json.loads(text)
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON response: {e}")
            logger.error(f"Response text: {text}")
            raise
        except Exception as e:
            logger.error(f"Error generating script: {e}")
            raise
    
    @retry_on_overload(max_retries=3, base_delay=5)
    async def generate_blog_post(self, title: str, products: List[Dict]) -> str:
        """Generate a blog post about the products"""
        try:
            product_list = "\\n".join([f"{p['number']}. {p['title']}: {p['description']}" for p in products])
            
            prompt = f"""Write a comprehensive blog post about: "{title}"
            
            Products to cover:
            {product_list}
            
            Include:
            - Introduction (why these products matter)
            - Detailed review of each product
            - Comparison points
            - Conclusion with recommendations
            
            Make it informative, engaging, and SEO-friendly.
            Write in a conversational tone. About 800-1000 words."""
            
            response = await self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            logger.error(f"Error generating blog post: {e}")
            raise

    async def close(self):
        """Clean up resources"""
        await self.client.close()
'''

# Write the fixed content
with open('mcp_servers/content_generation_server.py', 'w') as f:
    f.write(fixed_content)

print("✅ Fixed content generation server with proper retry logic")
print("✅ Retry decorator is now properly defined before the class")
print("✅ All methods have retry logic for 529 errors")
