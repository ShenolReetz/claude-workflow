"""Instagram Publisher SubAgent - Wraps existing Instagram Reels upload code"""
import sys
sys.path.append('/home/claude-workflow')
from agents.base_subagent import BaseSubAgent
from src.mcp.production_instagram_reels_upload import production_upload_to_instagram
from typing import Dict, Any

class InstagramPublisherSubAgent(BaseSubAgent):
    async def execute_task(self, task: Dict[str, Any]) -> Any:
        self.logger.info("📤 Publishing to Instagram...")
        params = task.get('params', {})
        video_path = params.get('create_video', {}).get('video_path')
        content = params.get('generate_content', {})

        result = await production_upload_to_instagram({
            'video_path': video_path,
            'caption': content.get('instagram_caption', ''),
            'hashtags': content.get('hashtags', [])
        })

        return {'media_url': result.get('media_url', ''), 'media_id': result.get('media_id')}

    async def validate_input(self, task: Dict[str, Any]) -> Dict[str, Any]:
        params = task.get('params', {})
        if 'create_video' not in params:
            return {'valid': False, 'error': 'Missing video data'}
        return {'valid': True}
