"""
Airtable Updater SubAgent
===========================
Updates Airtable with workflow results at all phases
Handles: images, scripts, voices, content, video, and publishing URLs
"""
import sys
sys.path.append('/home/claude-workflow')
from agents.base_subagent import BaseSubAgent
from agents.utils.airtable_client import AirtableClient
from typing import Dict, Any

class AirtableUpdaterSubAgent(BaseSubAgent):
    def __init__(self, name: str, config: Dict[str, Any], parent_agent_id: str = None):
        super().__init__(name, config, parent_agent_id)

        # Store Airtable configuration
        self.api_key = config.get('airtable_api_key')
        self.base_id = config.get('airtable_base_id', 'appTtNBJ8dAnjvkPP')
        self.table_id = config.get('airtable_table_id', 'tblhGDEW6eUbmaYZx')

        # Initialize Airtable client
        self.airtable = AirtableClient(self.api_key, self.base_id, self.table_id)

    async def execute_task(self, task: Dict[str, Any]) -> Any:
        """
        Execute Airtable update based on operation type

        Supports:
        - save_images: Phase 7
        - save_scripts: Phase 9
        - save_voices: Phase 11
        - save_content: Phase 13
        - save_video: Phase 15
        - final_update: Phase 17
        """
        operation = task.get('operation', 'final_update')

        if operation == 'save_images':
            return await self._save_images(task)
        elif operation == 'save_scripts':
            return await self._save_scripts(task)
        elif operation == 'save_voices':
            return await self._save_voices(task)
        elif operation == 'save_content':
            return await self._save_content(task)
        elif operation == 'save_video':
            return await self._save_video(task)
        else:  # final_update
            return await self._final_update(task)

    async def _save_images(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 7: Save image paths"""
        self.logger.info("💾 Saving images to Airtable...")

        record_id = task.get('record_id')
        image_paths = task.get('image_paths', [])

        if not record_id:
            raise ValueError("Missing record_id")

        fields = {}

        # Map image paths to Airtable fields
        if len(image_paths) >= 1:
            fields['IntroPhoto'] = image_paths[0] if image_paths[0] else ''
        for i in range(1, min(6, len(image_paths))):
            if image_paths[i]:
                fields[f'ProductNo{i}Photo'] = image_paths[i]
        if len(image_paths) >= 7:
            fields['OutroPhoto'] = image_paths[6] if image_paths[6] else ''

        # Update status
        fields['VideoProductionRDY'] = 'Pending'  # Still in progress

        self.airtable.update_record(record_id, fields)
        self.logger.info(f"✅ Saved {len(image_paths)} images to Airtable")

        return {'record_id': record_id, 'images_saved': len(image_paths)}

    async def _save_scripts(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 9: Save voice scripts"""
        self.logger.info("💾 Saving scripts to Airtable...")

        record_id = task.get('record_id')
        scripts = task.get('scripts', {})

        if not record_id:
            raise ValueError("Missing record_id")

        fields = {
            'IntroHook': scripts.get('intro_script', ''),
            'OutroCallToAction': scripts.get('outro_script', ''),
            'VideoScript': str(scripts)  # Store full script JSON
        }

        self.airtable.update_record(record_id, fields)
        self.logger.info(f"✅ Saved {len(scripts)} scripts to Airtable")

        return {'record_id': record_id, 'scripts_saved': len(scripts)}

    async def _save_voices(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 11: Save voice file paths"""
        self.logger.info("💾 Saving voices to Airtable...")

        record_id = task.get('record_id')
        voice_paths = task.get('voice_paths', {})

        if not record_id:
            raise ValueError("Missing record_id")

        fields = {
            'IntroMp3': voice_paths.get('IntroScript', ''),
            'Product1Mp3': voice_paths.get('Product1Script', ''),
            'Product2Mp3': voice_paths.get('Product2Script', ''),
            'Product3Mp3': voice_paths.get('Product3Script', ''),
            'Product4Mp3': voice_paths.get('Product4Script', ''),
            'Product5Mp3': voice_paths.get('Product5Script', ''),
            'OutroMp3': voice_paths.get('OutroScript', '')
        }

        self.airtable.update_record(record_id, fields)
        self.logger.info(f"✅ Saved {len(voice_paths)} voices to Airtable")

        return {'record_id': record_id, 'voices_saved': len(voice_paths)}

    async def _save_content(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 13: Save platform content"""
        self.logger.info("💾 Saving content to Airtable...")

        record_id = task.get('record_id')
        content = task.get('content', {})

        if not record_id:
            raise ValueError("Missing record_id")

        fields = {
            # YouTube
            'YouTubeTitle': content.get('youtube_title', ''),
            'YouTubeDescription': content.get('youtube_description', ''),
            'YouTubeKeywords': content.get('youtube_tags', ''),

            # WordPress
            'WordPressTitle': content.get('wordpress_title', ''),
            'WordPressContent': content.get('wordpress_content', ''),
            'WordPressSEO': content.get('wordpress_seo', ''),

            # Instagram
            'InstagramTitle': content.get('instagram_title', ''),
            'InstagramCaption': content.get('instagram_caption', ''),
            'InstagramHashtags': content.get('hashtags', ''),

            # TikTok (if available)
            'TikTokTitle': content.get('tiktok_title', ''),
            'TikTokCaption': content.get('tiktok_caption', ''),
            'TikTokHashtags': content.get('tiktok_hashtags', ''),

            # Status fields
            'VideoTitleStatus': 'Ready',
            'VideoDescriptionStatus': 'Ready',
            'ContentValidationStatus': 'Validated'
        }

        self.airtable.update_record(record_id, fields)
        self.logger.info(f"✅ Saved platform content to Airtable ({len(fields)} fields)")

        return {'record_id': record_id, 'content_saved': True}

    async def _save_video(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 15: Save video path"""
        self.logger.info("💾 Saving video to Airtable...")

        record_id = task.get('record_id')
        video_path = task.get('video_path', '')
        video_type = task.get('video_type', 'standard')

        if not record_id:
            raise ValueError("Missing record_id")

        fields = {
            'FinalVideo': video_path,
            'VideoProductionRDY': 'Ready'  # Video is ready!
        }

        self.airtable.update_record(record_id, fields)
        self.logger.info(f"✅ Saved {video_type} video to Airtable")

        return {'record_id': record_id, 'video_saved': True}

    async def _final_update(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 17: Final update with all publishing URLs"""
        self.logger.info("💾 Final Airtable update...")

        params = task.get('params', {})
        record_id = params.get('fetch_title', {}).get('record_id')

        # Collect all URLs from publishing phases
        youtube_url = params.get('publish_youtube', {}).get('youtube_url', '')
        wordpress_url = params.get('publish_wordpress', {}).get('wordpress_url', '')
        instagram_url = params.get('publish_instagram', {}).get('instagram_url', '')
        video_path = params.get('create_video', {}).get('video_path', '')

        fields = {
            'Status': 'Completed',
            'YouTubeURL': youtube_url,
            'WordPressURL': wordpress_url,
            'InstagramURL': instagram_url,
            'FinalVideo': video_path,
            'PlatformReadiness': ['Youtube', 'Instagram', 'Website']  # Mark as ready
        }

        self.airtable.update_record(record_id, fields)
        self.logger.info(f"✅ Final update complete for record {record_id}")

        return {'record_id': record_id, 'updated': True}

    async def validate_input(self, task: Dict[str, Any]) -> Dict[str, Any]:
        params = task.get('params', {})
        if 'fetch_title' not in params:
            return {'valid': False, 'error': 'Missing record_id'}
        return {'valid': True}
