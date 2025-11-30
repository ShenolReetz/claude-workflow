"""Airtable Updater SubAgent - Updates Airtable with publishing results"""
import sys
sys.path.append('/home/claude-workflow')
from agents.base_subagent import BaseSubAgent
from mcp_servers.production_airtable_server import ProductionAirtableMCPServer
from typing import Dict, Any

class AirtableUpdaterSubAgent(BaseSubAgent):
    def __init__(self, name: str, config: Dict[str, Any], parent_agent_id: str = None):
        super().__init__(name, config, parent_agent_id)
        self.airtable = ProductionAirtableMCPServer(
            api_key=config.get('airtable_api_key'),
            base_id=config.get('airtable_base_id'),
            table_id=config.get('airtable_table_id')
        )

    async def execute_task(self, task: Dict[str, Any]) -> Any:
        self.logger.info("💾 Updating Airtable...")
        params = task.get('params', {})
        record_id = params.get('fetch_title', {}).get('record_id')

        # Collect all URLs from publishing phases
        youtube_url = params.get('publish_youtube', {}).get('youtube_url', '')
        wordpress_url = params.get('publish_wordpress', {}).get('wordpress_url', '')
        instagram_url = params.get('publish_instagram', {}).get('instagram_url', '')
        video_path = params.get('create_video', {}).get('video_path', '')

        # Update Airtable record
        await self.airtable.update_record(record_id, {
            'Status': 'Published',
            'YouTubeURL': youtube_url,
            'WordPressURL': wordpress_url,
            'InstagramURL': instagram_url,
            'FinalVideo': video_path
        })

        return {'record_id': record_id}

    async def validate_input(self, task: Dict[str, Any]) -> Dict[str, Any]:
        params = task.get('params', {})
        if 'fetch_title' not in params:
            return {'valid': False, 'error': 'Missing record_id'}
        return {'valid': True}
