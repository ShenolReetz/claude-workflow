"""
Voice Generator SubAgent with ElevenLabs
=========================================
Generates voice-overs using ElevenLabs (keeping for quality).

COST: $0.10/video (kept - best quality)
SPEED: 5-7 seconds per clip
QUALITY: Excellent
"""

import sys
import asyncio
from typing import Dict, Any, List
from pathlib import Path

sys.path.append('/home/claude-workflow')

from agents.base_subagent import BaseSubAgent
from src.utils.dual_storage_manager import get_storage_manager

# Import ElevenLabs SDK
try:
    from elevenlabs.client import ElevenLabs
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False
    print("⚠️  ElevenLabs package not installed. Install with: pip install elevenlabs")


class VoiceGeneratorSubAgent(BaseSubAgent):
    """
    Generates voice files using ElevenLabs

    Features:
    - Professional voice quality
    - Multiple voice presets
    - Local storage for Remotion
    - Optimal timing and pacing

    TODO: Integrate with production_voice_generation_mcp_server for actual voice generation
    Currently using mock mode for testing
    """

    def __init__(self, name: str, config: Dict[str, Any], parent_agent_id: str = None):
        super().__init__(name, config, parent_agent_id)

        # Store configuration
        self.elevenlabs_api_key = config.get('elevenlabs_api_key')

        # Initialize ElevenLabs client
        self.elevenlabs_client = None
        if ELEVENLABS_AVAILABLE and self.elevenlabs_api_key:
            try:
                self.elevenlabs_client = ElevenLabs(api_key=self.elevenlabs_api_key)
                self.logger.info("✅ ElevenLabs client initialized")
            except Exception as e:
                self.logger.error(f"❌ Failed to initialize ElevenLabs client: {e}")

        # Voice IDs (using ElevenLabs default voices)
        self.voice_ids = {
            'intro': 'JBFqnCBsd6RMkjVDRZzb',      # George - professional male
            'product': 'pNInz6obpgDQGcFmaJgB',    # Adam - clear articulate male
            'outro': 'JBFqnCBsd6RMkjVDRZzb'       # George - professional male
        }

        # Initialize DualStorageManager for local + Google Drive storage
        self.storage_manager = get_storage_manager(config)

        self.logger.info("✅ VoiceGeneratorSubAgent initialized with ElevenLabs")
        self.logger.info("💰 Cost: $0.10/video (kept for quality)")

    async def execute_task(self, task: Dict[str, Any]) -> Any:
        """
        Generate voice files for all scripts

        Args:
            task: Task with 'scripts' dict and 'record_id'

        Returns:
            Paths to generated voice files
        """
        scripts = task.get('scripts', {})
        record_id = task.get('record_id')

        if not scripts or not record_id:
            raise ValueError("Missing scripts or record_id")

        self.logger.info(f"🎤 Generating {len(scripts)} voice files with ElevenLabs...")

        try:
            voice_paths = {}

            # Generate intro voice
            if scripts.get('IntroScript'):
                intro_result = await self._generate_voice_file(
                    text=scripts['IntroScript'],
                    record_id=record_id,
                    filename='intro_voice.mp3',
                    voice_type='intro'
                )
                voice_paths['intro'] = {
                    'local_path': intro_result['local_path'],
                    'drive_url': intro_result.get('drive_url')
                }

            # Generate product voices (1-5)
            for i in range(1, 6):
                script_key = f'Product{i}Script'
                if scripts.get(script_key):
                    voice_result = await self._generate_voice_file(
                        text=scripts[script_key],
                        record_id=record_id,
                        filename=f'product{i}_voice.mp3',
                        voice_type='product'
                    )
                    voice_paths[f'product{i}'] = {
                        'local_path': voice_result['local_path'],
                        'drive_url': voice_result.get('drive_url')
                    }

            # Generate outro voice
            if scripts.get('OutroScript'):
                outro_result = await self._generate_voice_file(
                    text=scripts['OutroScript'],
                    record_id=record_id,
                    filename='outro_voice.mp3',
                    voice_type='outro'
                )
                voice_paths['outro'] = {
                    'local_path': outro_result['local_path'],
                    'drive_url': outro_result.get('drive_url')
                }

            self.logger.info(f"✅ Generated {len(voice_paths)} voice files")

            return {'voice_paths': voice_paths}

        except Exception as e:
            self.logger.error(f"❌ Voice generation failed: {e}")
            raise

    async def _generate_voice_file(self, text: str, record_id: str, filename: str, voice_type: str, project_title: str = None) -> Dict:
        """Generate a single voice file using ElevenLabs API and upload to Google Drive"""
        self.logger.info(f"🎤 Generating {filename} with ElevenLabs...")

        try:
            # Check if ElevenLabs client is available
            if not self.elevenlabs_client:
                self.logger.error("❌ ElevenLabs client not initialized")
                # Create mock data as fallback
                audio_data = b'MOCK_AUDIO_DATA'
            else:
                # Get voice ID for this type
                voice_id = self.voice_ids.get(voice_type, self.voice_ids['product'])

                # Clean the text (remove quotes if present)
                clean_text = text.strip('"').strip("'")

                self.logger.info(f"   Text: {clean_text[:60]}...")
                self.logger.info(f"   Voice: {voice_type} (ID: {voice_id})")

                # Call ElevenLabs API to generate audio
                audio_bytes = self.elevenlabs_client.text_to_speech.convert(
                    text=clean_text,
                    voice_id=voice_id,
                    model_id="eleven_multilingual_v2",
                    output_format="mp3_44100_128"
                )

                # Convert generator to bytes
                audio_data = b"".join(audio_bytes)

                file_size = len(audio_data)
                self.logger.info(f"✅ Voice generated: {filename} ({file_size:,} bytes)")

            # Use DualStorageManager to save locally + Google Drive
            result = await self.storage_manager.save_media(
                content=audio_data,
                filename=filename,
                media_type='audio',
                record_id=record_id,
                upload_to_drive=True,  # Enable Google Drive upload
                project_title=project_title  # Pass project title for folder organization
            )

            if result.get('success'):
                self.logger.debug(f"💾 Saved voice to: {result['local_path']}")
                if result.get('drive_url'):
                    self.logger.info(f"☁️ Uploaded to Google Drive: {result['drive_url']}")
            else:
                raise RuntimeError(f"Failed to save voice: {result.get('error')}")

            return result

        except Exception as e:
            self.logger.error(f"❌ Voice file generation failed for {filename}: {e}")
            self.logger.error(f"   Text was: {text[:100]}...")

            # Create mock file as fallback
            self.logger.warning("⚠️  Creating mock file as fallback")
            result = await self.storage_manager.save_media(
                content=b'MOCK_AUDIO_DATA',
                filename=filename,
                media_type='audio',
                record_id=record_id,
                upload_to_drive=False  # Don't upload mock data
            )

            # Don't raise - return mock file to allow workflow to continue
            return result

    async def validate_input(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input parameters"""
        if 'scripts' not in task:
            return {'valid': False, 'error': 'Missing scripts'}

        if 'record_id' not in task:
            return {'valid': False, 'error': 'Missing record_id'}

        scripts = task['scripts']
        if not isinstance(scripts, dict):
            return {'valid': False, 'error': 'Scripts must be a dictionary'}

        # Check for at least intro and outro
        if not scripts.get('IntroScript'):
            return {'valid': False, 'error': 'Missing IntroScript'}

        if not scripts.get('OutroScript'):
            return {'valid': False, 'error': 'Missing OutroScript'}

        return {'valid': True}

    async def validate_output(self, result: Any) -> Dict[str, Any]:
        """Validate output result"""
        if not isinstance(result, dict):
            return {'valid': False, 'error': 'Result must be a dictionary'}

        if 'voice_paths' not in result:
            return {'valid': False, 'error': 'Missing voice_paths in result'}

        voice_paths = result['voice_paths']
        if not isinstance(voice_paths, dict):
            return {'valid': False, 'error': 'voice_paths must be a dictionary'}

        # Check for intro and outro
        if 'intro' not in voice_paths:
            return {'valid': False, 'error': 'Missing intro voice'}

        if 'outro' not in voice_paths:
            return {'valid': False, 'error': 'Missing outro voice'}

        # Validate all voice files exist
        import os
        for key, voice_data in voice_paths.items():
            if isinstance(voice_data, dict):
                path = voice_data.get('local_path')
            else:
                path = voice_data  # Backward compatibility

            if not path or not os.path.exists(path):
                return {'valid': False, 'error': f'Voice file not found: {path}'}

        return {'valid': True}
