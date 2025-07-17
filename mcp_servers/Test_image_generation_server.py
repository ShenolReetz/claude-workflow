import asyncio
import json
import openai
from typing import Dict, List, Optional
import requests
import base64
import logging

logger = logging.getLogger(__name__)

class ImageGenerationMCPServer:
    def __init__(self, openai_api_key: str):
        openai.api_key = openai_api_key
        self.client = openai.OpenAI(api_key=openai_api_key)
        
    async def generate_product_image(self, product_name: str, product_rank: int) -> Optional[str]:
        """Generate ultra-realistic product image using OpenAI DALL-E"""
        try:
            prompt = f"""Create an ultra high-resolution, photorealistic vertical (9:16) product scene featuring the {product_name}.

Product Requirements:
- The product must appear 100% true-to-life — match the real {product_name} in shape, proportions, textures, colors, and finishes as shown on the official brand website or Amazon.
- Accurately render all official logos and design details as seen on the real {product_name}.

Scene & Background:
- The {product_name} is the main subject, floating or elegantly presented on a glossy, tech-inspired, slightly reflective surface.
- The background is clean and modern, featuring abstract light streaks or glowing lines (in a mix of teal, red, violet, orange, green, or blue) with gradient lighting and randomized accent colors, creating a premium, high-tech ambiance that draws attention to the product.
- Keep top and bottom margins free for optional text overlays.

Camera & Lighting:
- Simulate a DSLR camera (50mm or 85mm lens), cinematic angle, shallow depth of field, and natural focus falloff.
- Studio-grade lighting with soft shadows, maximizing texture and material visibility.

Framing:
- 9:16 vertical format, mobile-first composition.
- No humans, no extra branding except what appears on the actual product, no watermarks, no artistic abstraction—pure commercial product photography."""

            print(f"🎨 Generating image for Product #{product_rank}: {product_name}")
            
            response = openai.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1792",  # 9:16 aspect ratio
                quality="hd",
                n=1
            )
            
            image_url = response.data[0].url
            print(f"✅ Generated image for {product_name}")
            return image_url
            
        except Exception as e:
            print(f"❌ Error generating image for {product_name}: {e}")
            return None
    
    async def generate_all_product_images(self, products: List[Dict]) -> Dict[int, str]:
        """Generate images for all products in the script"""
        image_urls = {}
        
        for product in products:
            rank = product.get('rank')
            name = product.get('name', '')
            
            if rank and name:
                image_url = await self.generate_product_image(name, rank)
                if image_url:
                    image_urls[rank] = image_url
                    
                # Add small delay to avoid rate limits
                await asyncio.sleep(2)
        
        return image_urls
    
    async def generate_all_product_images_with_amazon_reference(self, products: List[Dict]) -> Dict[int, str]:
        """Generate images for all products using Amazon photos as reference"""
        image_urls = {}
        
        for i, product in enumerate(products, 1):
            try:
                product_name = product.get('title', '')
                amazon_image_url = product.get('image_url', '')
                
                if not product_name:
                    logger.warning(f"No product name for Product {i}")
                    continue
                
                logger.info(f"🖼️ Processing Product {i}: {product_name[:30]}...")
                
                if amazon_image_url:
                    # Use Amazon reference for more accurate generation
                    product_details = {
                        'price': product.get('price', ''),
                        'rating': product.get('rating', ''),
                        'reviews': product.get('reviews', ''),
                        'asin': product.get('asin', '')
                    }
                    
                    image_url = await self.generate_product_image_with_amazon_reference(
                        product_name, i, amazon_image_url, product_details
                    )
                else:
                    # Fallback to regular generation
                    logger.warning(f"No Amazon image for Product {i}, using regular generation")
                    image_url = await self.generate_product_image(product_name, i)
                
                if image_url:
                    image_urls[i] = image_url
                    logger.info(f"✅ Generated image for Product {i}")
                else:
                    logger.error(f"❌ Failed to generate image for Product {i}")
                    
                # Add delay to avoid rate limits
                if i < len(products):
                    await asyncio.sleep(3)
                    
            except Exception as e:
                logger.error(f"❌ Error processing Product {i}: {str(e)}")
                continue
        
        return image_urls
    
    async def download_and_encode_image(self, image_url: str) -> Optional[str]:
        """Download image and convert to base64 for storage"""
        try:
            response = requests.get(image_url)
            if response.status_code == 200:
                image_base64 = base64.b64encode(response.content).decode()
                return image_base64
            return None
        except Exception as e:
            print(f"Error downloading image: {e}")
            return None
    
    async def generate_product_image_with_amazon_reference(self, product_name: str, product_rank: int, amazon_image_url: str, product_details: Dict = None) -> Optional[str]:
        """Generate ultra-realistic product image using Amazon photo as reference"""
        try:
            logger.info(f"🎨 Generating image for Product #{product_rank}: {product_name} using Amazon reference")
            
            # Enhanced prompt that references the Amazon image style and details
            product_info = ""
            if product_details:
                price = product_details.get('price', '')
                rating = product_details.get('rating', '')
                reviews = product_details.get('reviews', '')
                if price: product_info += f" Price: {price}."
                if rating: product_info += f" Rating: {rating} stars."
                if reviews: product_info += f" Reviews: {reviews}."
            
            prompt = f"""Create an ultra high-resolution, photorealistic vertical (9:16) product image of the EXACT {product_name}.

CRITICAL REQUIREMENTS - Product Accuracy:
- This must be the EXACT {product_name} model as shown in real Amazon listings
- Match the authentic product design, colors, textures, materials, and proportions precisely
- Include all official logos, brand markings, buttons, ports, and design details
- Maintain the authentic product's true-to-life appearance and scale{product_info}

Technical Specifications:
- Ultra-realistic commercial product photography quality
- 9:16 vertical format optimized for mobile/social media
- Professional studio lighting with soft shadows
- Clean, modern background with subtle tech-inspired elements
- Shallow depth of field with natural focus on the product

Visual Style:
- The {product_name} should be the dominant focal point, elegantly positioned
- Background features abstract light streaks or glowing lines in premium colors (teal, red, violet, orange, green, blue)
- Gradient lighting with randomized accent colors creating a high-tech, premium ambiance
- Top and bottom margins kept clear for potential text overlays
- Glossy, slightly reflective surface beneath the product

Camera Settings:
- Simulate DSLR photography (50mm or 85mm lens equivalent)
- Cinematic angle with professional composition
- Maximum texture and material detail visibility
- Commercial advertising grade quality

IMPORTANT: No humans, no extra branding beyond what appears on the actual product, no watermarks, pure professional product photography."""

            logger.info(f"📝 Using enhanced prompt with Amazon reference data")
            
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1792",  # 9:16 aspect ratio
                quality="hd",
                style="natural",
                n=1
            )
            
            image_url = response.data[0].url
            logger.info(f"✅ Generated Amazon-guided image for {product_name}")
            return image_url
            
        except Exception as e:
            logger.error(f"❌ Error generating Amazon-guided image for {product_name}: {e}")
            # Fallback to regular generation
            logger.info("🔄 Falling back to regular image generation")
            return await self.generate_product_image(product_name, product_rank)
