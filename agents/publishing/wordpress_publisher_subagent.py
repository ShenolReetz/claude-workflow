"""WordPress Publisher SubAgent - Wraps existing WordPress publishing code"""
import sys
sys.path.append('/home/claude-workflow')
from agents.base_subagent import BaseSubAgent
from src.mcp.production_wordpress_local_media import production_publish_to_wordpress_local
from typing import Dict, Any

class WordPressPublisherSubAgent(BaseSubAgent):
    async def execute_task(self, task: Dict[str, Any]) -> Any:
        self.logger.info("📤 Publishing to WordPress...")
        params = task.get('params', {})
        video_path = params.get('create_video', {}).get('video_path')
        content = params.get('generate_content', {})
        products = params.get('validate_products', {}).get('valid_products', [])

        result = await production_publish_to_wordpress_local({
            'video_path': video_path,
            'title': content.get('wordpress_title', ''),
            'content': content.get('wordpress_content', ''),
            'products': products
        })

        return {'post_url': result.get('post_url'), 'post_id': result.get('post_id')}

    async def validate_input(self, task: Dict[str, Any]) -> Dict[str, Any]:
        params = task.get('params', {})
        if 'create_video' not in params:
            return {'valid': False, 'error': 'Missing video data'}
        return {'valid': True}
