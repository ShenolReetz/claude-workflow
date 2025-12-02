"""
Image Generator SubAgent with HuggingFace FLUX
===============================================
Generates product images using HuggingFace FLUX.1-schnell for COST SAVINGS!

COST: $0.00/image (vs $0.03 with fal.ai)
SPEED: 3-4 seconds per image
QUALITY: Excellent
"""

import sys
import asyncio
import os
from typing import Dict, Any
from pathlib import Path

sys.path.append('/home/claude-workflow')

from agents.base_subagent import BaseSubAgent
from agents.content_generation.hf_image_client import HFImageClient
from src.utils.dual_storage_manager import get_storage_manager


class ImageGeneratorSubAgent(BaseSubAgent):
    """
    Generates product images using HuggingFace FLUX.1-schnell

    Features:
    - Uses FREE HuggingFace Inference API
    - Falls back to fal.ai if HF fails
    - Saves images locally for Remotion
    - Optimizes prompts for product images
    """

    def __init__(self, name: str, config: Dict[str, Any], parent_agent_id: str = None):
        super().__init__(name, config, parent_agent_id)

        # Check if HF is enabled
        self.use_hf = config.get('hf_use_inference_api', True)

        # Initialize HuggingFace image client only if enabled
        if self.use_hf:
            self.hf_client = HFImageClient(config)

        # Fallback to fal.ai if configured
        self.use_fallback = config.get('image_generation_fallback', True)

        # Initialize DualStorageManager for local + Google Drive storage
        self.storage_manager = get_storage_manager(config)

        if self.use_hf:
            self.logger.info("✅ ImageGeneratorSubAgent initialized with HuggingFace FLUX.1-schnell")
            self.logger.info("💰 Cost savings: $0.03 → $0.00 per image!")
        else:
            self.logger.info("✅ ImageGeneratorSubAgent initialized with fal.ai fallback")
            self.logger.info("💰 Cost: $0.03 per image")

    async def execute_task(self, task: Dict[str, Any]) -> Any:
        """
        Generate product image using HuggingFace FLUX

        Args:
            task: Task with 'product' data, 'product_index', and 'record_id'

        Returns:
            Dict with image_path, drive_url, method, and cost
        """
        product = task.get('product')
        product_index = task.get('product_index', 1)
        record_id = task.get('record_id', 'unknown')

        if not product:
            raise ValueError("No product data provided")

        self.logger.info(f"🖼️  Generating image {product_index} with HF FLUX...")

        try:
            # Build prompt for product image
            prompt = self._build_product_prompt(product)

            # Skip HF if disabled, go straight to fallback
            if not self.use_hf:
                self.logger.info(f"🔄 Using fal.ai (HF disabled in config)")
                return await self._fallback_fal_ai(product, product_index, prompt)

            # Try HuggingFace first if enabled
            try:
                # HF FLUX doesn't support reference images - generates from prompt only
                result = await self.hf_client.generate_image(
                    prompt=prompt,
                    width=1080,
                    height=1920
                )

                # Check if HF generation was successful
                if not result.get('success', False):
                    error_msg = result.get('error', 'Unknown HF error')
                    self.logger.warning(f"⚠️  HuggingFace failed: {error_msg}")

                    # Fallback to fal.ai if enabled
                    if self.use_fallback:
                        return await self._fallback_fal_ai(product, product_index, prompt)
                    else:
                        raise RuntimeError(f"HuggingFace generation failed: {error_msg}")

                # Extract image bytes from successful result
                image_bytes = result.get('image_bytes')
                if not image_bytes:
                    raise ValueError("HF result missing image_bytes")

                # Save image locally + Google Drive
                save_result = await self._save_image(image_bytes, product_index, record_id)

                self.logger.info(f"✅ Image {product_index} generated with HuggingFace (FREE): {save_result['local_path']}")
                if save_result.get('drive_url'):
                    self.logger.info(f"☁️ Uploaded to Google Drive: {save_result['drive_url']}")

                return {
                    'image_path': save_result['local_path'],
                    'drive_url': save_result.get('drive_url'),
                    'method': 'huggingface_flux',
                    'cost': 0.00
                }

            except Exception as hf_error:
                self.logger.error(f"❌ HuggingFace exception: {hf_error}")

                # Fallback to fal.ai if enabled
                if self.use_fallback:
                    return await self._fallback_fal_ai(product, product_index, prompt)
                else:
                    raise hf_error

        except Exception as e:
            self.logger.error(f"❌ Image generation failed: {e}")
            raise

    def _build_product_prompt(self, product: Dict[str, Any]) -> str:
        """Build optimized prompt for product image"""
        title = product.get('title', '')

        # Extract key product features
        # Clean up title for prompt
        clean_title = title.replace('Amazon.com:', '').replace('|', ',').strip()

        # Create professional product image prompt
        prompt = f"""Professional product photography of {clean_title}.
High-quality, well-lit studio shot.
Clean white background.
Product centered and in focus.
Professional lighting, sharp details.
Commercial photography style.
4K quality, high resolution."""

        return prompt

    async def _save_image(self, image_data: bytes, product_index: int, record_id: str) -> Dict:
        """Save generated image to local storage + Google Drive"""
        filename = f"product{product_index}.jpg"

        # Use DualStorageManager to save locally + Google Drive
        result = await self.storage_manager.save_media(
            content=image_data,
            filename=filename,
            media_type='image',
            record_id=record_id,
            upload_to_drive=True  # Enable Google Drive upload
        )

        if result.get('success'):
            self.logger.debug(f"💾 Saved image to: {result['local_path']}")
            if result.get('drive_url'):
                self.logger.debug(f"☁️ Google Drive: {result['drive_url']}")
        else:
            raise RuntimeError(f"Failed to save image: {result.get('error')}")

        return result

    async def _fallback_fal_ai(self, product: Dict[str, Any], product_index: int, prompt: str) -> Dict[str, Any]:
        """Fallback to fal.ai if HuggingFace fails"""
        self.logger.info(f"🔄 Falling back to fal.ai for image {product_index}...")

        try:
            # With real Amazon scraper, we should have real image URLs
            # Proceed to fal.ai for image enhancement

            # Import fal.ai generator class
            from src.mcp.production_fal_image_generator import FalImageGenerator

            # Instantiate fal.ai generator
            generator = FalImageGenerator(self.config)

            # Get record_id from parent agent context if available
            record_id = self.parent_agent_id or 'unknown'

            # Generate with fal.ai using single-product method
            result = await generator.enhance_product_image(
                amazon_image_url=product.get('image_url', ''),
                product_title=product.get('title', ''),
                product_description=product.get('description', ''),
                product_num=product_index,
                record_id=record_id,
                vision_analysis=None
            )

            if result.get('success'):
                self.logger.warning(f"⚠️  Image {product_index} generated with fal.ai (fallback, cost: $0.03)")

                return {
                    'image_path': result['local_path'],
                    'drive_url': result.get('drive_url'),  # Include Google Drive URL if available
                    'method': 'fal_ai_fallback',
                    'cost': 0.03
                }
            else:
                raise RuntimeError(f"fal.ai generation failed: {result.get('error', 'Unknown error')}")

        except Exception as e:
            self.logger.error(f"❌ Fallback also failed: {e}")
            raise RuntimeError(f"Both HuggingFace and fal.ai failed for image {product_index}")

    async def validate_input(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input parameters"""
        if 'product' not in task:
            return {'valid': False, 'error': 'Missing product data'}

        product = task['product']
        if not isinstance(product, dict):
            return {'valid': False, 'error': 'Product must be a dictionary'}

        # Check for required fields
        if 'title' not in product:
            return {'valid': False, 'error': 'Product missing title'}

        return {'valid': True}

    async def validate_output(self, result: Any) -> Dict[str, Any]:
        """Validate output result"""
        if not isinstance(result, dict):
            return {'valid': False, 'error': 'Result must be a dictionary'}

        if 'image_path' not in result:
            return {'valid': False, 'error': 'Missing image_path in result'}

        # Check if image file exists
        image_path = result['image_path']
        if not os.path.exists(image_path):
            return {'valid': False, 'error': f'Image file not found: {image_path}'}

        # Check file size (should be > 10KB)
        file_size = os.path.getsize(image_path)
        if file_size < 10000:  # 10KB
            return {'valid': False, 'error': f'Image file too small: {file_size} bytes'}

        return {'valid': True}
