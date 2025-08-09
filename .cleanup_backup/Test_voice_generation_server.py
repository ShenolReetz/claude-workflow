#!/usr/bin/env python3
"""
Test Voice Generation MCP Server - Hardcoded responses for testing
Purpose: Test voice generation without consuming API tokens
"""

from typing import Dict, Any, List

class TestVoiceGenerationMCPServer:
    """Test Voice Generation MCP Server with hardcoded responses"""
    
    def __init__(self, elevenlabs_api_key: str):
        self.elevenlabs_api_key = elevenlabs_api_key  # Not used in test mode
        
        # Hardcoded test audio URLs (publicly accessible)
        self.test_audio_urls = [
            'https://www.learningcontainer.com/wp-content/uploads/2020/02/Kalimba.mp3',
            'https://sample-videos.com/zip/10/mp3/SampleAudio_0.4mb_mp3.mp3',
            'https://file-examples.com/storage/feaca9322b9931d2cb3a1b3/2017/11/file_example_MP3_700KB.mp3'
        ]
        
        print("🧪 Test Voice Generation Server initialized with hardcoded audio URLs")
    
    async def generate_voice_for_record(self, record_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate hardcoded voice URLs for all required fields"""
        print("🎙️ Generating test voice narration (no API calls)")
        
        updated_record = record_data.copy()
        
        # Generate intro voice
        if record_data.get('IntroHook'):
            updated_record['IntroVoiceURL'] = self.test_audio_urls[0]
            print(f"   🎵 Intro voice: Generated")
        
        # Generate outro voice
        if record_data.get('OutroCallToAction'):
            updated_record['OutroVoiceURL'] = self.test_audio_urls[1]
            print(f"   🎵 Outro voice: Generated")
        
        # Generate product voices (1-5)
        for i in range(1, 6):
            description_key = f'ProductNo{i}Description'
            voice_key = f'Product{i}VoiceURL'
            
            if record_data.get(description_key):
                updated_record[voice_key] = self.test_audio_urls[i % len(self.test_audio_urls)]
                print(f"   🎵 Product {i} voice: Generated")
        
        return {
            'success': True,
            'updated_record': updated_record,
            'voices_generated': 7,  # Intro + Outro + 5 products
            'total_duration': '55 seconds',
            'api_calls_used': 0,
            'cost': '$0.00'
        }
    
    async def generate_single_voice(self, text: str, voice_id: str = 'default') -> Dict[str, Any]:
        """Generate single hardcoded voice URL"""
        print(f"🎙️ Generating single test voice for text: {text[:30]}... (no API call)")
        
        return {
            'success': True,
            'audio_url': self.test_audio_urls[0],
            'voice_id': voice_id,
            'duration': '10 seconds',
            'text_length': len(text),
            'api_calls_used': 0,
            'cost': '$0.00'
        }
    
    async def get_available_voices(self) -> List[Dict[str, Any]]:
        """Return hardcoded list of available test voices"""
        print("🎤 Getting test voice list (no API call)")
        
        return [
            {'voice_id': 'test_voice_1', 'name': 'Emma Test', 'language': 'en-US'},
            {'voice_id': 'test_voice_2', 'name': 'James Test', 'language': 'en-US'},
            {'voice_id': 'test_voice_3', 'name': 'Sarah Test', 'language': 'en-US'}
        ]
    
    async def validate_audio_url(self, audio_url: str) -> bool:
        """Always return True for test URLs"""
        print(f"✅ Test audio URL validation: {audio_url[:50]}... (no API call)")
        return True
    
    async def close(self):
        """Close test server (no cleanup needed)"""
        print("🧪 Test Voice Generation Server closed")
        pass