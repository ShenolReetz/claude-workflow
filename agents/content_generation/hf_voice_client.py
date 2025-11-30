"""
Hugging Face Voice Generation Client
=====================================
Generates voices using Bark or Coqui TTS.

Note: Bark may have limited availability on HF Inference API.
Consider self-hosting Coqui TTS as alternative.
"""

import aiohttp
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class HuggingFaceVoiceClient:
    """
    Client for HF voice generation
    Replaces ElevenLabs to save costs
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_token = config.get('hf_api_token')
        self.model_id = config.get('hf_voice_model', 'suno/bark')

        self.base_url = f"https://router.huggingface.co/models/{self.model_id}"

        # Voice presets
        self.voice_presets = {
            'intro': 'v2/en_speaker_6',      # Energetic male
            'outro': 'v2/en_speaker_6',      # Same for consistency
            'product': 'v2/en_speaker_9'     # Professional male
        }

        self.logger = logging.getLogger(__name__)
        self.logger.info(f"🎤 HF Voice Client initialized: {self.model_id}")

    async def generate_voice(self, text: str, voice_preset: str = 'narrator',
                            save_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate voice audio from text

        Args:
            text: Text to speak
            voice_preset: Voice style preset
            save_path: Optional path to save audio

        Returns:
            {'success': bool, 'audio_path': str, 'audio_bytes': bytes}
        """
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "inputs": text,
            "parameters": {
                "voice_preset": voice_preset
            }
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, headers=headers, json=payload,
                                       timeout=aiohttp.ClientTimeout(total=90)) as response:

                    if response.status == 200:
                        audio_bytes = await response.read()

                        # Save if path provided
                        if save_path:
                            Path(save_path).write_bytes(audio_bytes)
                            self.logger.info(f"✅ Voice saved: {save_path}")

                        return {
                            'success': True,
                            'audio_path': save_path,
                            'audio_bytes': audio_bytes,
                            'size_kb': len(audio_bytes) / 1024
                        }
                    else:
                        error_text = await response.text()
                        self.logger.error(f"❌ Voice generation failed: {response.status} - {error_text}")

                        return {
                            'success': False,
                            'error': error_text,
                            'status': response.status,
                            'note': 'Bark may not be available on HF API - consider self-hosted Coqui TTS'
                        }

        except Exception as e:
            self.logger.error(f"❌ Voice generation exception: {e}")
            return {
                'success': False,
                'error': str(e),
                'note': 'Consider using self-hosted Coqui TTS as alternative'
            }

    async def generate_script_voice(self, script: str, section: str,
                                   record_id: str, storage_manager) -> Dict[str, Any]:
        """
        Generate voice for script section (compatible with existing workflow)

        Args:
            script: Text to speak
            section: 'intro', 'product1'-'product5', or 'outro'
            record_id: Airtable record ID
            storage_manager: Storage manager

        Returns:
            Result dictionary with audio path
        """
        # Get voice preset for section
        voice_preset = self.voice_presets.get(section.replace('1','').replace('2','').replace('3','').replace('4','').replace('5',''),
                                              self.voice_presets['product'])

        # Generate voice
        result = await self.generate_voice(script, voice_preset)

        if result['success']:
            # Save using storage manager
            audio_path = storage_manager.save_file(
                result['audio_bytes'],
                f"{section}.mp3",
                "audio",
                record_id
            )

            return {
                'success': True,
                'audio_path': audio_path,
                'local_path': audio_path,
                'section': section
            }
        else:
            return result

    async def generate_all_voices(self, scripts: Dict[str, str],
                                 record_id: str, storage_manager) -> Dict[str, Any]:
        """
        Generate all voice files for a video

        Args:
            scripts: Dictionary of {section: script_text}
            record_id: Airtable record ID
            storage_manager: Storage manager

        Returns:
            Dictionary of results for each section
        """
        results = {}

        # Generate voices in parallel
        tasks = []
        for section, script in scripts.items():
            task = self.generate_script_voice(script, section, record_id, storage_manager)
            tasks.append((section, task))

        # Wait for all to complete
        import asyncio
        completed = await asyncio.gather(*[t[1] for t in tasks], return_exceptions=True)

        # Collect results
        for (section, _), result in zip(tasks, completed):
            if isinstance(result, Exception):
                results[section] = {
                    'success': False,
                    'error': str(result)
                }
            else:
                results[section] = result

        # Check if all succeeded
        all_success = all(r.get('success', False) for r in results.values())

        return {
            'success': all_success,
            'results': results,
            'total_voices': len(scripts),
            'successful': sum(1 for r in results.values() if r.get('success', False))
        }


# Alternative: Coqui TTS (self-hosted)
class CoquiTTSClient:
    """
    Self-hosted Coqui TTS client (alternative if Bark not available on HF)

    Requires: pip install TTS
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model_name = config.get('coqui_model', 'tts_models/en/ljspeech/tacotron2-DDC')

        try:
            from TTS.api import TTS
            self.tts = TTS(self.model_name)
            self.available = True
            self.logger = logging.getLogger(__name__)
            self.logger.info(f"🎤 Coqui TTS initialized: {self.model_name}")
        except ImportError:
            self.available = False
            self.logger = logging.getLogger(__name__)
            self.logger.warning("Coqui TTS not installed. Run: pip install TTS")

    async def generate_voice(self, text: str, save_path: str) -> Dict[str, Any]:
        """Generate voice using Coqui TTS"""
        if not self.available:
            return {
                'success': False,
                'error': 'Coqui TTS not installed'
            }

        try:
            # Generate (synchronous operation)
            import asyncio
            await asyncio.to_thread(self.tts.tts_to_file, text=text, file_path=save_path)

            return {
                'success': True,
                'audio_path': save_path
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
