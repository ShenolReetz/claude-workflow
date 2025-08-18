#!/usr/bin/env python3
"""
Production Image Generation with GPT-4o Vision + Imagen 4 Ultra
================================================================
1. Analyze Amazon scraped images with GPT-4o Vision
2. Generate detailed product descriptions
3. Create enhanced images with Imagen 4 Ultra
"""

import asyncio
import aiohttp
import base64
import json
from typing import Dict, List, Optional
import logging
from pathlib import Path
import time
import openai
from src.utils.dual_storage_manager import get_storage_manager

logger = logging.getLogger(__name__)


class Imagen4UltraWithGPT4Vision:
    """
    Two-step image generation:
    1. GPT-4o analyzes Amazon product photo
    2. Imagen 4 Ultra generates enhanced version
    """
    
    def __init__(self, config: Dict):
        self.config = config
        # OpenAI for GPT-4o Vision
        self.openai_api_key = config.get('openai_api_key')
        openai.api_key = self.openai_api_key
        
        # Google Imagen 4 Ultra API key (provided by user)
        self.imagen_api_key = "AIzaSyAyLn6dRabkrwr9gIHBdqbL8Fyzfv47Mpc"
        self.project_id = config.get('google_project_id', 'your-project-id')
        self.location = config.get('google_location', 'us-central1')
        
        # Storage manager
        self.storage_manager = get_storage_manager(config)
        
    async def generate_enhanced_product_images(self, record: Dict) -> Dict:
        """
        Main function to generate all product images
        """
        try:
            start_time = time.time()
            fields = record.get('fields', {})
            record_id = record.get('record_id', 'unknown')
            
            logger.info("""
╔════════════════════════════════════════════════════════════╗
║  🎨 STARTING IMAGE GENERATION WITH IMAGEN 4 ULTRA         ║
║  Step 1: GPT-4o Vision analyzes Amazon photos             ║
║  Step 2: Imagen 4 Ultra generates enhanced versions       ║
╚════════════════════════════════════════════════════════════╝
""")
            
            # Process all products in parallel
            tasks = []
            for i in range(1, 6):
                amazon_url = fields.get(f'ProductNo{i}Photo', '')
                product_title = fields.get(f'ProductNo{i}Title', '')
                product_description = fields.get(f'ProductNo{i}Description', '')
                
                if amazon_url and product_title:
                    task = self.process_single_product(
                        amazon_image_url=amazon_url,
                        product_title=product_title,
                        product_description=product_description,
                        product_num=i,
                        record_id=record_id
                    )
                    tasks.append((i, task))
            
            # Also generate intro and outro
            intro_task = self.generate_intro_outro(
                video_title=fields.get('VideoTitle', 'Amazing Products'),
                image_type='intro',
                record_id=record_id
            )
            tasks.append(('intro', intro_task))
            
            outro_task = self.generate_intro_outro(
                video_title=fields.get('VideoTitle', 'Amazing Products'),
                image_type='outro',
                record_id=record_id
            )
            tasks.append(('outro', outro_task))
            
            # Execute all tasks
            results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
            
            # Process results
            success_count = 0
            failed_images = []
            
            for (identifier, _), result in zip(tasks, results):
                if isinstance(result, Exception):
                    logger.error(f"❌ Error processing {identifier}: {result}")
                    failed_images.append(str(identifier))
                elif isinstance(result, dict) and result.get('success'):
                    if isinstance(identifier, int):  # Product image
                        fields[f'ProductNo{identifier}Photo'] = result['local_path']
                        fields[f'ProductNo{identifier}Photo_Local'] = result['local_path']
                        if result.get('vision_analysis'):
                            fields[f'ProductNo{identifier}VisionAnalysis'] = result['vision_analysis']
                    elif identifier == 'intro':
                        fields['IntroPhoto'] = result['local_path']
                        fields['IntroPhoto_Local'] = result['local_path']
                    elif identifier == 'outro':
                        fields['OutroPhoto'] = result['local_path']
                        fields['OutroPhoto_Local'] = result['local_path']
                    
                    success_count += 1
                    logger.info(f"✅ {identifier} image generated successfully")
                else:
                    failed_images.append(str(identifier))
            
            elapsed_time = time.time() - start_time
            
            # Update record
            record['fields'] = fields
            
            logger.info(f"""
════════════════════════════════════════
📊 IMAGE GENERATION COMPLETE
════════════════════════════════════════
✅ Success: {success_count}/{len(tasks)} images
⏱️ Time: {elapsed_time:.1f} seconds
🎨 Model: Imagen 4 Ultra
🔍 Analysis: GPT-4o Vision
{f"❌ Failed: {', '.join(failed_images)}" if failed_images else ""}
════════════════════════════════════════
""")
            
            return {
                'success': success_count > 0,
                'images_generated': success_count,
                'failed_images': failed_images,
                'updated_record': record,
                'elapsed_time': elapsed_time
            }
            
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'updated_record': record
            }
    
    async def process_single_product(self,
                                    amazon_image_url: str,
                                    product_title: str,
                                    product_description: str,
                                    product_num: int,
                                    record_id: str) -> Dict:
        """
        Process a single product image:
        1. Analyze with GPT-4o Vision
        2. Generate with Imagen 4 Ultra
        """
        try:
            logger.info(f"🔍 Analyzing product {product_num} with GPT-4o Vision...")
            
            # Step 1: Analyze Amazon image with GPT-4o Vision
            vision_analysis = await self.analyze_with_gpt4_vision(
                image_url=amazon_image_url,
                product_title=product_title,
                product_description=product_description
            )
            
            if not vision_analysis:
                logger.warning(f"Failed to analyze product {product_num}, using fallback description")
                vision_analysis = product_description
            
            logger.info(f"📝 Vision analysis complete for product {product_num}")
            
            # Step 2: Generate enhanced image with Imagen 4 Ultra
            logger.info(f"🎨 Generating product {product_num} with Imagen 4 Ultra...")
            
            # Combine vision analysis with existing prompt style
            enhanced_prompt = f"""Create a high-quality product showcase image for video content.

Product: {product_title}
Rank: #{product_num} Best Seller

VISUAL DETAILS FROM ACTUAL PRODUCT:
{vision_analysis}

CRITICAL REQUIREMENTS:
- Match the exact product design, colors, and features described above
- Preserve ALL text, logos, and branding exactly as described
- Maintain all product specifications and features visible
- Professional studio lighting with clean background
- 9:16 aspect ratio optimized for Instagram Stories/Reels
- Add subtle "#{product_num}" badge in corner
- Ensure all product details are clearly visible
- Professional product photography style
- Clean, modern presentation suitable for video

Original Description: {product_description[:200] if product_description else ''}

Style: Professional product photography, clean e-commerce style, high resolution, perfect for video content."""
            
            # Generate with Imagen 4 Ultra
            imagen_result = await self.generate_with_imagen4_ultra(
                prompt=enhanced_prompt,
                product_num=product_num,
                record_id=record_id
            )
            
            if imagen_result.get('success'):
                return {
                    'success': True,
                    'local_path': imagen_result['local_path'],
                    'vision_analysis': vision_analysis[:500],  # Store first 500 chars
                    'product_num': product_num
                }
            else:
                return {
                    'success': False,
                    'error': imagen_result.get('error', 'Imagen generation failed')
                }
                
        except Exception as e:
            logger.error(f"Error processing product {product_num}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def analyze_with_gpt4_vision(self,
                                      image_url: str,
                                      product_title: str,
                                      product_description: str) -> Optional[str]:
        """
        Analyze Amazon product image with GPT-4o Vision
        """
        try:
            # Create the vision analysis prompt
            messages = [
                {
                    "role": "system",
                    "content": "You are a product image analyst. Provide detailed, structured descriptions of products for image generation."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"""Analyze this product image and provide a detailed, structured description for recreating it.
Product Title: {product_title}

Please describe:
1. PRODUCT TYPE & SHAPE: Exact product type, form factor, dimensions
2. COLORS: Primary colors, secondary colors, color placement
3. MATERIALS & TEXTURES: Visible materials, surface textures, finishes
4. TEXT & BRANDING: Any visible text, logos, brand names, labels (describe exactly)
5. UNIQUE FEATURES: Buttons, ports, displays, special features
6. PACKAGING: If visible, describe packaging elements
7. OVERALL STYLE: Modern/classic, premium/budget, target audience

Be extremely specific and detailed. This description will be used to generate an accurate product image."""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url,
                                "detail": "high"
                            }
                        }
                    ]
                }
            ]
            
            # Call GPT-4o Vision
            response = await asyncio.to_thread(
                openai.chat.completions.create,
                model="gpt-4o",
                messages=messages,
                max_tokens=500,
                temperature=0.3  # Lower temperature for more accurate descriptions
            )
            
            if response and response.choices:
                analysis = response.choices[0].message.content
                return analysis
            
            return None
            
        except Exception as e:
            logger.error(f"GPT-4o Vision analysis failed: {e}")
            return None
    
    async def generate_with_imagen4_ultra(self,
                                         prompt: str,
                                         product_num: int,
                                         record_id: str) -> Dict:
        """
        Generate image with Imagen 4 Ultra using the provided API key
        """
        try:
            # Imagen 4 Ultra API endpoint
            url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-ultra-generate-001:generateImages"
            
            # Prepare request
            headers = {
                "Content-Type": "application/json",
                "X-Goog-Api-Key": self.imagen_api_key
            }
            
            payload = {
                "instances": [
                    {
                        "prompt": prompt
                    }
                ],
                "parameters": {
                    "sampleCount": 1,
                    "aspectRatio": "9:16",  # For Instagram/TikTok
                    "safetyFilterLevel": "block_some",
                    "personGeneration": "allow_all",
                    "outputOptions": {
                        "mimeType": "image/jpeg",
                        "compressionQuality": 95
                    }
                }
            }
            
            # Make API request
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        # Extract generated image
                        if result.get('predictions') and len(result['predictions']) > 0:
                            image_data_base64 = result['predictions'][0].get('bytesBase64Encoded')
                            
                            if image_data_base64:
                                # Decode base64 image
                                image_data = base64.b64decode(image_data_base64)
                                
                                # Save locally
                                filename = f"product{product_num}_imagen4ultra.jpg"
                                save_result = await self.storage_manager.save_media(
                                    content=image_data,
                                    filename=filename,
                                    media_type="image",
                                    record_id=record_id,
                                    upload_to_drive=False  # Local only
                                )
                                
                                if save_result.get('success'):
                                    logger.info(f"✅ Imagen 4 Ultra generated product {product_num}")
                                    return {
                                        'success': True,
                                        'local_path': save_result['local_path']
                                    }
                        
                        return {
                            'success': False,
                            'error': 'No image in response'
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"Imagen 4 Ultra API error: {response.status} - {error_text}")
                        return {
                            'success': False,
                            'error': f'API error: {response.status}'
                        }
                        
        except Exception as e:
            logger.error(f"Imagen 4 Ultra generation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def generate_intro_outro(self,
                                  video_title: str,
                                  image_type: str,
                                  record_id: str) -> Dict:
        """
        Generate intro or outro image with Imagen 4 Ultra
        """
        try:
            if image_type == 'intro':
                prompt = f"""Create an eye-catching intro image for a product countdown video.
Title: "Top 5 {video_title}"
Style: Modern, vibrant, exciting countdown theme
Text overlay: "Top 5 {video_title}" in bold, dynamic typography
Include: Number "5" prominently displayed, countdown timer visual
Colors: Bright yellow (#FFFF00) and green (#00FF00) accents on dark background
Layout: 9:16 aspect ratio for Instagram/TikTok
Quality: Ultra high definition, professional graphic design"""
            else:  # outro
                prompt = f"""Create a "Thanks for watching" outro image for a product video.
Main text: "Thanks for Watching!" in large, friendly font
Secondary text: "Subscribe for More Amazing Products!"
Include: Subscribe button graphic, thumbs up icon, notification bell icon
Style: Engaging, colorful, clear call-to-action
Colors: Bright and inviting with yellow (#FFFF00) and green (#00FF00) CTAs
Layout: 9:16 aspect ratio for Instagram/TikTok
Quality: Ultra high definition, professional graphic design"""
            
            # Generate with Imagen 4 Ultra
            imagen_result = await self.generate_with_imagen4_ultra(
                prompt=prompt,
                product_num=0 if image_type == 'intro' else 6,
                record_id=record_id
            )
            
            if imagen_result.get('success'):
                # Rename file appropriately
                local_path = imagen_result['local_path']
                new_path = local_path.replace('product0', 'intro').replace('product6', 'outro')
                
                if local_path != new_path:
                    Path(local_path).rename(new_path)
                    local_path = new_path
                
                return {
                    'success': True,
                    'local_path': local_path,
                    'image_type': image_type
                }
            else:
                return imagen_result
                
        except Exception as e:
            logger.error(f"Error generating {image_type}: {e}")
            return {
                'success': False,
                'error': str(e)
            }


# Export main function
async def production_generate_images_with_imagen4_ultra(record: Dict, config: Dict) -> Dict:
    """
    Main entry point for Imagen 4 Ultra image generation
    """
    generator = Imagen4UltraWithGPT4Vision(config)
    return await generator.generate_enhanced_product_images(record)