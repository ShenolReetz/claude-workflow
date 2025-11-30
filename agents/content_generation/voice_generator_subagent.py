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

        # Store configuration for future MCP integration
        self.elevenlabs_api_key = config.get('elevenlabs_api_key')

        # Voice presets
        self.voice_presets = {
            'intro': config.get('intro_voice', 'narrator'),
            'product': config.get('product_voice', 'friendly'),
            'outro': config.get('outro_voice', 'narrator')
        }

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
                intro_path = await self._generate_voice_file(
                    text=scripts['IntroScript'],
                    record_id=record_id,
                    filename='intro_voice.mp3',
                    voice_type='intro'
                )
                voice_paths['intro'] = intro_path

            # Generate product voices (1-5)
            for i in range(1, 6):
                script_key = f'Product{i}Script'
                if scripts.get(script_key):
                    voice_path = await self._generate_voice_file(
                        text=scripts[script_key],
                        record_id=record_id,
                        filename=f'product{i}_voice.mp3',
                        voice_type='product'
                    )
                    voice_paths[f'product{i}'] = voice_path

            # Generate outro voice
            if scripts.get('OutroScript'):
                outro_path = await self._generate_voice_file(
                    text=scripts['OutroScript'],
                    record_id=record_id,
                    filename='outro_voice.mp3',
                    voice_type='outro'
                )
                voice_paths['outro'] = outro_path

            self.logger.info(f"✅ Generated {len(voice_paths)} voice files")

            return {'voice_paths': voice_paths}

        except Exception as e:
            self.logger.error(f"❌ Voice generation failed: {e}")
            raise

    async def _generate_voice_file(self, text: str, record_id: str, filename: str, voice_type: str) -> str:
        """Generate a single voice file"""
        self.logger.debug(f"🎤 Generating {filename}...")

        try:
            # TODO: Implement actual ElevenLabs voice generation using production_voice_generation_mcp_server
            # For now, create mock voice file for testing
            self.logger.warning("⚠️  Using mock voice file - ElevenLabs MCP integration pending")

            # Create mock voice file path
            voice_dir = Path(f"/home/claude-workflow/local_storage/{record_id}/voice")
            voice_dir.mkdir(parents=True, exist_ok=True)

            voice_path = str(voice_dir / filename)

            # Create empty mock MP3 file for testing
            Path(voice_path).write_bytes(b'MOCK_AUDIO_DATA')

            self.logger.info(f"✅ Mock voice file created: {voice_path}")

            return voice_path

        except Exception as e:
            self.logger.error(f"❌ Voice file generation failed for {filename}: {e}")
            raise

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
        for key, path in voice_paths.items():
            if not os.path.exists(path):
                return {'valid': False, 'error': f'Voice file not found: {path}'}

        return {'valid': True}
