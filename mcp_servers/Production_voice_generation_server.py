#!/usr/bin/env python3
"""
Production Voice Generation MCP Server - Using ElevenLabs API
"""

import aiohttp
import asyncio
from typing import Dict, List, Optional
import json
import base64
from io import BytesIO

class ProductionVoiceGenerationMCPServer:
    def __init__(self, elevenlabs_api_key: str):
        self.api_key = elevenlabs_api_key
        self.base_url = "https://api.elevenlabs.io/v1"
        self.voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice (or configure as needed)
        self.headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
    async def generate_voice_for_record(self, record: Dict) -> Dict:
        """Generate voice for all scripts in a record - ASYNC/PARALLEL"""
        try:
            print("🚀 Starting ASYNC voice generation for all scripts...")
            voice_tasks = []
            voice_keys = []
            
            # Prepare intro voice task
            if 'IntroScript' in record.get('fields', {}):
                voice_tasks.append(self.generate_voice(
                    record['fields']['IntroScript'],
                    duration_target=5
                ))
                voice_keys.append('intro_voice')
            
            # Prepare product voice tasks
            for i in range(1, 6):
                script_field = f'Product{i}Script'
                if script_field in record.get('fields', {}):
                    voice_tasks.append(self.generate_voice(
                        record['fields'][script_field],
                        duration_target=9
                    ))
                    voice_keys.append(f'product{i}_voice')
            
            # Prepare outro voice task
            if 'OutroScript' in record.get('fields', {}):
                voice_tasks.append(self.generate_voice(
                    record['fields']['OutroScript'],
                    duration_target=5
                ))
                voice_keys.append('outro_voice')
            
            # Execute all voice generation tasks in PARALLEL
            print(f"⚡ Generating {len(voice_tasks)} voices in parallel...")
            voice_results = await asyncio.gather(*voice_tasks, return_exceptions=True)
            
            # Map results to voice_urls
            voice_urls = {}
            for key, result in zip(voice_keys, voice_results):
                if isinstance(result, Exception):
                    print(f"⚠️ Voice generation failed for {key}: {result}")
                elif result:
                    voice_urls[key] = result
                    print(f"✅ Generated {key}")
            
            print(f"🎉 Async voice generation complete! Generated {len(voice_urls)}/{len(voice_tasks)} voices")
            
            # Update record with voice URLs
            if 'fields' not in record:
                record = {'record_id': record.get('record_id', ''), 'fields': {}}
            
            # Add voice URLs to record fields
            for key, url in voice_urls.items():
                if 'intro_voice' in key:
                    record['fields']['IntroMp3'] = url
                elif 'outro_voice' in key:
                    record['fields']['OutroMp3'] = url
                elif 'product' in key:
                    # Extract product number from key (e.g., 'product1_voice' -> '1')
                    product_num = key.replace('product', '').replace('_voice', '')
                    record['fields'][f'Product{product_num}Mp3'] = url
            
            return {
                'success': True,
                'updated_record': record,
                'voice_urls': voice_urls
            }
            
        except Exception as e:
            print(f"❌ Error generating voices: {e}")
            return {
                'success': False,
                'error': str(e),
                'updated_record': record
            }
    
    async def generate_voice(self, text: str, duration_target: int = 7, voice_id: str = None) -> Optional[str]:
        """Generate voice using ElevenLabs API"""
        try:
            if not text:
                return None
            
            # Use provided voice_id or default
            voice = voice_id or self.voice_id
            
            # ElevenLabs text-to-speech endpoint
            url = f"{self.base_url}/text-to-speech/{voice}"
            
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
                    if response.status == 200:
                        # Get audio data
                        audio_data = await response.read()
                        
                        # Convert to base64 for storage
                        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                        
                        # Create data URL
                        audio_url = f"data:audio/mpeg;base64,{audio_base64}"
                        
                        print(f"✅ Generated voice for text: {text[:30]}...")
                        return audio_url
                    else:
                        error_data = await response.text()
                        print(f"❌ ElevenLabs API error: {response.status} - {error_data}")
                        return None
                        
        except Exception as e:
            print(f"❌ Error generating voice: {e}")
            return None
    
    async def generate_intro_voice(self, text: str) -> Optional[str]:
        """Generate intro voice (5 seconds)"""
        return await self.generate_voice(text, duration_target=5)
    
    async def generate_outro_voice(self, text: str) -> Optional[str]:
        """Generate outro voice (5 seconds)"""
        return await self.generate_voice(text, duration_target=5)
    
    async def generate_product_voice(self, product_name: str, description: str, rank: int) -> Optional[str]:
        """Generate product voice (9 seconds)"""
        text = f"Number {rank}: {product_name}. {description}"
        return await self.generate_voice(text, duration_target=9)
    
    def _optimize_text_for_duration(self, text: str, target_duration: int) -> str:
        """Optimize text length for target duration"""
        # Approximate: 150 words per minute = 2.5 words per second
        words_per_second = 2.5
        target_words = int(target_duration * words_per_second)
        
        words = text.split()
        
        if len(words) > target_words:
            # Truncate if too long
            optimized = ' '.join(words[:target_words])
            return optimized + '.'
        elif len(words) < target_words * 0.7:
            # Add pauses if too short
            return text + ' ... '
        else:
            return text
    
    async def get_voice_list(self) -> List[Dict]:
        """Get list of available voices from ElevenLabs"""
        try:
            url = f"{self.base_url}/voices"
            headers = {"xi-api-key": self.api_key}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        voices = data.get('voices', [])
                        return [
                            {
                                'voice_id': v['voice_id'],
                                'name': v['name'],
                                'category': v.get('category', 'unknown')
                            }
                            for v in voices
                        ]
                    else:
                        print(f"❌ Failed to get voice list: {response.status}")
                        return []
                        
        except Exception as e:
            print(f"❌ Error getting voice list: {e}")
            return []
    
    async def check_usage(self) -> Dict:
        """Check ElevenLabs API usage and limits"""
        try:
            url = f"{self.base_url}/user/subscription"
            headers = {"xi-api-key": self.api_key}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'character_count': data.get('character_count', 0),
                            'character_limit': data.get('character_limit', 0),
                            'available_characters': data.get('character_limit', 0) - data.get('character_count', 0),
                            'next_reset': data.get('next_character_count_reset_unix', 0)
                        }
                    else:
                        print(f"❌ Failed to check usage: {response.status}")
                        return {}
                        
        except Exception as e:
            print(f"❌ Error checking usage: {e}")
            return {}
    
    def get_fallback_voice_urls(self) -> Dict:
        """Return fallback voice URLs if API fails"""
        return {
            'intro_voice': 'data:audio/mpeg;base64,SUQzAwAAAAA...',  # Placeholder
            'product1_voice': 'data:audio/mpeg;base64,SUQzAwAAAAA...',
            'product2_voice': 'data:audio/mpeg;base64,SUQzAwAAAAA...',
            'product3_voice': 'data:audio/mpeg;base64,SUQzAwAAAAA...',
            'product4_voice': 'data:audio/mpeg;base64,SUQzAwAAAAA...',
            'product5_voice': 'data:audio/mpeg;base64,SUQzAwAAAAA...',
            'outro_voice': 'data:audio/mpeg;base64,SUQzAwAAAAA...'
        }