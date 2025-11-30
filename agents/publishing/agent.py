"""
Publishing Agent
=================
Main agent that orchestrates multi-platform publishing.
"""

import asyncio
import logging
from typing import Dict, Any, List
import sys

sys.path.append('/home/claude-workflow')

from agents.base_agent import BaseAgent
from .youtube_publisher_subagent import YouTubePublisherSubAgent
from .wordpress_publisher_subagent import WordPressPublisherSubAgent
from .instagram_publisher_subagent import InstagramPublisherSubAgent
from .airtable_updater_subagent import AirtableUpdaterSubAgent


class PublishingAgent(BaseAgent):
    """
    Manages publishing to all platforms:
    - YouTube (with OAuth)
    - WordPress (with media upload)
    - Instagram Reels
    - Airtable status updates

    Features parallel publishing for speed!
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__("publishing", config)

        # Initialize sub-agents
        self.sub_agents = [
            YouTubePublisherSubAgent("youtube_publisher", config, self.agent_id),
            WordPressPublisherSubAgent("wordpress_publisher", config, self.agent_id),
            InstagramPublisherSubAgent("instagram_publisher", config, self.agent_id),
            AirtableUpdaterSubAgent("airtable_updater", config, self.agent_id),
        ]

        # Platform settings
        self.enabled_platforms = config.get('enabled_platforms', ['youtube', 'wordpress', 'instagram'])
        self.parallel_publishing = config.get('parallel_publishing', True)

        self.logger.info(f"✅ PublishingAgent initialized with {len(self.sub_agents)} sub-agents")
        self.logger.info(f"🚀 Parallel publishing: {'enabled' if self.parallel_publishing else 'disabled'}")

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute publishing task

        Args:
            task: Task parameters with 'phase' key

        Returns:
            Publishing results
        """
        phase = task.get('phase', '')
        self.logger.info(f"📤 Executing publishing phase: {phase}")

        try:
            if phase == 'publish_youtube':
                return await self._publish_to_youtube(task)

            elif phase == 'publish_wordpress':
                return await self._publish_to_wordpress(task)

            elif phase == 'publish_instagram':
                return await self._publish_to_instagram(task)

            elif phase == 'update_airtable_status':
                return await self._update_airtable_status(task)

            elif phase == 'publish_all':
                # Publish to all platforms in parallel
                return await self._publish_all_platforms(task)

            else:
                raise ValueError(f"Unknown phase: {phase}")

        except Exception as e:
            self.logger.error(f"❌ Publishing failed: {e}")
            raise

    async def _publish_to_youtube(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Publish video to YouTube"""
        self.logger.info("📤 Publishing to YouTube...")

        result = await self.delegate_to_subagent('YouTubePublisherSubAgent', task)

        if not result['success']:
            raise RuntimeError(f"YouTube publishing failed: {result.get('error')}")

        return {
            'youtube_url': result['result']['video_url'],
            'youtube_id': result['result']['video_id'],
            'status': 'published'
        }

    async def _publish_to_wordpress(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Publish post to WordPress"""
        self.logger.info("📤 Publishing to WordPress...")

        result = await self.delegate_to_subagent('WordPressPublisherSubAgent', task)

        if not result['success']:
            raise RuntimeError(f"WordPress publishing failed: {result.get('error')}")

        return {
            'wordpress_url': result['result']['post_url'],
            'wordpress_id': result['result']['post_id'],
            'status': 'published'
        }

    async def _publish_to_instagram(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Publish video to Instagram"""
        self.logger.info("📤 Publishing to Instagram...")

        result = await self.delegate_to_subagent('InstagramPublisherSubAgent', task)

        if not result['success']:
            raise RuntimeError(f"Instagram publishing failed: {result.get('error')}")

        return {
            'instagram_url': result['result'].get('media_url', ''),
            'instagram_id': result['result']['media_id'],
            'status': 'published'
        }

    async def _update_airtable_status(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Update Airtable with all publishing URLs"""
        self.logger.info("💾 Updating Airtable with publishing results...")

        result = await self.delegate_to_subagent('AirtableUpdaterSubAgent', task)

        if not result['success']:
            raise RuntimeError(f"Airtable update failed: {result.get('error')}")

        return {
            'record_id': result['result']['record_id'],
            'status': 'updated'
        }

    async def _publish_all_platforms(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Publish to all enabled platforms in parallel"""
        self.logger.info(f"🚀 Publishing to {len(self.enabled_platforms)} platforms in parallel...")

        if self.parallel_publishing:
            # Publish to all platforms concurrently
            publishing_tasks = []

            if 'youtube' in self.enabled_platforms:
                publishing_tasks.append(self._publish_to_youtube(task))

            if 'wordpress' in self.enabled_platforms:
                publishing_tasks.append(self._publish_to_wordpress(task))

            if 'instagram' in self.enabled_platforms:
                publishing_tasks.append(self._publish_to_instagram(task))

            # Execute all in parallel
            results = await asyncio.gather(*publishing_tasks, return_exceptions=True)

            # Collect results
            publishing_results = {
                'youtube_url': '',
                'wordpress_url': '',
                'instagram_url': '',
                'errors': []
            }

            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    platform = self.enabled_platforms[i]
                    self.logger.error(f"❌ {platform} failed: {result}")
                    publishing_results['errors'].append(f"{platform}: {str(result)}")
                elif isinstance(result, dict):
                    publishing_results.update(result)

            return publishing_results

        else:
            # Sequential publishing
            results = {}

            if 'youtube' in self.enabled_platforms:
                results.update(await self._publish_to_youtube(task))

            if 'wordpress' in self.enabled_platforms:
                results.update(await self._publish_to_wordpress(task))

            if 'instagram' in self.enabled_platforms:
                results.update(await self._publish_to_instagram(task))

            return results

    def get_capabilities(self) -> List[str]:
        """Return list of capabilities"""
        return [
            'publish_youtube',
            'publish_wordpress',
            'publish_instagram',
            'update_airtable_status',
            'publish_all'
        ]
