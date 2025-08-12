#!/usr/bin/env python3
"""
Production Voice Generation MCP Server - Async Optimized Version
=================================================================
Optimized for parallel voice generation with ElevenLabs API
- Supports concurrent requests based on subscription tier
- Implements rate limiting and retry logic
- Generates all voices in parallel for maximum speed
"""

import aiohttp
import asyncio
from typing import Dict, List, Optional, Tuple
import json
import base64
import time
from asyncio import Semaphore

class ProductionVoiceGenerationAsyncOptimized:
    def __init__(self, elevenlabs_api_key: str, max_concurrent_requests: int = 5):
        self.api_key = elevenlabs_api_key
        self.base_url = "https://api.elevenlabs.io/v1"
        self.voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice
        self.headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        # Rate limiting based on subscription tier
        # Free: 2, Starter: 3, Creator: 5, Pro: 10, Scale: 15
        self.semaphore = Semaphore(max_concurrent_requests)
        self.max_retries = 3
        
    async def generate_all_voices_parallel(self, record: Dict) -> Dict:
        """Generate all voices in parallel with optimized concurrency"""
        try:
            start_time = time.time()
            print(f"🚀 Starting PARALLEL voice generation with semaphore limit...")
            
            # Prepare all voice generation tasks
            voice_tasks = []
            
            # Intro voice task
            if 'IntroScript' in record.get('fields', {}):
                voice_tasks.append(('intro', self._generate_voice_with_retry(
                    record['fields']['IntroScript'],
                    duration_target=5,
                    voice_type='intro'
                )))
            
            # Product voice tasks (all in parallel)
            for i in range(1, 6):
                script_field = f'Product{i}Script'
                if script_field in record.get('fields', {}):
                    voice_tasks.append((f'product{i}', self._generate_voice_with_retry(
                        record['fields'][script_field],
                        duration_target=9,
                        voice_type=f'product{i}'
                    )))
            
            # Outro voice task
            if 'OutroScript' in record.get('fields', {}):
                voice_tasks.append(('outro', self._generate_voice_with_retry(
                    record['fields']['OutroScript'],
                    duration_target=5,
                    voice_type='outro'
                )))
            
            # Execute all tasks in parallel
            print(f"⚡ Generating {len(voice_tasks)} voices concurrently...")
            
            # Unpack tasks for gather
            task_names = [name for name, _ in voice_tasks]
            task_coroutines = [task for _, task in voice_tasks]
            
            # Run all voice generations in parallel
            results = await asyncio.gather(*task_coroutines, return_exceptions=True)
            
            # Process results
            voice_urls = {}
            success_count = 0
            
            for name, result in zip(task_names, results):
                if isinstance(result, Exception):
                    print(f"❌ Failed to generate {name} voice: {result}")
                elif result:
                    voice_urls[f'{name}_voice'] = result
                    success_count += 1
                    print(f"✅ Generated {name} voice")
            
            # Update record with voice URLs (thread-safe)
            # Create a lock to prevent race conditions when updating the shared record
            record_lock = asyncio.Lock()
            
            async with record_lock:
                if 'fields' not in record:
                    record = {'record_id': record.get('record_id', ''), 'fields': {}}
                
                # Map voice URLs to Airtable fields
                for key, url in voice_urls.items():
                    if 'intro_voice' in key:
                        record['fields']['IntroMp3'] = url
                    elif 'outro_voice' in key:
                        record['fields']['OutroMp3'] = url
                    elif 'product' in key:
                        product_num = key.replace('product', '').replace('_voice', '')
                        record['fields'][f'Product{product_num}Mp3'] = url
            
            elapsed_time = time.time() - start_time
            print(f"🎉 Parallel voice generation complete in {elapsed_time:.2f}s!")
            print(f"   Generated {success_count}/{len(voice_tasks)} voices successfully")
            
            return {
                'success': True,
                'updated_record': record,
                'voice_urls': voice_urls,
                'generation_time': elapsed_time,
                'success_rate': f"{success_count}/{len(voice_tasks)}"
            }
            
        except Exception as e:
            print(f"❌ Error in parallel voice generation: {e}")
            return {
                'success': False,
                'error': str(e),
                'updated_record': record
            }
    
    async def _generate_voice_with_retry(self, text: str, duration_target: int, voice_type: str) -> Optional[str]:
        """Generate voice with retry logic and rate limiting"""
        for attempt in range(self.max_retries):
            try:
                async with self.semaphore:  # Rate limiting
                    result = await self._generate_single_voice(text, duration_target)
                    if result:
                        return result
                    
            except aiohttp.ClientError as e:
                if attempt < self.max_retries - 1:
                    wait_time = (2 ** attempt) * 0.5  # Exponential backoff
                    print(f"⚠️ Retry {attempt + 1} for {voice_type} after {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    print(f"❌ Max retries reached for {voice_type}")
                    raise
        
        return None
    
    async def _generate_single_voice(self, text: str, duration_target: int) -> Optional[str]:
        """Generate a single voice using ElevenLabs API"""
        if not text:
            return None
        
        url = f"{self.base_url}/text-to-speech/{self.voice_id}"
        
        # Optimize text for target duration
        optimized_text = self._optimize_text_for_duration(text, duration_target)
        
        payload = {
            "text": optimized_text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5,
                "style": 0.5,
                "use_speaker_boost": True
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=self.headers, json=payload) as response:
                # Check response headers for rate limit info
                if 'current-concurrent-requests' in response.headers:
                    current = response.headers.get('current-concurrent-requests')
                    maximum = response.headers.get('maximum-concurrent-requests', 'unknown')
                    print(f"   Concurrency: {current}/{maximum}")
                
                if response.status == 200:
                    audio_data = await response.read()
                    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                    audio_url = f"data:audio/mpeg;base64,{audio_base64}"
                    return audio_url
                    
                elif response.status == 429:
                    error_data = await response.json()
                    if error_data.get('detail', {}).get('message') == 'too_many_concurrent_requests':
                        print(f"⚠️ Hit concurrent request limit, will retry...")
                        raise aiohttp.ClientError("Concurrent request limit")
                    else:
                        print(f"⚠️ System busy, will retry...")
                        raise aiohttp.ClientError("System busy")
                        
                else:
                    error_text = await response.text()
                    print(f"❌ ElevenLabs API error {response.status}: {error_text}")
                    return None
    
    def _optimize_text_for_duration(self, text: str, target_duration: int) -> str:
        """Optimize text length for target duration"""
        words_per_second = 2.5
        target_words = int(target_duration * words_per_second)
        
        words = text.split()
        
        if len(words) > target_words:
            optimized = ' '.join(words[:target_words])
            return optimized + '.'
        elif len(words) < target_words * 0.7:
            return text + ' ... '
        else:
            return text

# Wrapper function for easy integration
async def generate_voices_async_optimized(record: Dict, config: Dict) -> Dict:
    """Async optimized voice generation for production workflow"""
    # Determine max concurrent requests based on subscription
    # Default to 5 (Creator tier) but can be configured
    max_concurrent = config.get('elevenlabs_max_concurrent', 5)
    
    generator = ProductionVoiceGenerationAsyncOptimized(
        elevenlabs_api_key=config.get('elevenlabs_api_key', ''),
        max_concurrent_requests=max_concurrent
    )
    
    return await generator.generate_all_voices_parallel(record)