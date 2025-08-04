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
    
    async def generate_single_product(self, prompt: str) -> str:
        """Generate a single product based on specific requirements"""
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=200,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
        except Exception as e:
            print(f"Error generating single product: {e}")
            return None
    
    async def generate_optimized_product_descriptions(self, products: List[Dict], universal_keywords: List[str], title: str) -> List[Dict]:
        """Generate SEO-optimized product descriptions for ProductNo1-5 fields using universal keywords"""
        try:
            keywords_str = ', '.join(universal_keywords[:10])
            
            # Format products for the prompt
            products_info = ""
            for i, product in enumerate(products[:5], 1):
                products_info += f"Product #{i}: {product.get('title', 'Unknown')} - Price: ${product.get('price', 'N/A')}, Rating: {product.get('rating', 'N/A')}/5\n"
            
            prompt = f"""
            Optimize product titles and descriptions for video content: "{title}"
            Universal Keywords to integrate: {keywords_str}
            
            PRODUCTS TO OPTIMIZE:
            {products_info}
            
            REQUIREMENTS FOR EACH PRODUCT:
            - TITLE: Keep original product name but add 1-2 power words if needed
            - DESCRIPTION: Exactly 18-22 words for perfect TTS timing (8-9 seconds)
            - Include 2-3 universal keywords naturally
            - Highlight unique selling points and key features
            - Mention price/rating if compelling
            - Use action words and benefits-focused language
            - Avoid generic phrases, be specific
            
            OPTIMIZATION GOALS:
            - Video engagement and retention
            - Cross-platform discoverability
            - Clear value proposition
            - Natural keyword integration
            
            Return as JSON array with this structure:
            [
                {{
                    "rank": 5,
                    "optimized_title": "Enhanced product title",
                    "optimized_description": "18-22 word description with keywords",
                    "keywords_used": ["keyword1", "keyword2"],
                    "word_count": 20,
                    "estimated_seconds": 8.5,
                    "selling_points": ["point1", "point2", "point3"]
                }}
            ]
            
            Order products by rank 5 (least exciting) to 1 (most exciting/best value).
            """
            
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response.content[0].text
            
            # Parse JSON response
            try:
                # Extract JSON from response
                start_idx = response_text.find('[')
                end_idx = response_text.rfind(']') + 1
                if start_idx != -1 and end_idx > start_idx:
                    json_str = response_text[start_idx:end_idx]
                    optimized_products = json.loads(json_str)
                    print(f"✅ Generated {len(optimized_products)} optimized product descriptions")
                    return optimized_products
                else:
                    print("❌ Could not extract JSON from response")
                    return []
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing error: {e}")
                return []
                
        except Exception as e:
            print(f"❌ Error generating optimized product descriptions: {e}")
            return []
    
    async def generate_attention_grabbing_intro(self, title: str, keywords: List[str], hook_style: str = "shocking") -> Dict:
        """Generate extremely catchy intro hooks for maximum viewer retention"""
        try:
            keywords_str = ', '.join(keywords[:8])
            
            # Define different hook styles
            hook_styles = {
                "shocking": "Start with shocking statistics, surprising facts, or bold claims",
                "question": "Start with intriguing questions that create curiosity gaps", 
                "countdown": "Start with urgency and countdown energy",
                "story": "Start with a relatable problem or story hook",
                "controversy": "Start with controversial or contrarian takes"
            }
            
            style_instruction = hook_styles.get(hook_style, hook_styles["shocking"])
            
            prompt = f"""
            Create the most attention-grabbing 5-second intro for: "{title}"
            Keywords to naturally include: {keywords_str}
            Hook style: {style_instruction}
            
            PSYCHOLOGICAL TRIGGERS TO USE:
            - Curiosity gap (make them wonder what's coming)
            - Social proof (everyone's talking about this)
            - Urgency/FOMO (limited time, trending now)
            - Benefit preview (what they'll gain)
            - Pattern interrupt (unexpected opening)
            
            INTRO REQUIREMENTS:
            - Exactly 10-15 words (5 seconds max when spoken)
            - Hook viewers in first 3 seconds
            - Create strong reason to watch until end
            - Use power words and emotional triggers
            - Include numbers/rankings if relevant
            - End with momentum toward countdown
            
            EXAMPLES OF GREAT HOOKS:
            - "These 5 products are breaking the internet right now!"
            - "Number 1 will literally save you thousands of dollars!"
            - "I can't believe Amazon is still selling these for this price!"
            - "99% of people don't know about these hidden gems!"
            
            Return as JSON:
            {{
                "intro_text": "The hook text (10-15 words)",
                "hook_type": "shocking/question/countdown/story/controversy",
                "psychological_triggers": ["trigger1", "trigger2"],
                "word_count": 12,
                "estimated_seconds": 4.8,
                "retention_score": 85,
                "alternative_hooks": ["hook2", "hook3"]
            }}
            """
            
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response.content[0].text
            
            # Parse JSON response
            try:
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                if start_idx != -1 and end_idx > start_idx:
                    json_str = response_text[start_idx:end_idx]
                    intro_data = json.loads(json_str)
                    print(f"✅ Generated attention-grabbing intro: {intro_data.get('intro_text', '')}")
                    return intro_data
                else:
                    print("❌ Could not extract JSON from intro response")
                    return {}
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing error for intro: {e}")
                return {}
                
        except Exception as e:
            print(f"❌ Error generating intro hook: {e}")
            return {}
    
    async def generate_platform_upload_metadata(self, title: str, products: List[Dict], platform_keywords: Dict, affiliate_data: List[Dict] = None) -> Dict:
        """Generate platform-specific titles and descriptions for upload metadata only"""
        try:
            # Get top products for context
            top_products = [p.get('optimized_title', p.get('title', '')) for p in products[:3]]
            products_str = ', '.join(top_products)
            
            # Format affiliate links for inclusion
            affiliate_links_text = ""
            if affiliate_data:
                affiliate_links_text = "🛒 AFFILIATE LINKS:\n"
                for i, affiliate in enumerate(affiliate_data[:5], 1):
                    product_name = affiliate.get('title', f'Product #{i}')
                    affiliate_url = affiliate.get('affiliate_link', '')
                    if affiliate_url:
                        affiliate_links_text += f"#{i}: {product_name}\n{affiliate_url}\n\n"
                
                affiliate_links_text += "💡 As an Amazon Associate, I earn from qualifying purchases at no extra cost to you.\n"
            
            results = {}
            
            # YouTube Metadata
            youtube_keywords = ', '.join(platform_keywords.get('youtube', [])[:10])
            youtube_prompt = f"""
            Create YouTube-optimized metadata for: "{title}"
            Featured products: {products_str}
            YouTube keywords: {youtube_keywords}
            
            YOUTUBE REQUIREMENTS:
            - Title: Under 60 characters, clickable, retention-focused
            - Description: 200-300 words with keywords, hashtags, CTA, and affiliate links
            - Include product mentions and affiliate disclosure
            - Use YouTube-specific language and trending terms
            - Add timestamps for each product (0:05 #5, 0:15 #4, etc.)
            - Include affiliate links section
            
            AFFILIATE LINKS TO INCLUDE:
            {affiliate_links_text}
            
            Return as JSON:
            {{
                "title": "YouTube optimized title",
                "description": "Complete YouTube description with hashtags and affiliate links",
                "tags": ["tag1", "tag2", "tag3"],
                "character_count": 58
            }}
            """
            
            # TikTok Metadata  
            tiktok_keywords = ', '.join(platform_keywords.get('tiktok', [])[:8])
            tiktok_prompt = f"""
            Create TikTok-optimized metadata for: "{title}"
            Featured products: {products_str}
            TikTok keywords: {tiktok_keywords}
            
            TIKTOK REQUIREMENTS:
            - Title: Gen Z language, trending slang, under 50 characters
            - Caption: 2-3 sentences with trending hashtags and "Link in bio for Amazon deals!"
            - Use TikTok-specific hashtags and discovery terms
            - Include product mentions and affiliate disclosure
            - Add call-to-action for bio link
            
            AFFILIATE DISCLOSURE:
            Include: "Amazon affiliate links in bio! 🛒 #amazonfinds #tiktokmademebuyit"
            
            Return as JSON:
            {{
                "title": "TikTok optimized title",
                "caption": "TikTok caption with hashtags and bio CTA",
                "hashtags": ["#hashtag1", "#hashtag2"],
                "character_count": 45
            }}
            """
            
            # Instagram Metadata
            instagram_hashtags = ' '.join(platform_keywords.get('instagram', [])[:15])
            instagram_prompt = f"""
            Create Instagram-optimized metadata for: "{title}"
            Featured products: {products_str}
            Instagram hashtags: {instagram_hashtags}
            
            INSTAGRAM REQUIREMENTS:
            - Title: Visual storytelling focus, under 55 characters
            - Caption: Engaging story with call-to-action, hashtags, and "Link in bio!"
            - Mix popular and niche hashtags for reach
            - Include product mentions and affiliate disclosure
            - Add strong call-to-action for bio link
            
            AFFILIATE DISCLOSURE:
            Include: "🛒 Amazon affiliate links in bio! Tap the link for the best deals!"
            
            Return as JSON:
            {{
                "title": "Instagram optimized title",
                "caption": "Instagram caption with storytelling and bio CTA",
                "hashtags": ["#hashtag1", "#hashtag2"],
                "character_count": 52
            }}
            """
            
            # WordPress Metadata
            wordpress_keywords = ', '.join(platform_keywords.get('wordpress', [])[:8])
            
            # Format product images for WordPress
            wordpress_images_html = ""
            if affiliate_data:
                for i, affiliate in enumerate(affiliate_data[:5], 1):
                    product_name = affiliate.get('title', f'Product #{i}')
                    image_url = affiliate.get('image_url', '')
                    affiliate_url = affiliate.get('affiliate_link', '')
                    price = affiliate.get('price', 'N/A')
                    rating = affiliate.get('rating', 'N/A')
                    
                    if image_url and affiliate_url:
                        wordpress_images_html += f'''
                        <div class="product-review">
                            <h3>#{i}: {product_name}</h3>
                            <img src="{image_url}" alt="{product_name}" style="max-width: 300px; height: auto;" />
                            <p><strong>Price:</strong> ${price} | <strong>Rating:</strong> {rating}/5</p>
                            <a href="{affiliate_url}" target="_blank" rel="nofollow" class="affiliate-button">Check Price on Amazon</a>
                        </div>
                        '''
            
            wordpress_prompt = f"""
            Create WordPress SEO-optimized content for: "{title}"
            Featured products: {products_str}
            WordPress keywords: {wordpress_keywords}
            
            WORDPRESS REQUIREMENTS:
            - Title: Long-tail SEO optimized, under 60 characters
            - Meta description: 150-160 characters with keywords
            - Content: 800-1200 word blog post with product reviews
            - Include product images with affiliate links
            - Focus on search intent and organic discovery
            - Include product comparison table
            - Add FAQ section
            
            PRODUCT IMAGES HTML TO INCLUDE:
            {wordpress_images_html}
            
            AFFILIATE DISCLOSURE:
            Include: "This post contains affiliate links. As an Amazon Associate, I earn from qualifying purchases at no extra cost to you."
            
            Return as JSON:
            {{
                "title": "WordPress SEO title",
                "meta_description": "SEO meta description",
                "content": "Full blog post with HTML, images, and affiliate links",
                "focus_keywords": ["keyword1", "keyword2"],
                "character_count": 58
            }}
            """
            
            # Generate all platform metadata in parallel
            platforms = [
                ("youtube", youtube_prompt),
                ("tiktok", tiktok_prompt), 
                ("instagram", instagram_prompt),
                ("wordpress", wordpress_prompt)
            ]
            
            for platform, prompt in platforms:
                try:
                    response = self.client.messages.create(
                        model="claude-3-5-sonnet-20241022",
                        max_tokens=800,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    
                    response_text = response.content[0].text
                    start_idx = response_text.find('{')
                    end_idx = response_text.rfind('}') + 1
                    
                    if start_idx != -1 and end_idx > start_idx:
                        json_str = response_text[start_idx:end_idx]
                        platform_data = json.loads(json_str)
                        results[platform] = platform_data
                        print(f"✅ Generated {platform} metadata: {platform_data.get('title', '')[:40]}...")
                    
                except Exception as e:
                    print(f"❌ Error generating {platform} metadata: {e}")
                    results[platform] = {}
            
            return results
                
        except Exception as e:
            print(f"❌ Error generating platform metadata: {e}")
            return {}

    async def generate_platform_titles_from_keywords(self, original_title: str, platform_keywords: Dict[str, List[str]]) -> Dict[str, str]:
        """Generate platform-specific titles USING platform keywords (SEO-first approach)"""
        try:
            prompt = f"""
            Generate platform-optimized titles using their specific keywords for SEO.
            Original title: "{original_title}"
            
            Platform Keywords:
            - YouTube: {', '.join(platform_keywords.get('youtube', [])[:10])}
            - TikTok: {', '.join(platform_keywords.get('tiktok', [])[:8])}
            - Instagram: {', '.join([h.replace('#', '') for h in platform_keywords.get('instagram', [])[:8]])}
            - WordPress: {', '.join(platform_keywords.get('wordpress', [])[:8])}
            
            CRITICAL: Each title MUST include relevant keywords from its platform for SEO.
            
            YouTube (60 chars max): Include keywords like "2025", "best", "top 5"
            TikTok (100 chars max): Include trending keywords, make it clickable
            Instagram (125 chars max): Include relevant hashtag terms naturally
            WordPress (150 chars max): Include long-tail SEO keywords
            
            Return as JSON:
            {{
                "youtube": "YouTube title with keywords",
                "tiktok": "TikTok title with keywords", 
                "instagram": "Instagram title with keywords",
                "wordpress": "WordPress title with keywords"
            }}
            """
            
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=800,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Safer JSON parsing with regex extraction
            response_text = response.content[0].text
            import re
            
            # Try to extract JSON from response, handling potential extra text
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    result = json.loads(json_match.group())
                    print("✅ Generated platform-specific titles using keywords")
                    return result
                except json.JSONDecodeError:
                    pass
            
            # If JSON parsing fails, try direct parsing
            try:
                result = json.loads(response_text)
                print("✅ Generated platform-specific titles using keywords")
                return result
            except:
                pass
            
            print("⚠️ Could not parse JSON response, using fallback")
            return {
                "youtube": original_title,
                "tiktok": original_title,
                "instagram": original_title,
                "wordpress": original_title
            }
            
        except Exception as e:
            print(f"Error generating platform titles: {e}")
            return {
                "youtube": original_title,
                "tiktok": original_title,
                "instagram": original_title,
                "wordpress": original_title
            }
    
    async def generate_platform_descriptions_from_keywords(self, products: List[Dict], platform_keywords: Dict[str, List[str]], platform_titles: Dict[str, str], affiliate_data: Dict = None, video_url: str = None, product_photos: Dict = None) -> Dict[str, str]:
        """Generate platform-specific descriptions USING platform keywords with affiliate links"""
        try:
            # Get product info with affiliate links for context
            product_info = ""
            affiliate_links_section = ""
            
            for i, product in enumerate(products[:5], 1):
                product_title = product.get('title', f'Product {i}')
                product_price = product.get('price', 0)
                product_rating = product.get('rating', 0)
                
                product_info += f"#{i}: {product_title} - ${product_price} - {product_rating}⭐\n"
                
                # Add affiliate link if available
                if affiliate_data and affiliate_data.get(f'ProductNo{i}AffiliateLink'):
                    affiliate_url = affiliate_data[f'ProductNo{i}AffiliateLink']
                    affiliate_links_section += f"🛒 #{i} {product_title}: {affiliate_url}\n"
            
            # Add affiliate disclosure
            if affiliate_links_section:
                affiliate_links_section += "\n💡 As an Amazon Associate, I earn from qualifying purchases at no extra cost to you.\n"
            
            # Prepare WordPress-specific content with photos and video
            wordpress_photos_section = ""
            if product_photos:
                wordpress_photos_section = "\n### Product Images:\n"
                for i in range(1, 6):
                    if product_photos.get(f'ProductNo{i}Photo'):
                        product_name = products[i-1].get('title', f'Product {i}') if i <= len(products) else f'Product {i}'
                        photo_url = product_photos[f'ProductNo{i}Photo']
                        wordpress_photos_section += f"![{product_name}]({photo_url})\n"
            
            wordpress_video_section = ""
            if video_url:
                wordpress_video_section = f"\n### Watch the Full Review:\n[🎥 Click here to watch our detailed video review]({video_url})\n"
            
            prompt = f"""
            Generate platform-optimized descriptions using their specific keywords and include affiliate links.
            
            Products to feature:
            {product_info}
            
            Platform Titles (for context):
            - YouTube: {platform_titles.get('youtube', '')}
            - TikTok: {platform_titles.get('tiktok', '')}
            - Instagram: {platform_titles.get('instagram', '')}
            - WordPress: {platform_titles.get('wordpress', '')}
            
            Platform Keywords to include:
            - YouTube: {', '.join(platform_keywords.get('youtube', [])[:15])}
            - TikTok: {', '.join(platform_keywords.get('tiktok', [])[:10])}
            - Instagram: {', '.join(platform_keywords.get('instagram', [])[:15])}
            - WordPress: {', '.join(platform_keywords.get('wordpress', [])[:12])}
            
            AFFILIATE LINKS TO INCLUDE:
            {affiliate_links_section}
            
            PLATFORM-SPECIFIC REQUIREMENTS:
            
            YouTube: 
            - 200-300 words with timestamps (0:05 #5, 0:15 #4, etc.)
            - Include keywords naturally
            - Add affiliate links section at the end
            - Include affiliate disclosure
            
            TikTok: 
            - 100-150 words with trending keywords
            - Add relevant hashtags
            - Include "Link in bio for deals!" 
            - Keep affiliate links concise
            
            Instagram: 
            - 150-200 words, engaging tone
            - Integrate hashtags naturally throughout
            - Include "Link in bio for exclusive deals!" 
            - Add affiliate links in a clean format
            
            WordPress: 
            - 300-500 words, SEO-optimized with long-tail keywords
            - Include affiliate links integrated naturally in content
            - Add product photos section: {wordpress_photos_section}
            - Add video section: {wordpress_video_section}
            - Include comprehensive affiliate disclosure
            
            Return as JSON:
            {{
                "youtube": "YouTube description with keywords, timestamps, and affiliate links",
                "tiktok": "TikTok description with keywords, hashtags, and affiliate links",
                "instagram": "Instagram caption with keywords, hashtags, and affiliate links", 
                "wordpress": "WordPress blog post with keywords, affiliate links, photos, and video"
            }}
            """
            
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Safer JSON parsing with regex extraction
            response_text = response.content[0].text
            import re
            
            # Try to extract JSON from response, handling potential extra text
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    # Clean up potential control characters before parsing
                    clean_json = json_match.group().replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
                    result = json.loads(clean_json)
                    print("✅ Generated platform-specific descriptions using keywords")
                    return result
                except json.JSONDecodeError:
                    pass
            
            # If JSON parsing fails, try direct parsing
            try:
                clean_text = response_text.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
                result = json.loads(clean_text)
                print("✅ Generated platform-specific descriptions using keywords")
                return result
            except:
                pass
            
            print("⚠️ Could not parse JSON response, using fallback")
            return {
                "youtube": "Check out these amazing products!",
                "tiktok": "You need to see these!",
                "instagram": "These products are incredible!",
                "wordpress": "Discover the best products in this category."
            }
            
        except Exception as e:
            print(f"Error generating platform descriptions: {e}")
            return {
                "youtube": "Check out these amazing products!",
                "tiktok": "You need to see these!",
                "instagram": "These products are incredible!",
                "wordpress": "Discover the best products in this category."
            }
    
    async def generate_intro_hook_and_outro_cta(self, video_title: str) -> Dict[str, str]:
        """Generate IntroHook (5s) and OutroCallToAction (5s) from VideoTitle"""
        try:
            prompt = f"""
            Transform this video title into engaging video content:
            VideoTitle: "{video_title}"
            
            Generate TWO components with STRICT timing:
            
            1. IntroHook (MAX 5 seconds when spoken):
            - Grab attention immediately
            - Create curiosity/urgency about #1 product
            - Make viewers want to watch until the end
            - Examples: "The #1 product shocked even me!", "Wait until you see #1!"
            
            2. OutroCallToAction (MAX 5 seconds when spoken):
            - Drive immediate action
            - Create urgency
            - Direct to links/engagement
            - Examples: "Grab these deals NOW - links below!", "Which one will you buy?"
            
            CRITICAL: Keep both under 5 seconds of spoken audio!
            
            Return as JSON:
            {{
                "intro_hook": "5-second attention grabber",
                "outro_cta": "5-second call to action"
            }}
            """
            
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Extract JSON from response, handling potential extra text
            response_text = response.content[0].text.strip()
            
            # Try to find JSON block in response
            if '{' in response_text and '}' in response_text:
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                json_text = response_text[start_idx:end_idx]
                result = json.loads(json_text)
            else:
                raise ValueError("No JSON found in response")
            
            print("✅ Generated IntroHook and OutroCallToAction with timing validation")
            return result
            
        except Exception as e:
            print(f"Error generating intro/outro: {e}")
            return {
                "intro_hook": "Check out these amazing products!",
                "outro_cta": "Links below - which one will you choose?"
            }
    
    async def format_products_with_countdown(self, products: List[Dict]) -> List[Dict]:
        """Format products with countdown numbering (#5 to #1)"""
        try:
            formatted_products = []
            
            for i, product in enumerate(products[:5]):
                # Countdown: Product 1 = #5, Product 5 = #1
                countdown_number = 5 - i
                winner_emoji = " 🏆" if countdown_number == 1 else ""
                
                formatted_product = product.copy()
                formatted_product['countdown_title'] = f"#{countdown_number}{winner_emoji} {product.get('title', f'Product {i+1}')}"
                formatted_product['countdown_number'] = countdown_number
                formatted_product['is_winner'] = countdown_number == 1
                
                formatted_products.append(formatted_product)
                print(f"🏆 Formatted: {formatted_product['countdown_title']}")
            
            return formatted_products
            
        except Exception as e:
            print(f"Error formatting countdown products: {e}")
            return products
    
    async def calculate_seo_metrics(self, title: str, description: str, keywords: List[str], platform: str = "youtube") -> Dict[str, float]:
        """Calculate SEO metrics for content optimization"""
        try:
            import re
            from collections import Counter
            
            # Combine title and description for analysis
            full_text = f"{title} {description}".lower()
            word_count = len(full_text.split())
            
            # Calculate keyword density
            keyword_mentions = 0
            for keyword in keywords[:10]:  # Use top 10 keywords
                keyword_mentions += len(re.findall(r'\b' + re.escape(keyword.lower()) + r'\b', full_text))
            
            keyword_density = (keyword_mentions / word_count * 100) if word_count > 0 else 0
            
            # SEO Score calculation (0-100)
            seo_score = 0
            
            # Title optimization (30 points)
            if len(title) >= 40 and len(title) <= 70:  # Optimal title length
                seo_score += 15
            if any(keyword.lower() in title.lower() for keyword in keywords[:5]):  # Keywords in title
                seo_score += 15
            
            # Content optimization (40 points)
            if word_count >= 100:  # Sufficient content length
                seo_score += 10
            if keyword_density >= 1.0 and keyword_density <= 3.0:  # Optimal keyword density
                seo_score += 15
            if keyword_mentions >= 3:  # Multiple keyword mentions
                seo_score += 15
            
            # Platform-specific optimization (30 points)
            platform_score = 0
            if platform == "youtube":
                if "2025" in full_text: platform_score += 10
                if any(word in full_text for word in ["best", "top", "review"]): platform_score += 10
                if len(description) >= 200: platform_score += 10
            elif platform == "tiktok":
                if any(word in full_text for word in ["viral", "trending", "must"]): platform_score += 10
                if "#" in description: platform_score += 10
                if len(description) <= 300: platform_score += 10
            elif platform == "instagram":
                hashtag_count = len(re.findall(r'#\w+', description))
                if hashtag_count >= 5 and hashtag_count <= 30: platform_score += 20
                if len(description) <= 2200: platform_score += 10
            elif platform == "wordpress":
                if len(description) >= 300: platform_score += 10
                if keyword_density >= 0.5: platform_score += 10
                if "http" in description: platform_score += 10  # Contains links
            
            seo_score += platform_score
            
            # Title optimization score (0-100)
            title_score = 0
            if len(title) >= 30 and len(title) <= 70: title_score += 40
            if any(keyword.lower() in title.lower() for keyword in keywords[:3]): title_score += 30
            if any(word in title.lower() for word in ["2025", "best", "top"]): title_score += 20
            if title.count(" ") >= 4 and title.count(" ") <= 12: title_score += 10  # Good word count
            
            # Engagement prediction (0-100)
            engagement_score = 50  # Base score
            
            # Engagement factors
            if any(word in title.lower() for word in ["shocking", "amazing", "incredible", "best", "top"]): 
                engagement_score += 15
            if "!" in title or "?" in title: engagement_score += 10
            if any(word in title.lower() for word in ["you", "your", "need", "must"]): engagement_score += 10
            if len(title.split()) >= 5 and len(title.split()) <= 10: engagement_score += 10
            if keyword_density >= 1.5: engagement_score += 5
            
            # Platform-specific engagement
            if platform == "tiktok" and any(word in full_text.lower() for word in ["viral", "trend", "hack"]):
                engagement_score += 10
            elif platform == "youtube" and "review" in full_text.lower():
                engagement_score += 10
            
            engagement_score = min(engagement_score, 100)  # Cap at 100
            
            return {
                "seo_score": round(min(seo_score, 100), 1),
                "title_optimization_score": round(title_score, 1),
                "keyword_density": round(keyword_density, 2),
                "engagement_prediction": round(engagement_score, 1),
                "word_count": word_count,
                "keyword_mentions": keyword_mentions
            }
            
        except Exception as e:
            print(f"Error calculating SEO metrics: {e}")
            return {
                "seo_score": 50.0,
                "title_optimization_score": 50.0,
                "keyword_density": 1.0,
                "engagement_prediction": 50.0,
                "word_count": 0,
                "keyword_mentions": 0
            }
    
    async def validate_content_timing(self, content_data: Dict[str, str]) -> Dict[str, any]:
        """Validate content meets timing requirements and suggest fixes"""
        try:
            validation_results = {
                "is_valid": True,
                "issues": [],
                "suggestions": [],
                "regeneration_needed": False
            }
            
            # Estimate speaking time (average 150 words per minute, 2.5 words per second)
            def estimate_seconds(text: str) -> float:
                word_count = len(text.split())
                return word_count / 2.5
            
            # Check IntroHook (max 5 seconds)
            if 'intro_hook' in content_data:
                intro_time = estimate_seconds(content_data['intro_hook'])
                if intro_time > 5.0:
                    validation_results["is_valid"] = False
                    validation_results["issues"].append(f"IntroHook: {intro_time:.1f}s (FAILED - max 5s)")
                    validation_results["suggestions"].append("Shorten IntroHook to under 12 words")
                    validation_results["regeneration_needed"] = True
            
            # Check OutroCallToAction (max 8 seconds)
            if 'outro_cta' in content_data:
                outro_time = estimate_seconds(content_data['outro_cta'])
                if outro_time > 8.0:
                    validation_results["is_valid"] = False
                    validation_results["issues"].append(f"OutroCallToAction: {outro_time:.1f}s (FAILED - max 8s)")
                    validation_results["suggestions"].append("Shorten OutroCallToAction to under 16 words")
                    validation_results["regeneration_needed"] = True
            
            # Check Product Descriptions (max 9 seconds each)
            for i in range(1, 6):
                product_key = f'ProductNo{i}Description'
                if product_key in content_data:
                    product_time = estimate_seconds(content_data[product_key])
                    if product_time > 9.0:
                        validation_results["is_valid"] = False
                        validation_results["issues"].append(f"Product{i}Description: {product_time:.1f}s (FAILED - max 9s)")
                        validation_results["suggestions"].append(f"Shorten Product {i} description to under 22 words")
                        validation_results["regeneration_needed"] = True
            
            # Calculate total video time
            total_time = 0
            if 'intro_hook' in content_data:
                total_time += estimate_seconds(content_data['intro_hook'])
            if 'outro_cta' in content_data:
                total_time += estimate_seconds(content_data['outro_cta'])
            
            product_times = []
            for i in range(1, 6):
                product_key = f'ProductNo{i}Description'
                if product_key in content_data:
                    product_time = estimate_seconds(content_data[product_key])
                    product_times.append(product_time)
                    total_time += product_time
            
            # Check total video time (must be under 60 seconds)
            if total_time > 60.0:
                validation_results["is_valid"] = False
                validation_results["issues"].append(f"Total video: {total_time:.1f}s (FAILED - max 60s)")
                validation_results["suggestions"].append("Reduce overall content length by 10-15 words")
                validation_results["regeneration_needed"] = True
            
            validation_results["timing_breakdown"] = {
                "intro_hook": estimate_seconds(content_data.get('intro_hook', '')) if 'intro_hook' in content_data else 0,
                "outro_cta": estimate_seconds(content_data.get('outro_cta', '')) if 'outro_cta' in content_data else 0,
                "products": product_times,
                "total_time": total_time
            }
            
            return validation_results
            
        except Exception as e:
            print(f"Error validating content timing: {e}")
            return {
                "is_valid": False,
                "issues": [f"Validation error: {str(e)}"],
                "suggestions": ["Re-run validation"],
                "regeneration_needed": True
            }

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
