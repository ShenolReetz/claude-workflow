"""
Hugging Face Image Generation Client
=====================================
Generates images using FLUX.1-schnell via HF Inference API.
"""

import asyncio
import aiohttp
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class HuggingFaceImageClient:
    """
    Client for HF FLUX.1-schnell image generation
    Replaces fal.ai to save costs
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_token = config.get('hf_api_token')
        self.model_id = config.get('hf_image_model', 'black-forest-labs/FLUX.1-schnell')

        # Use router endpoint as per HF API (api-inference is deprecated)
        self.base_url = f"https://router.huggingface.co/models/{self.model_id}"

        # Generation parameters
        self.num_inference_steps = 4  # schnell uses 4 steps
        self.guidance_scale = 0        # schnell doesn't use guidance

        self.logger = logging.getLogger(__name__)
        self.logger.info(f"🎨 HF Image Client initialized: {self.model_id}")

    async def generate_image(self, prompt: str, width: int = 1080, height: int = 1920,
                            save_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate image from text prompt

        Args:
            prompt: Text description
            width: Image width
            height: Image height
            save_path: Optional path to save image

        Returns:
            {'success': bool, 'image_path': str, 'image_bytes': bytes}
        """
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "inputs": prompt,
            "parameters": {
                "num_inference_steps": self.num_inference_steps,
                "guidance_scale": self.guidance_scale,
                "width": width,
                "height": height
            }
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, headers=headers, json=payload,
                                       timeout=aiohttp.ClientTimeout(total=60)) as response:

                    if response.status == 200:
                        image_bytes = await response.read()

                        # Save if path provided
                        if save_path:
                            Path(save_path).write_bytes(image_bytes)
                            self.logger.info(f"✅ Image saved: {save_path}")

                        return {
                            'success': True,
                            'image_path': save_path,
                            'image_bytes': image_bytes,
                            'size_kb': len(image_bytes) / 1024
                        }
                    else:
                        error_text = await response.text()
                        self.logger.error(f"❌ Image generation failed: {response.status} - {error_text}")

                        return {
                            'success': False,
                            'error': error_text,
                            'status': response.status
                        }

        except Exception as e:
            self.logger.error(f"❌ Image generation exception: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def generate_product_image(self, product_title: str, product_description: str,
                                    product_num: int, record_id: str,
                                    storage_manager) -> Dict[str, Any]:
        """
        Generate product image (compatible with existing workflow)

        Args:
            product_title: Product title
            product_description: Product description
            product_num: Product number (1-5)
            record_id: Airtable record ID
            storage_manager: Storage manager for saving files

        Returns:
            Result dictionary with image path
        """
        # Build prompt (similar to current system)
        prompt = f"""Professional product photography: {product_title}.
{product_description}.
Studio lighting, white background, high resolution,
sharp focus, commercial quality."""

        # Generate image
        result = await self.generate_image(prompt, width=1080, height=1920)

        if result['success']:
            # Save using storage manager
            image_path = storage_manager.save_file(
                result['image_bytes'],
                f"product{product_num}_flux.jpg",
                "images",
                record_id
            )

            return {
                'success': True,
                'image_path': image_path,
                'local_path': image_path,
                'product_num': product_num
            }
        else:
            return result

    async def generate_intro_outro_image(self, prompt: str, image_type: str,
                                        record_id: str, storage_manager) -> Dict[str, Any]:
        """
        Generate intro or outro image

        Args:
            prompt: Text prompt
            image_type: 'intro' or 'outro'
            record_id: Airtable record ID
            storage_manager: Storage manager

        Returns:
            Result dictionary
        """
        result = await self.generate_image(prompt, width=1080, height=1920)

        if result['success']:
            image_path = storage_manager.save_file(
                result['image_bytes'],
                f"{image_type}_flux.jpg",
                "images",
                record_id
            )

            return {
                'success': True,
                'image_path': image_path,
                'local_path': image_path,
                'type': image_type
            }
        else:
            return result


# Alias for backward compatibility
HFImageClient = HuggingFaceImageClient
