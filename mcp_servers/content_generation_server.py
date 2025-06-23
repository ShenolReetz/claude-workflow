import asyncio
import json
from anthropic import Anthropic
from typing import Dict, List, Optional

class ContentGenerationMCPServer:
    def __init__(self, anthropic_api_key: str):
        self.client = Anthropic(api_key=anthropic_api_key)
        
    async def generate_seo_keywords(self, title: str, product_category: str) -> List[str]:
        """Generate SEO keywords for YouTube/TikTok optimization"""
        try:
            prompt = f"""
            Generate 20 high-impact SEO keywords for this video title: "{title}"
            Product category: {product_category}
            
            Focus on:
            - YouTube Shorts optimization
            - TikTok trending keywords  
            - Amazon product search terms
            - 2025 trending tech keywords
            
            Return as a simple comma-separated list.
            """
            
            # Remove await - Anthropic client is sync
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            keywords_text = response.content[0].text
            keywords = [k.strip() for k in keywords_text.split(',')]
            
            print(f"✅ Generated {len(keywords)} SEO keywords")
            return keywords
            
        except Exception as e:
            print(f"Error generating keywords: {e}")
            return []
    
    async def optimize_title(self, original_title: str, keywords: List[str]) -> str:
        """Optimize title for social media engagement"""
        try:
            keywords_str = ', '.join(keywords[:10])  # Use top 10 keywords
            
            prompt = f"""
            Optimize this video title for maximum engagement on YouTube Shorts, TikTok, and Instagram:
            
            Original title: "{original_title}"
            Key SEO terms: {keywords_str}
            
            Requirements:
            - Under 60 characters for YouTube Shorts
            - Attention-grabbing and clickable
            - Include trending keywords naturally
            - Add urgency/FOMO elements
            - Perfect for 9:16 vertical video format
            
            Return only the optimized title, nothing else.
            """
            
            # Remove await - Anthropic client is sync
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            
            optimized_title = response.content[0].text.strip().strip('"')
            print(f"✅ Optimized title: {optimized_title}")
            return optimized_title
            
        except Exception as e:
            print(f"Error optimizing title: {e}")
            return original_title
    
    async def generate_countdown_script(self, title: str, keywords: List[str]) -> Dict:
        """Generate 5-product countdown script under 1 minute"""
        try:
            keywords_str = ', '.join(keywords[:15])
            
            prompt = f"""
            Create a YouTube Shorts script for: "{title}"
            Keywords to include: {keywords_str}
            
            STRICT REQUIREMENTS:
            - TOTAL VIDEO: Under 60 seconds
            - INTRO: Maximum 5 seconds, extremely attention-grabbing
            - PRODUCTS: Exactly 5 products, countdown from #5 to #1
            - EACH PRODUCT: Maximum 9 seconds each
            - OUTRO: Maximum 5 seconds, call-to-action for links in comments
            - FORMAT: 9:16 vertical video
            - STYLE: Fast-paced, energetic, hook viewer immediately
            
            Return ONLY valid JSON with this exact structure:
            {{
                "intro": "5-second intro script",
                "products": [
                    {{
                        "rank": 5,
                        "name": "Product name",
                        "script": "9-second product description",
                        "key_features": ["feature1", "feature2", "feature3"]
                    }}
                ],
                "outro": "5-second outro with CTA",
                "total_duration": "estimated seconds",
                "hook_phrases": ["attention-grabbing phrases used"]
            }}
            """
            
            # Remove await - Anthropic client is sync
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            script_text = response.content[0].text
            # Extract JSON from response
            start_idx = script_text.find('{')
            end_idx = script_text.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = script_text[start_idx:end_idx]
                script_data = json.loads(json_str)
                print(f"✅ Generated countdown script with {len(script_data.get('products', []))} products")
                return script_data
            else:
                print("❌ Could not extract JSON from response")
                return {}
            
        except Exception as e:
            print(f"Error generating script: {e}")
            return {}
    
    async def generate_blog_post(self, title: str, script_data: Dict, keywords: List[str]) -> str:
        """Generate SEO blog post for website"""
        try:
            products_info = ""
            if 'products' in script_data:
                for product in script_data['products']:
                    products_info += f"#{product.get('rank', 'N/A')}: {product.get('name', 'N/A')} - {product.get('script', 'N/A')}\n"
            
            keywords_str = ', '.join(keywords)
            
            prompt = f"""
            Write a comprehensive blog post for this video content:
            
            Title: {title}
            Products covered: {products_info}
            SEO Keywords: {keywords_str}
            
            Requirements:
            - 800-1200 words
            - SEO optimized with keywords naturally integrated
            - Include product affiliate sections
            - Add FAQ section
            - Mobile-friendly formatting
            - Include call-to-action for video
            - Professional but engaging tone
            
            Structure:
            1. Engaging introduction with hook
            2. Detailed product reviews (based on script)
            3. Comparison table placeholder
            4. FAQ section
            5. Conclusion with video CTA
            """
            
            # Remove await - Anthropic client is sync
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=3000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            blog_post = response.content[0].text
            print(f"✅ Generated blog post ({len(blog_post)} characters)")
            return blog_post
            
        except Exception as e:
            print(f"Error generating blog post: {e}")
            return ""

# Test the server
async def test_content_generation():
    # Load config
    with open('/app/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    # Initialize server
    server = ContentGenerationMCPServer(
        anthropic_api_key=config['anthropic_api_key']
    )
    
    # Test with sample data
    title = "Top 5 New Car Mono Amplifiers Releases 2025"
    category = "Car Audio Equipment"
    
    print("🔍 Generating SEO keywords...")
    keywords = await server.generate_seo_keywords(title, category)
    print(f"Keywords: {keywords[:5]}...")  # Show first 5
    
    print("\n🎯 Optimizing title...")
    optimized_title = await server.optimize_title(title, keywords)
    
    print("\n📝 Generating countdown script...")
    script = await server.generate_countdown_script(optimized_title, keywords)
    if script:
        print(f"Script intro: {script.get('intro', 'N/A')[:50]}...")

if __name__ == "__main__":
    asyncio.run(test_content_generation())
