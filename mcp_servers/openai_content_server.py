import asyncio
import json
import openai
from typing import Dict, List, Optional

class OpenAIContentGenerationServer:
    def __init__(self, openai_api_key: str):
        openai.api_key = openai_api_key
        
    async def generate_seo_keywords(self, title: str, product_category: str) -> List[str]:
        """Generate SEO keywords using OpenAI"""
        try:
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[{
                    "role": "user", 
                    "content": f"""Generate 20 SEO keywords for: "{title}"
                    Category: {product_category}
                    Focus on YouTube Shorts, TikTok, Amazon search terms.
                    Return comma-separated list only."""
                }],
                max_tokens=500
            )
            
            keywords_text = response.choices[0].message.content
            keywords = [k.strip() for k in keywords_text.split(',')]
            
            print(f"✅ Generated {len(keywords)} SEO keywords")
            return keywords
            
        except Exception as e:
            print(f"Error generating keywords: {e}")
            return []
    
    async def optimize_title(self, original_title: str, keywords: List[str]) -> str:
        """Optimize title using OpenAI"""
        try:
            keywords_str = ', '.join(keywords[:10])
            
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[{
                    "role": "user",
                    "content": f"""Optimize this title for YouTube Shorts:
                    Original: "{original_title}"
                    Keywords: {keywords_str}
                    
                    Requirements: Under 60 characters, clickable, trending.
                    Return only the optimized title."""
                }],
                max_tokens=100
            )
            
            optimized_title = response.choices[0].message.content.strip().strip('"')
            print(f"✅ Optimized title: {optimized_title}")
            return optimized_title
            
        except Exception as e:
            print(f"Error optimizing title: {e}")
            return original_title

# Test function
async def test_openai_content():
    with open('/app/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    server = OpenAIContentGenerationServer(config['openai_api_key'])
    
    title = "Top 5 New Car Mono Amplifiers Releases 2025"
    
    print("🔍 Testing OpenAI keywords...")
    keywords = await server.generate_seo_keywords(title, "Car Audio")
    print(f"Keywords: {keywords[:3]}...")
    
    print("🎯 Testing title optimization...")
    optimized = await server.optimize_title(title, keywords)

if __name__ == "__main__":
    asyncio.run(test_openai_content())
