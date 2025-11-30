"""YouTube Publisher SubAgent - Wraps existing YouTube upload code"""
import sys
sys.path.append('/home/claude-workflow')
from agents.base_subagent import BaseSubAgent
from src.mcp.production_youtube_local_upload import production_upload_to_youtube_local
from typing import Dict, Any

class YouTubePublisherSubAgent(BaseSubAgent):
    async def execute_task(self, task: Dict[str, Any]) -> Any:
        self.logger.info("📤 Publishing to YouTube...")
        params = task.get('params', {})
        video_path = params.get('create_video', {}).get('video_path')
        content = params.get('generate_content', {})

        result = await production_upload_to_youtube_local({
            'video_path': video_path,
            'title': content.get('youtube_title', ''),
            'description': content.get('youtube_description', ''),
            'tags': content.get('youtube_tags', [])
        })

        return {'video_url': result.get('video_url'), 'video_id': result.get('video_id')}

    async def validate_input(self, task: Dict[str, Any]) -> Dict[str, Any]:
        params = task.get('params', {})
        if 'create_video' not in params:
            return {'valid': False, 'error': 'Missing video data'}
        return {'valid': True}
