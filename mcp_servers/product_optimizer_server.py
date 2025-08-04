#!/usr/bin/env python3
"""
Product Title & Description Optimizer MCP Server
Optimizes Amazon product titles and generates 9-second countdown descriptions
"""

import asyncio
import logging
from typing import Dict, List, Optional
from anthropic import Anthropic

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductOptimizerServer:
    """Optimizes product titles and generates countdown descriptions"""
    
    def __init__(self, anthropic_api_key: str):
        self.client = Anthropic(api_key=anthropic_api_key)
        
    async def optimize_product_title(self, original_title: str) -> str:
        """
        Optimize product title to core brand + model only
        Example: "Pioneer TS-WX1210A Kick Panel Speaker Enclosures for Car Audio Upgrade" 
        → "Pioneer TS-WX1210A"
        """
        
        try:
            prompt = f"""
            Extract only the core product name from this Amazon product title.
            Remove ALL descriptive text, categories, specifications, and "for X" phrases.
            Keep ONLY: Brand + Model Number/Name (maximum 3-4 words)
            
            Original title: "{original_title}"
            
            Examples:
            "Pioneer TS-WX1210A Kick Panel Speaker Enclosures for Car Audio Upgrade" → "Pioneer TS-WX1210A"
            "Sony WH-1000XM5 Wireless Noise Canceling Headphones" → "Sony WH-1000XM5"
            "Logitech MX Keys Advanced Wireless Illuminated Keyboard" → "Logitech MX Keys"
            "Apple AirPods Pro (2nd Generation) with MagSafe Case" → "Apple AirPods Pro"
            "ThermalFlow Pro X3000 Universal Laptop Cooling Pad with RGB" → "ThermalFlow Pro X3000"
            "AICHESON Laptop Cooling Pad 5 Fans Up to 17.3 Inch" → "AICHESON S035"
            
            Return ONLY the short product name (Brand + Model), nothing else.
            """
            
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=100,
                messages=[{"role": "user", "content": prompt}]
            )
            
            optimized_title = response.content[0].text.strip().strip('"')
            logger.info(f"📝 Title optimized: '{original_title[:30]}...' → '{optimized_title}'")
            
            return optimized_title
            
        except Exception as e:
            logger.error(f"Error optimizing title: {e}")
            return original_title
    
    async def generate_countdown_description(self, 
                                           product_name: str, 
                                           product_rank: int, 
                                           product_details: Dict,
                                           category: str) -> str:
        """
        Generate exactly 9-second countdown description (18-20 words maximum)
        Format: "At number X is ProductName! [key feature]"
        """
        
        try:
            rating = product_details.get('rating', '4.5')
            price = product_details.get('price', 'N/A')
            reviews = product_details.get('review_count', 'many')
            
            prompt = f"""
            Create a 9-second countdown product description (18-20 words MAXIMUM).
            
            Product: {product_name}
            Rank: #{product_rank} (countdown position)
            Category: {category}
            Rating: {rating} stars
            Price: ${price}
            Reviews: {reviews}
            
            STRICT REQUIREMENTS:
            - EXACTLY 18-20 words (no more!)
            - Must fit in exactly 9 seconds of speech
            - Start with countdown position: "At number {product_rank}" OR "Number {product_rank}"
            - Include product name
            - Add ONE key selling point (rating, price, or feature)
            - Energetic countdown style
            - No bullet points or lists
            
            Examples (18-20 words each):
            "At number 5 is the Sony WH-1000XM5! Industry-leading noise cancellation with 30-hour battery life!"
            "Number 4: Apple AirPods Pro with spatial audio! Premium sound quality trusted by millions worldwide!"
            "At number 3: Logitech MX Keys! Professional wireless keyboard with perfect-stroke keys and smart illumination!"
            
            Return ONLY the description, nothing else.
            """
            
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=150,
                messages=[{"role": "user", "content": prompt}]
            )
            
            description = response.content[0].text.strip().strip('"')
            
            # Validate word count (should be 18-20 words for 9 seconds)
            word_count = len(description.split())
            if word_count > 22:
                logger.warning(f"⚠️ Description too long: {word_count} words (max 22)")
                # Truncate if too long
                words = description.split()[:20]
                description = ' '.join(words) + "!"
                
            logger.info(f"📝 Generated {word_count}-word description for #{product_rank}: {description[:50]}...")
            
            return description
            
        except Exception as e:
            logger.error(f"Error generating description: {e}")
            return f"At number {product_rank} is the {product_name}! A top-rated choice in {category}!"
    
    async def optimize_all_products(self, products: List[Dict], category: str) -> List[Dict]:
        """
        Optimize all product titles and generate countdown descriptions
        """
        
        optimized_products = []
        
        for i, product in enumerate(products[:5]):  # Only process top 5
            product_rank = 5 - i  # Countdown: Product 1 = #5, Product 5 = #1
            
            # Optimize title
            original_title = product.get('title', f'Product {i+1}')
            optimized_title = await self.optimize_product_title(original_title)
            
            # Generate countdown description
            countdown_description = await self.generate_countdown_description(
                product_name=optimized_title,
                product_rank=product_rank,
                product_details=product,
                category=category
            )
            
            # Create optimized product
            optimized_product = product.copy()
            optimized_product['title'] = optimized_title
            optimized_product['original_title'] = original_title
            optimized_product['countdown_description'] = countdown_description
            optimized_product['countdown_rank'] = product_rank
            
            optimized_products.append(optimized_product)
            
            # Small delay to be API-friendly
            await asyncio.sleep(1)
        
        logger.info(f"✅ Optimized {len(optimized_products)} products for countdown")
        return optimized_products
    
    async def generate_intro_outro(self, video_title: str, category: str, winner_product: str) -> Dict:
        """
        Generate intro hook and outro call-to-action (5 seconds each = ~10 words)
        """
        
        try:
            prompt = f"""
            Generate intro hook and outro call-to-action for a Top 5 countdown video.
            
            Video title: {video_title}
            Category: {category}
            Winner product: {winner_product}
            
            STRICT REQUIREMENTS:
            - Intro: EXACTLY 10 words maximum (5 seconds of speech)
            - Outro: EXACTLY 12 words maximum (6 seconds of speech) - simple thanks message
            - Energetic countdown style for intro
            - Create urgency and excitement for intro
            - Outro should be simple and direct
            
            Examples:
            Intro: "This {category} will change everything - let's count down!"
            Outro: "Thanks for watching and the affiliate links are in the video descriptions"
            
            Return as JSON:
            {{
                "intro_hook": "10-word intro",
                "outro_cta": "Thanks for watching and the affiliate links are in the video descriptions"
            }}
            """
            
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            
            import json
            response_text = response.content[0].text
            
            # Extract JSON
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                intro_outro = json.loads(json_str)
                
                # Always use the specific outro text requested by user
                intro_outro['outro_cta'] = "Thanks for watching and the affiliate links are in the video descriptions"
                
                # Validate word counts
                intro_words = len(intro_outro['intro_hook'].split())
                outro_words = len(intro_outro['outro_cta'].split())
                
                logger.info(f"📝 Generated intro ({intro_words} words) and outro ({outro_words} words)")
                return intro_outro
            else:
                # Fallback
                return {
                    "intro_hook": f"Best {category} countdown starts now!",
                    "outro_cta": "Links below - grab yours today!"
                }
                
        except Exception as e:
            logger.error(f"Error generating intro/outro: {e}")
            return {
                "intro_hook": f"Top 5 {category} countdown!",
                "outro_cta": "Check links below now!"
            }