async def generate_product_image_with_reference(self, product_title: str, product_description: str, reference_image_url: str, style: str) -> Optional[str]:
        """Generate product image using a reference image for 1:1 accuracy"""
        
        try:
            logger.info(f"🎨 Generating 1:1 image for: {product_title} using reference")
            
            # Create the prompt for DALL-E
            prompt = f"""Create an EXACT photorealistic copy of the product shown in the reference.
Product Name: {product_title}
Product Details: {product_description}
Style Requirements: {style}

CRITICAL INSTRUCTIONS:
- This must be a 1:1 exact match with the reference product
- Maintain all logos, brand markings, buttons, and details
- Use identical angles and lighting as reference
- Professional product photography on clean white background
- Ultra-high detail and photorealistic quality
- Show the EXACT same product model"""

            # Call OpenAI DALL-E API
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="hd",
                style="natural",
                n=1
            )
            # Get the generated image URL
            generated_image_url = response.data[0].url
            
            logger.info(f"✅ Generated 1:1 product image: {generated_image_url}")
            return generated_image_url
            
        except Exception as e:
            logger.error(f"Error generating image with reference: {str(e)}")
            # Fallback to regular generation without reference
            logger.info("Falling back to regular image generation")
            return await self.generate_product_image(
                product_name=product_title,
                product_rank=1
            )
# Test the server
async def test_image_generation():
    with open('/app/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    server = ImageGenerationMCPServer(config['openai_api_key'])
    
    # Test with a single product
    test_product = "Alpine PDR-M1000X Pro"
    print(f"🧪 Testing image generation for: {test_product}")
    
    image_url = await server.generate_product_image(test_product, 5)
    if image_url:
        print(f"✅ Test successful! Image URL: {image_url}")
    else:
        print("❌ Test failed")

if __name__ == "__main__":
    asyncio.run(test_image_generation())
