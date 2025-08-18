#!/usr/bin/env python3
"""
Production Voice Generation Server - LOCAL STORAGE ONLY
========================================================
Generates voice files with ElevenLabs and saves them LOCALLY ONLY.
No Google Drive uploads. WordPress can optionally embed audio players.
"""

import asyncio
import aiohttp
from typing import Dict, List, Optional
import logging
from datetime import datetime
import time
from src.utils.dual_storage_manager import get_storage_manager

logger = logging.getLogger(__name__)


class ProductionVoiceGenerationLocal:
    """Voice generation with local storage only"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.api_key = config.get('elevenlabs_api_key')
        self.base_url = "https://api.elevenlabs.io/v1"
        
        # Voice IDs for different sections
        self.voice_ids = {
            'intro': config.get('elevenlabs_intro_voice_id', 'pNInz6obpgDQGcFmaJgB'),  # Adam
            'outro': config.get('elevenlabs_outro_voice_id', 'pNInz6obpgDQGcFmaJgB'),  # Adam
            'product': config.get('elevenlabs_product_voice_id', 'pNInz6obpgDQGcFmaJgB'),  # Adam
        }
        
        # Rate limiting based on tier
        self.max_concurrent = config.get('elevenlabs_max_concurrent', 3)  # Default to Starter tier
        
        # Initialize storage manager
        self.storage_manager = get_storage_manager(config)
        
        self.logger = logging.getLogger(__name__)
    
    async def generate_all_voices_local(self, record: Dict) -> Dict:
        """
        Generate all voice files and save locally only
        """
        try:
            start_time = time.time()
            fields = record.get('fields', {})
            record_id = record.get('record_id', 'unknown')
            
            self.logger.info(f"🎤 Generating voices for record {record_id} (LOCAL STORAGE ONLY)")
            
            # Prepare all voice generation tasks
            tasks = []
            
            # Intro voice
            intro_script = fields.get('IntroScript', '')
            if intro_script:
                tasks.append(('intro', 'IntroMp3', intro_script))
            
            # Product voices (1-5)
            for i in range(1, 6):
                script = fields.get(f'Product{i}Script', '')
                if script:
                    tasks.append((f'product{i}', f'Product{i}Mp3', script))
            
            # Outro voice
            outro_script = fields.get('OutroScript', '')
            if outro_script:
                tasks.append(('outro', 'OutroMp3', outro_script))
            
            if not tasks:
                return {
                    'success': False,
                    'error': 'No scripts to generate voices for',
                    'updated_record': record
                }
            
            self.logger.info(f"🚀 Generating {len(tasks)} voice files in parallel (max {self.max_concurrent} concurrent)")
            
            # Create semaphore for rate limiting
            semaphore = asyncio.Semaphore(self.max_concurrent)
            
            # Generate all voices with rate limiting
            voice_tasks = []
            for voice_type, field_name, script in tasks:
                task = self._generate_voice_with_limit(
                    semaphore=semaphore,
                    voice_type=voice_type,
                    script=script,
                    record_id=record_id
                )
                voice_tasks.append((voice_type, field_name, task))
            
            # Execute all voice generations
            all_tasks = [task for _, _, task in voice_tasks]
            results = await asyncio.gather(*all_tasks, return_exceptions=True)
            
            # Process results
            success_count = 0
            failed_voices = []
            
            for (voice_type, field_name, _), result in zip(voice_tasks, results):
                if isinstance(result, Exception):
                    self.logger.error(f"❌ Error generating {voice_type} voice: {result}")
                    failed_voices.append(voice_type)
                elif isinstance(result, dict) and result.get('success'):
                    # Update fields with local paths
                    fields[field_name] = result['local_path']
                    fields[f'{field_name}_Local'] = result['local_path']
                    success_count += 1
                    self.logger.info(f"✅ {voice_type} voice saved locally")
                else:
                    failed_voices.append(voice_type)
            
            elapsed_time = time.time() - start_time
            
            # Get storage statistics
            storage_stats = self.storage_manager.get_storage_stats()
            
            # Update record
            record['fields'] = fields
            
            # Log summary
            self.logger.info(f"""
════════════════════════════════════════
📊 VOICE GENERATION COMPLETE (LOCAL ONLY)
════════════════════════════════════════
✅ Success: {success_count}/{len(tasks)} voices
⏱️ Time: {elapsed_time:.1f} seconds
📁 Storage: {storage_stats.get('total_size_mb', 0)} MB
📍 Location: {storage_stats.get('storage_path', '')}
{f"❌ Failed: {', '.join(failed_voices)}" if failed_voices else ""}
════════════════════════════════════════
""")
            
            return {
                'success': success_count > 0,
                'voices_generated': success_count,
                'failed_voices': failed_voices,
                'updated_record': record,
                'elapsed_time': elapsed_time,
                'storage_stats': storage_stats,
                'local_storage_only': True
            }
            
        except Exception as e:
            self.logger.error(f"Voice generation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'updated_record': record
            }
    
    async def _generate_voice_with_limit(self, semaphore, voice_type: str, script: str, record_id: str) -> Dict:
        """Generate voice with rate limiting"""
        async with semaphore:
            return await self._generate_single_voice(voice_type, script, record_id)
    
    async def _generate_single_voice(self, voice_type: str, script: str, record_id: str) -> Dict:
        """Generate a single voice file and save locally"""
        try:
            # Determine voice ID
            if 'product' in voice_type:
                voice_id = self.voice_ids['product']
            else:
                voice_id = self.voice_ids.get(voice_type, self.voice_ids['product'])
            
            # ElevenLabs API request
            url = f"{self.base_url}/text-to-speech/{voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }
            
            data = {
                "text": script,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5
                }
            }
            
            # Generate voice with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.post(url, json=data, headers=headers, timeout=30) as response:
                            if response.status == 200:
                                audio_content = await response.read()
                                
                                # Save locally only (no Drive upload)
                                filename = f"{voice_type}.mp3"
                                result = await self.storage_manager.save_media(
                                    content=audio_content,
                                    filename=filename,
                                    media_type="audio",
                                    record_id=record_id,
                                    upload_to_drive=False  # LOCAL ONLY
                                )
                                
                                return result
                            
                            elif response.status == 429:  # Rate limit
                                wait_time = (attempt + 1) * 2
                                self.logger.warning(f"Rate limited, waiting {wait_time}s...")
                                await asyncio.sleep(wait_time)
                            else:
                                error_text = await response.text()
                                raise Exception(f"API error {response.status}: {error_text}")
                                
                except asyncio.TimeoutError:
                    if attempt < max_retries - 1:
                        self.logger.warning(f"Timeout on attempt {attempt + 1}, retrying...")
                        await asyncio.sleep(2)
                    else:
                        raise
            
            return {
                'success': False,
                'error': f'Failed after {max_retries} attempts'
            }
            
        except Exception as e:
            self.logger.error(f"Error generating {voice_type} voice: {e}")
            return {
                'success': False,
                'error': str(e)
            }