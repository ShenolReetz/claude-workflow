"""
Content Generation Agent
=========================
Main agent that orchestrates all content generation using HuggingFace models.
"""

import asyncio
import logging
from typing import Dict, Any, List
import sys

sys.path.append('/home/claude-workflow')

from agents.base_agent import BaseAgent
from .image_generator_subagent import ImageGeneratorSubAgent
from .text_generator_subagent import TextGeneratorSubAgent
from .voice_generator_subagent import VoiceGeneratorSubAgent
from .content_validator_subagent import ContentValidatorSubAgent


class ContentGenerationAgent(BaseAgent):
    """
    Manages all content generation with HuggingFace integration:
    - Image generation (HF FLUX.1-schnell) - COST SAVINGS!
    - Text generation (HF Llama-3.1-8B) - COST SAVINGS!
    - Voice generation (ElevenLabs - kept for quality)
    - Content validation
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__("content_generation", config)

        # Initialize sub-agents
        self.sub_agents = [
            ImageGeneratorSubAgent("image_generator", config, self.agent_id),
            TextGeneratorSubAgent("text_generator", config, self.agent_id),
            VoiceGeneratorSubAgent("voice_generator", config, self.agent_id),
            ContentValidatorSubAgent("content_validator", config, self.agent_id),
        ]

        self.logger.info(f"✅ ContentGenerationAgent initialized with {len(self.sub_agents)} sub-agents")
        self.logger.info("🎯 Using HuggingFace for images and text - COST SAVINGS ACTIVE!")

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute content generation task

        Args:
            task: Task parameters with 'phase' key

        Returns:
            Generated content
        """
        phase = task.get('phase', '')
        self.logger.info(f"🎨 Executing content generation phase: {phase}")

        try:
            if phase == 'generate_images':
                return await self._generate_images(task)

            elif phase == 'generate_content':
                return await self._generate_content(task)

            elif phase == 'generate_scripts':
                return await self._generate_scripts(task)

            elif phase == 'generate_voices':
                return await self._generate_voices(task)

            elif phase == 'validate_content':
                return await self._validate_content(task)

            else:
                raise ValueError(f"Unknown phase: {phase}")

        except Exception as e:
            self.logger.error(f"❌ Content generation failed: {e}")
            raise

    async def _generate_images(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Generate product images using HuggingFace FLUX"""
        self.logger.info("🖼️  Generating images with HuggingFace FLUX.1-schnell...")

        products = task.get('params', {}).get('validate_products', {}).get('valid_products', [])
        if not products:
            raise ValueError("No products provided for image generation")

        # Get record_id from task
        record_id = task.get('record_id', task.get('params', {}).get('record_id', 'unknown'))

        # Generate images for each product (max 5)
        image_tasks = []
        for i, product in enumerate(products[:5], 1):
            img_task = {
                **task,
                'product': product,
                'product_index': i,
                'record_id': record_id
            }
            image_tasks.append(self.delegate_to_subagent('ImageGeneratorSubAgent', img_task))

        # Generate all images in parallel
        results = await asyncio.gather(*image_tasks, return_exceptions=True)

        # Collect successful results
        image_paths = []
        for i, result in enumerate(results, 1):
            if isinstance(result, Exception):
                self.logger.error(f"❌ Image {i} failed with exception: {result}")
                image_paths.append(None)
            elif not isinstance(result, dict):
                self.logger.error(f"❌ Image {i} returned invalid type: {type(result)}")
                image_paths.append(None)
            elif not result.get('success', False):
                error = result.get('error', 'Unknown error')
                self.logger.error(f"❌ Image {i} failed: success=False, error={error}")
                image_paths.append(None)
            else:
                # Success case
                result_data = result.get('result', {})
                image_path = result_data.get('image_path')
                drive_url = result_data.get('drive_url')
                if image_path:
                    self.logger.info(f"✅ Image {i} path collected: {image_path}")
                    if drive_url:
                        self.logger.info(f"☁️ Image {i} Google Drive: {drive_url}")
                    # Store both local path and drive URL
                    image_paths.append({
                        'local_path': image_path,
                        'drive_url': drive_url
                    })
                else:
                    self.logger.error(f"❌ Image {i}: success=True but no image_path in result")
                    image_paths.append(None)

        return {
            'image_paths': image_paths,
            'count': len([p for p in image_paths if p is not None]),
            'status': 'images_generated'
        }

    async def _generate_content(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content metadata and descriptions"""
        self.logger.info("📝 Generating content metadata...")

        products = task.get('params', {}).get('validate_products', {}).get('valid_products', [])
        category = task.get('params', {}).get('extract_category', {}).get('category', 'Electronics')

        # Generate platform-specific content
        content_task = {
            **task,
            'products': products,
            'category': category
        }

        result = await self.delegate_to_subagent('TextGeneratorSubAgent', content_task)

        if not result['success']:
            raise RuntimeError(f"Failed to generate content: {result.get('error')}")

        return {
            'youtube_title': result['result']['youtube_title'],
            'youtube_description': result['result']['youtube_description'],
            'youtube_tags': result['result']['youtube_tags'],
            'wordpress_title': result['result']['wordpress_title'],
            'wordpress_content': result['result']['wordpress_content'],
            'instagram_caption': result['result']['instagram_caption'],
            'hashtags': result['result']['hashtags'],
            'status': 'content_generated'
        }

    async def _generate_scripts(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Generate voice scripts using HuggingFace Llama"""
        self.logger.info("📜 Generating voice scripts with HuggingFace Llama-3.1-8B...")

        products = task.get('params', {}).get('validate_products', {}).get('valid_products', [])
        if not products:
            raise ValueError("No products provided for script generation")

        # Generate scripts for intro, products, and outro
        script_task = {
            **task,
            'products': products,
            'operation': 'generate_scripts'
        }

        result = await self.delegate_to_subagent('TextGeneratorSubAgent', script_task)

        if not result['success']:
            raise RuntimeError(f"Failed to generate scripts: {result.get('error')}")

        return {
            'intro_script': result['result']['intro_script'],
            'product1_script': result['result'].get('product1_script', ''),
            'product2_script': result['result'].get('product2_script', ''),
            'product3_script': result['result'].get('product3_script', ''),
            'product4_script': result['result'].get('product4_script', ''),
            'product5_script': result['result'].get('product5_script', ''),
            'outro_script': result['result']['outro_script'],
            'status': 'scripts_generated'
        }

    async def _generate_voices(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Generate voice files using ElevenLabs"""
        self.logger.info("🎤 Generating voices with ElevenLabs...")

        scripts_data = task.get('params', {}).get('generate_scripts', {})
        record_id = task.get('params', {}).get('fetch_title', {}).get('record_id')

        # Generate voices for all scripts
        voice_task = {
            **task,
            'record_id': record_id,
            'scripts': {
                'IntroScript': scripts_data.get('intro_script', ''),
                'Product1Script': scripts_data.get('product1_script', ''),
                'Product2Script': scripts_data.get('product2_script', ''),
                'Product3Script': scripts_data.get('product3_script', ''),
                'Product4Script': scripts_data.get('product4_script', ''),
                'Product5Script': scripts_data.get('product5_script', ''),
                'OutroScript': scripts_data.get('outro_script', ''),
            }
        }

        result = await self.delegate_to_subagent('VoiceGeneratorSubAgent', voice_task)

        if not result['success']:
            raise RuntimeError(f"Failed to generate voices: {result.get('error')}")

        return {
            'voice_paths': result['result']['voice_paths'],
            'count': len(result['result']['voice_paths']),
            'status': 'voices_generated'
        }

    async def _validate_content(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Validate all generated content"""
        self.logger.info("✅ Validating generated content...")

        # Collect all generated content
        content_data = {
            'images': task.get('params', {}).get('generate_images', {}).get('image_paths', []),
            'scripts': task.get('params', {}).get('generate_scripts', {}),
            'voices': task.get('params', {}).get('generate_voices', {}).get('voice_paths', []),
        }

        validate_task = {
            **task,
            'content_data': content_data
        }

        result = await self.delegate_to_subagent('ContentValidatorSubAgent', validate_task)

        if not result['success']:
            raise RuntimeError(f"Content validation failed: {result.get('error')}")

        return {
            'validation_passed': result['result']['passed'],
            'validation_report': result['result']['report'],
            'status': 'content_validated'
        }

    def get_capabilities(self) -> List[str]:
        """Return list of capabilities"""
        return [
            'generate_images',      # HuggingFace FLUX
            'generate_content',     # HuggingFace Llama
            'generate_scripts',     # HuggingFace Llama
            'generate_voices',      # ElevenLabs
            'validate_content'
        ]
