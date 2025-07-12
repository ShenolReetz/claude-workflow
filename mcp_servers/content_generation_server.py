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
            Category context: {title}
            
            PRODUCT EXAMPLES BY CATEGORY:
            - Marine Stereos: Fusion MS-RA70, JBL PRV-175, Kenwood KMR-M328BT
            - Satellite TV: DISH Wally HD, Winegard SK-SWM3, KING VQ4500
            - Computer Vacuums: XPOWER A-2, Metro Vacuum DataVac, OPOLAR Cordless
            - Security Cameras: Wyze Cam v3, Blink Mini, Ring Indoor Cam
            - Keyboards: Logitech MX Keys, Corsair K95 RGB, Razer BlackWidow
            
            STRICT REQUIREMENTS:
            - TOTAL VIDEO: Under 60 seconds
            - INTRO: Maximum 5 seconds, extremely attention-grabbing
            - PRODUCTS: Exactly 5 products, countdown from #5 to #1
            - EACH PRODUCT: Maximum 9 seconds each
            - IMPORTANT: Use ONLY REAL products that ACTUALLY exist on Amazon!
              Examples: "Logitech MX Keys", "Sony WH-1000XM5", "Apple AirPods Pro"
              NEVER invent fake products like "Neptune Command Center" or "TelepathX"!
              Use actual brand names and model numbers!
            - OUTRO: Maximum 5 seconds, call-to-action for links in comments
            - FORMAT: 9:16 vertical video
            - STYLE: Fast-paced, energetic, hook viewer immediately
            
            Return ONLY valid JSON with this exact structure:
            {{
                "intro": "5-second intro script",
                "products": [
                    {{
                        "rank": 5,
                        "name": "REAL product name (e.g. Sony WH-1000XM5)",
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
    
    async def generate_seo_keywords_with_products(self, title: str, product_names: List[str]) -> List[str]:
        """Generate SEO keywords using actual product data"""
        try:
            products_str = ', '.join(product_names[:5])
            
            prompt = f"""
            Generate 20 high-impact SEO keywords for this video title: "{title}"
            Actual products featured: {products_str}
            
            Focus on:
            - YouTube Shorts optimization
            - TikTok trending keywords  
            - Amazon product search terms
            - Product-specific keywords
            - 2025 trending tech keywords
            
            Return as a simple comma-separated list.
            """
            
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            keywords_text = response.content[0].text
            keywords = [k.strip() for k in keywords_text.split(',')]
            
            print(f"✅ Generated {len(keywords)} SEO keywords with product data")
            return keywords
            
        except Exception as e:
            print(f"Error generating keywords with products: {e}")
            return []
    
    async def generate_countdown_script_with_products(self, title: str, keywords: List[str], products: List[Dict]) -> Dict:
        """Generate countdown script using actual Amazon product data"""
        try:
            keywords_str = ', '.join(keywords[:15])
            
            # Format products for the prompt
            products_info = ""
            for i, product in enumerate(products[:5], 1):
                products_info += f"#{i}: {product['title']} - Rating: {product['rating']}, Reviews: {product['review_count']}, Price: ${product['price']}\n"
            
            prompt = f"""
            Create a YouTube Shorts script for: "{title}"
            Keywords to include: {keywords_str}
            
            ACTUAL PRODUCTS TO FEATURE:
            {products_info}
            
            STRICT REQUIREMENTS:
            - TOTAL VIDEO: Under 60 seconds
            - INTRO: Maximum 5 seconds, extremely attention-grabbing
            - PRODUCTS: Exactly 5 products, countdown from #5 to #1
            - EACH PRODUCT: Maximum 9 seconds each
            - OUTRO: Maximum 5 seconds with clear CTA
            - USE ACTUAL PRODUCT NAMES AND DETAILS PROVIDED
            
            FORMAT - Return as JSON:
            {{
                "intro": "Text for intro (5 seconds max)",
                "products": [
                    {{
                        "rank": 5,
                        "name": "Actual product name",
                        "script": "Product description script (9 seconds max)",
                        "price": "Product price",
                        "rating": "Product rating"
                    }},
                    // ... continue for products 4, 3, 2, 1
                ],
                "outro": "Text for outro (5 seconds max)"
            }}
            
            SCRIPT WRITING STYLE:
            - Energetic, fast-paced for Shorts
            - Use numbers and rankings prominently
            - Mention key product features quickly
            - Build excitement toward #1 product
            - Include price/rating mentions naturally
            """
            
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            script_text = response.content[0].text
            
            # Try to parse JSON response
            try:
                script_data = json.loads(script_text)
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                print("⚠️ Could not parse JSON, creating fallback structure")
                script_data = {
                    "intro": "Here are the top 5 products you need to see!",
                    "products": [],
                    "outro": "Which product will you choose? Check the links below!"
                }
                
                for i, product in enumerate(products[:5]):
                    script_data["products"].append({
                        "rank": 5-i,
                        "name": product['title'][:50],
                        "script": f"Coming in at #{5-i}, the {product['title'][:30]} with {product['rating']} stars!",
                        "price": product['price'],
                        "rating": product['rating']
                    })
            
            print(f"✅ Generated countdown script with {len(script_data.get('products', []))} products")
            return script_data
            
        except Exception as e:
            print(f"Error generating countdown script with products: {e}")
            return {}
    
    async def generate_multi_platform_keywords(self, title: str, products: List[Dict]) -> Dict[str, List[str]]:
        """Generate platform-specific keywords for all social media platforms"""
        try:
            # Get product names for context
            product_names = [p.get('title', '')[:30] for p in products[:5] if p.get('title')]
            products_str = ', '.join(product_names)
            
            prompt = f"""
            Generate comprehensive keywords for this video across multiple platforms:
            Title: "{title}"
            Featured Products: {products_str}
            
            Create platform-specific keywords following these EXACT requirements:
            
            1. YOUTUBE KEYWORDS (20 keywords):
            - YouTube search optimization
            - Include "2025", "best", "top 5", "review"
            - Product-specific terms
            - Buyer intent keywords
            - Format: comma-separated list
            
            2. INSTAGRAM HASHTAGS (30 hashtags):
            - Mix of popular and niche hashtags
            - Include trending tech hashtags
            - Product category hashtags
            - Engagement hashtags (#techfinds #gadgetlover)
            - Format: space-separated with # symbol
            - Mix high-volume (1M+) and medium-volume (10K-1M) hashtags
            
            3. TIKTOK KEYWORDS (15 keywords):
            - TikTok discovery algorithm keywords
            - Trending sounds/challenges related to tech
            - Gen Z search terms
            - Short, punchy keywords
            - Include "POV", "finds", "haul", "musthave"
            - Format: comma-separated list
            
            4. WORDPRESS SEO (15 long-tail keywords):
            - Long-tail keywords for blog SEO
            - Question-based keywords
            - Comparison keywords
            - Buyer intent phrases
            - Location-neutral terms
            - Format: comma-separated list
            
            5. UNIVERSAL KEYWORDS (10 core keywords):
            - Keywords that work on ALL platforms
            - Brand-neutral terms
            - Core product categories
            - Essential search terms
            - Format: comma-separated list
            
            Return as JSON with this EXACT structure:
            {{
                "youtube": ["keyword1", "keyword2", ...],
                "instagram": ["#hashtag1", "#hashtag2", ...],
                "tiktok": ["keyword1", "keyword2", ...],
                "wordpress": ["long tail keyword 1", "long tail keyword 2", ...],
                "universal": ["keyword1", "keyword2", ...]
            }}
            """
            
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response.content[0].text
            
            # Parse JSON response
            try:
                keywords_data = json.loads(response_text)
                
                # Validate and format the response
                result = {
                    'youtube': keywords_data.get('youtube', [])[:20],
                    'instagram': keywords_data.get('instagram', [])[:30],
                    'tiktok': keywords_data.get('tiktok', [])[:15],
                    'wordpress': keywords_data.get('wordpress', [])[:15],
                    'universal': keywords_data.get('universal', [])[:10]
                }
                
                print(f"✅ Generated multi-platform keywords:")
                print(f"   YouTube: {len(result['youtube'])} keywords")
                print(f"   Instagram: {len(result['instagram'])} hashtags")
                print(f"   TikTok: {len(result['tiktok'])} keywords")
                print(f"   WordPress: {len(result['wordpress'])} keywords")
                print(f"   Universal: {len(result['universal'])} keywords")
                
                return result
                
            except json.JSONDecodeError:
                print("⚠️ Could not parse JSON response, extracting keywords manually")
                # Fallback parsing logic
                return self._parse_keywords_fallback(response_text)
                
        except Exception as e:
            print(f"❌ Error generating multi-platform keywords: {e}")
            return {
                'youtube': [],
                'instagram': [],
                'tiktok': [],
                'wordpress': [],
                'universal': []
            }
    
    def _parse_keywords_fallback(self, text: str) -> Dict[str, List[str]]:
        """Fallback parser for keywords if JSON parsing fails"""
        result = {
            'youtube': [],
            'instagram': [],
            'tiktok': [],
            'wordpress': [],
            'universal': []
        }
        
        # Simple text parsing logic
        lines = text.split('\n')
        current_platform = None
        
        for line in lines:
            line_lower = line.lower()
            if 'youtube' in line_lower:
                current_platform = 'youtube'
            elif 'instagram' in line_lower:
                current_platform = 'instagram'
            elif 'tiktok' in line_lower:
                current_platform = 'tiktok'
            elif 'wordpress' in line_lower:
                current_platform = 'wordpress'
            elif 'universal' in line_lower:
                current_platform = 'universal'
            elif current_platform and ',' in line:
                # Parse comma-separated keywords
                keywords = [k.strip() for k in line.split(',') if k.strip()]
                result[current_platform].extend(keywords)
        
        return result

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
