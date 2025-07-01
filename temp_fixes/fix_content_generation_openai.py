#!/usr/bin/env python3
"""
Replace Anthropic with OpenAI for content generation
"""

# Create a new content generation server using OpenAI
new_content = '''import json
import asyncio
import time
from typing import Dict, List, Optional
from openai import AsyncOpenAI
import logging
from functools import wraps

logger = logging.getLogger(__name__)

def retry_on_overload(max_retries=3, base_delay=5):
    """Decorator to retry on API overload errors"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if "429" in str(e) or "overloaded" in str(e).lower() or "rate" in str(e).lower():
                        if attempt < max_retries - 1:
                            delay = base_delay * (2 ** attempt)  # Exponential backoff
                            logger.warning(f"API overloaded, retrying in {delay} seconds... (attempt {attempt + 1}/{max_retries})")
                            await asyncio.sleep(delay)
                        else:
                            logger.error(f"Max retries reached for API")
                            raise
                    else:
                        raise
            return None
        return wrapper
    return decorator

class ContentGenerationMCPServer:
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
        
    @retry_on_overload(max_retries=3, base_delay=5)
    async def generate_seo_keywords(self, title: str) -> List[str]:
        """Generate SEO keywords for a given title"""
        try:
            prompt = f"""Generate 20 SEO keywords for this YouTube video title: "{title}"
            
            Return ONLY a comma-separated list of keywords, nothing else.
            Focus on terms people would search for on YouTube."""
            
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=300
            )
            
            keywords = response.choices[0].message.content.strip().split(',')
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
            
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=100
            )
            
            return response.choices[0].message.content.strip()
            
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
            
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1500,
                response_format={"type": "json_object"}
            )
            
            # Parse JSON response
            text = response.choices[0].message.content.strip()
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
            
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating blog post: {e}")
            raise

    async def close(self):
        """Clean up resources"""
        await self.client.close()
'''

# Write the new content
with open('mcp_servers/content_generation_server.py', 'w') as f:
    f.write(new_content)

print("✅ Replaced Anthropic with OpenAI for content generation")
print("✅ Using GPT-3.5-turbo model (cost-effective)")
print("✅ All content generation methods updated:")
print("   - generate_seo_keywords")
print("   - generate_social_media_title")
print("   - generate_countdown_script")
print("   - generate_blog_post")
print("✅ Added JSON response format for countdown script")
