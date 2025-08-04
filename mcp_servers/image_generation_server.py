#!/usr/bin/env python3
"""
OpenAI Image Generation MCP Server
Generates high-quality product images using DALL-E 3 with Amazon images as reference
"""

import asyncio
import logging
from typing import Dict, Optional
import httpx
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

class ImageGenerationMCPServer:
    """OpenAI Image Generation Server for creating product showcase images"""
    
    def __init__(self, openai_api_key: str):
        self.client = AsyncOpenAI(api_key=openai_api_key)
        
    async def generate_product_image_with_amazon_reference(
        self, 
        product_name: str, 
        product_number: int,
        amazon_image_url: str,
        product_details: Dict
    ) -> Optional[str]:
        """
        Generate a high-quality product image using Amazon image as reference
        Uses the product_prompt.md template for consistent e-commerce style
        """
        
        try:
            # Build the enhanced prompt using the template from product_prompt.md
            # Amazon image is ONLY for product reference - we create a new stylized image
            prompt = f"""
            A high-resolution, ultra-realistic 9:16 vertical product photo of a {product_name}.
            
            IMPORTANT: Use this Amazon product photo ONLY as reference to identify the exact product: {amazon_image_url}
            The reference shows the actual product that needs to be recreated in a professional studio setting.
            
            Create a NEW stylized image with:
            - The SAME product as shown in the reference image but in a professional studio setting
            - Product floating slightly above the ground with a soft natural shadow underneath
            - Sharp detail with accurate lighting reflections and visible textures
            - Vibrant, colorful gradient background (purple to orange recommended)
            - Bokeh or abstract lighting effects in background
            - Product centered and isolated with dramatic studio lighting
            - Realistic shadows and soft depth-of-field blur in background
            
            Product context for accuracy:
            - This is product #{product_number} in the top 5 bestsellers
            - Rating: {product_details.get('rating', '')} stars
            - Price: ${product_details.get('price', '')}
            
            The final image must be a clean, commercial-grade product photo suitable for e-commerce platforms.
            Leave negative space at top and bottom for text overlays.
            
            Style: product showcase, studio lighting, e-commerce hero shot, high contrast, professional product photography
            """
            
            logger.info(f"🎨 Generating OpenAI image for: {product_name[:50]}...")
            logger.info(f"   Using Amazon reference: {amazon_image_url[:50]}...")
            
            # Generate image using DALL-E 3
            response = await self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1792",  # 9:16 aspect ratio for vertical video
                quality="hd",
                n=1
            )
            
            if response.data and len(response.data) > 0:
                image_url = response.data[0].url
                logger.info(f"✅ Generated OpenAI image: {image_url[:50]}...")
                return image_url
            else:
                logger.error(f"No image generated for {product_name}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating image for {product_name}: {str(e)}")
            return None
    
    async def generate_product_image(self, product_name: str, product_number: int) -> Optional[str]:
        """
        Generate a product image without Amazon reference (fallback method)
        """
        
        try:
            prompt = f"""
            A high-resolution, ultra-realistic 9:16 vertical product photo of a {product_name}, 
            floating slightly above the ground with a soft natural shadow underneath. 
            The product is rendered in sharp detail with accurate lighting reflections and visible textures. 
            
            The background features a vibrant purple-to-orange gradient with bokeh-style lighting. 
            The scene has dramatic lighting, clean shadows, and cinematic depth-of-field. 
            Center the product and leave some negative space above and below for text overlays. 
            
            Product position: #{product_number} in top 5 bestsellers
            
            Perfect for e-commerce platforms. Style: product showcase, studio lighting, 
            e-commerce banner, high contrast, background blur, hero shot
            """
            
            logger.info(f"🎨 Generating OpenAI image (no reference) for: {product_name[:50]}...")
            
            response = await self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1792",  # 9:16 aspect ratio
                quality="hd",
                n=1
            )
            
            if response.data and len(response.data) > 0:
                return response.data[0].url
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            return None
    
    async def generate_intro_image(self, title: str, category: str) -> Optional[str]:
        """Generate intro image for video"""
        
        try:
            prompt = f"""
            A stunning 9:16 vertical banner image for a video titled "{title}".
            Product category: {category}
            
            The image should feature:
            - Bold, eye-catching gradient background (purple to orange)
            - Abstract geometric shapes suggesting the product category
            - Dramatic lighting effects with lens flares
            - Space for overlaying text in the center
            - Professional e-commerce aesthetic
            - High energy and excitement
            
            Style: modern, vibrant, commercial, hero banner, product showcase intro
            """
            
            response = await self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1792",
                quality="hd",
                n=1
            )
            
            if response.data and len(response.data) > 0:
                return response.data[0].url
            return None
            
        except Exception as e:
            logger.error(f"Error generating intro image: {str(e)}")
            return None
    
    async def generate_outro_image(self, title: str, cta: str) -> Optional[str]:
        """Generate outro image for video"""
        
        try:
            prompt = f"""
            A professional 9:16 vertical outro banner for an e-commerce video.
            Video title: "{title}"
            Call to action theme: "{cta}"
            
            The image should feature:
            - Gradient background transitioning from blue to purple
            - Subtle shopping cart or purchase icons
            - Space for call-to-action text overlay
            - Professional finish suggesting quality and trust
            - Soft bokeh effects in background
            
            Style: professional, trustworthy, e-commerce outro, call-to-action banner
            """
            
            response = await self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1792",
                quality="hd",
                n=1
            )
            
            if response.data and len(response.data) > 0:
                return response.data[0].url
            return None
            
        except Exception as e:
            logger.error(f"Error generating outro image: {str(e)}")
            return None