"""
WOW Video SubAgent
==================
Renders WOW videos with premium effects using Remotion.
"""

import sys
import asyncio
from typing import Dict, Any

sys.path.append('/home/claude-workflow')

from agents.base_subagent import BaseSubAgent
from src.mcp.production_wow_video_generator import production_generate_wow_video
from src.utils.dual_storage_manager import get_storage_manager


class WowVideoSubAgent(BaseSubAgent):
    """
    Renders WOW product videos with effects

    Features:
    - Particle effects
    - 3D transitions
    - Review card animations
    - Premium visual effects
    - 60-75 second duration
    - 40% higher engagement
    """

    def __init__(self, name: str, config: Dict[str, Any], parent_agent_id: str = None):
        super().__init__(name, config, parent_agent_id)

        # Initialize DualStorageManager for local + Google Drive storage
        self.storage_manager = get_storage_manager(config)

        self.logger.info("✅ WowVideoSubAgent initialized")
        self.logger.info("🎨 +40% engagement with WOW effects!")

    async def execute_task(self, task: Dict[str, Any]) -> Any:
        """
        Render WOW video with effects

        Args:
            task: Task with workflow data (images, voices, product data)

        Returns:
            Path to rendered video
        """
        self.logger.info("🎬 Rendering WOW video with effects...")

        try:
            # Extract required data from task params
            params = task.get('params', {})

            # Prepare video data
            video_data = self._prepare_video_data(params)

            # DEBUG: Log what data is being passed to video generator
            self.logger.info(f"🔍 DEBUG: video_data keys = {list(video_data.keys())}")
            self.logger.info(f"🔍 DEBUG: video_data['images'] = {video_data.get('images', [])}")
            self.logger.info(f"🔍 DEBUG: video_data type = {type(video_data)}")

            # Render video using existing WOW video function
            result = await production_generate_wow_video(video_data, self.config)

            video_path = result.get('video_path')
            self.logger.info(f"✅ WOW video rendered: {video_path}")

            # Upload video to Google Drive
            drive_url = None
            if video_path:
                try:
                    # Read video file
                    with open(video_path, 'rb') as f:
                        video_data_bytes = f.read()

                    # Get record_id and project_title from task
                    record_id = task.get('record_id', params.get('record_id', 'unknown'))
                    project_title = task.get('project_title', params.get('project_title'))

                    # Upload to Google Drive
                    upload_result = await self.storage_manager.save_media(
                        content=video_data_bytes,
                        filename='final_video.mp4',
                        media_type='video',
                        record_id=record_id,
                        upload_to_drive=True,
                        project_title=project_title
                    )

                    if upload_result.get('success') and upload_result.get('drive_url'):
                        drive_url = upload_result['drive_url']
                        self.logger.info(f"☁️ Video uploaded to Google Drive: {drive_url}")
                    else:
                        self.logger.warning(f"⚠️ Google Drive upload failed: {upload_result.get('error', 'Unknown error')}")
                except Exception as upload_error:
                    self.logger.warning(f"⚠️ Google Drive upload failed: {upload_error}")

            return {
                'video_path': video_path,
                'drive_url': drive_url,
                'duration': result.get('duration', 70),
                'resolution': '1080x1920',
                'effects': 'enabled'
            }

        except Exception as e:
            self.logger.error(f"❌ WOW video rendering failed: {e}")
            raise

    def _prepare_video_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for WOW video rendering"""
        # Extract data from workflow params
        images_data = params.get('generate_images', {}).get('image_paths', [])
        voices_data = params.get('generate_voices', {}).get('voice_paths', {})
        products = params.get('validate_products', {}).get('valid_products', [])
        record_id = params.get('fetch_title', {}).get('record_id')

        # Extract local paths from image dicts (new structure with drive_url)
        import os
        valid_images = []
        for i, img_item in enumerate(images_data, 1):
            # Handle both new dict structure and old string structure
            if isinstance(img_item, dict):
                img_path = img_item.get('local_path')
            else:
                img_path = img_item

            if img_path and os.path.exists(img_path):
                self.logger.info(f"✅ Image {i} validated: {img_path}")
                valid_images.append(img_path)
            else:
                self.logger.warning(f"⚠️  Image {i} missing or None: {img_path}")
                # Fallback to Amazon product image if available
                if i <= len(products):
                    amazon_img = products[i-1].get('image_url', '')
                    if amazon_img and ('amazon' in amazon_img.lower() or 'media-amazon' in amazon_img.lower()):
                        self.logger.info(f"   Fallback to Amazon image: {amazon_img[:50]}...")
                        valid_images.append(amazon_img)
                    else:
                        valid_images.append(None)
                else:
                    valid_images.append(None)

        # Extract local paths from voice dicts (new structure with drive_url)
        voice_local_paths = {}
        for voice_key, voice_item in voices_data.items():
            # Handle both new dict structure and old string structure
            if isinstance(voice_item, dict):
                voice_local_paths[voice_key] = voice_item.get('local_path')
            else:
                voice_local_paths[voice_key] = voice_item

        self.logger.info(f"📊 Video data prepared: {len(valid_images)} images, {len(voice_local_paths)} voices, {len(products)} products")

        return {
            'record_id': record_id,
            'images': valid_images,
            'voices': voice_local_paths,
            'products': products,
            'effects_enabled': True
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
