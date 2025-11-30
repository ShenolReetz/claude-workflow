"""
Standard Video SubAgent
========================
Renders standard videos using Remotion.
"""

import sys
import asyncio
from typing import Dict, Any

sys.path.append('/home/claude-workflow')

from agents.base_subagent import BaseSubAgent
from src.mcp.production_remotion_video_generator_strict import production_run_video_creation


class StandardVideoSubAgent(BaseSubAgent):
    """
    Renders standard product videos using Remotion

    Features:
    - 7-scene structure
    - Background music
    - 45-60 second duration
    - 1080x1920 vertical format
    """

    def __init__(self, name: str, config: Dict[str, Any], parent_agent_id: str = None):
        super().__init__(name, config, parent_agent_id)
        self.logger.info("✅ StandardVideoSubAgent initialized")

    async def execute_task(self, task: Dict[str, Any]) -> Any:
        """
        Render standard video

        Args:
            task: Task with workflow data (images, voices, product data)

        Returns:
            Path to rendered video
        """
        self.logger.info("🎬 Rendering standard video with Remotion...")

        try:
            # Extract required data from task params
            params = task.get('params', {})

            # Prepare video data
            video_data = self._prepare_video_data(params)

            # Render video using existing Remotion function
            result = await production_run_video_creation(video_data)

            self.logger.info(f"✅ Video rendered: {result.get('video_path')}")

            return {
                'video_path': result.get('video_path'),
                'duration': result.get('duration', 60),
                'resolution': '1080x1920'
            }

        except Exception as e:
            self.logger.error(f"❌ Standard video rendering failed: {e}")
            raise

    def _prepare_video_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for Remotion rendering"""
        # Extract data from workflow params
        images = params.get('generate_images', {}).get('image_paths', [])
        voices = params.get('generate_voices', {}).get('voice_paths', {})
        products = params.get('validate_products', {}).get('valid_products', [])
        record_id = params.get('fetch_title', {}).get('record_id')

        return {
            'record_id': record_id,
            'images': images,
            'voices': voices,
            'products': products
        }

    async def validate_input(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input parameters"""
        params = task.get('params', {})

        if not params:
            return {'valid': False, 'error': 'Missing params'}

        # Check for images
        if 'generate_images' not in params:
            return {'valid': False, 'error': 'Missing generate_images data'}

        # Check for voices
        if 'generate_voices' not in params:
            return {'valid': False, 'error': 'Missing generate_voices data'}

        return {'valid': True}

    async def validate_output(self, result: Any) -> Dict[str, Any]:
        """Validate output result"""
        if not isinstance(result, dict):
            return {'valid': False, 'error': 'Result must be a dictionary'}

        if 'video_path' not in result:
            return {'valid': False, 'error': 'Missing video_path'}

        # Check if video file exists
        import os
        video_path = result['video_path']
        if not os.path.exists(video_path):
            return {'valid': False, 'error': f'Video file not found: {video_path}'}

        return {'valid': True}
