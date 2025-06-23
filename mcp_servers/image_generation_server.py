import asyncio
import json
import openai
from typing import Dict, List, Optional
import requests
import base64

class ImageGenerationMCPServer:
    def __init__(self, openai_api_key: str):
        openai.api_key = openai_api_key
        
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
