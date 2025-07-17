#!/usr/bin/env python3
"""
Test Voice Generation Workflow Integration
"""

import asyncio
import json
import sys
sys.path.append('/home/claude-workflow')

from src.workflow_runner import ContentPipelineOrchestrator

async def test_voice_generation_workflow():
    """Test voice generation integration in workflow"""
    print("🎤 Testing Voice Generation Workflow Integration")
    print("=" * 50)
    
    # Initialize orchestrator
    orchestrator = ContentPipelineOrchestrator()
    
    # Test voice text generation
    print("\n📝 Testing voice text generation...")
    
    # Sample script data
    script_data = {
        'products': [
            {
                'title': 'SteelSeries Arctis Nova Pro',
                'description': 'Premium gaming headset with active noise cancellation and wireless connectivity.'
            },
            {
                'title': 'Razer BlackShark V2 Pro',
                'description': 'Professional esports headset with THX spatial audio and breathable cushions.'
            },
            {
                'title': 'HyperX Cloud Flight',
                'description': 'Wireless gaming headset with 30-hour battery life and comfortable design.'
            }
        ]
    }
    
    optimized_title = "Top 5 Gaming Headsets for 2025"
    
    # Test voice text generation
    voice_text_data = await orchestrator.generate_voice_text(script_data, optimized_title)
    
    print(f"✅ Generated voice text for {len(voice_text_data)} segments")
    print(f"   Intro: {voice_text_data.get('IntroHook', 'N/A')[:50]}...")
    print(f"   Outro: {voice_text_data.get('OutroCallToAction', 'N/A')[:50]}...")
    
    # Show VideoScript which contains all product voice text
    video_script = voice_text_data.get('VideoScript', 'N/A')
    if video_script != 'N/A':
        print(f"   VideoScript: {video_script[:100]}...")
    else:
        print("   VideoScript: No combined script generated")
    
    # Test voice generation (this will use ElevenLabs API)
    print("\n🎤 Testing voice generation with ElevenLabs...")
    
    # Create a mock record with voice text
    mock_record = {
        'record_id': 'test123',
        **voice_text_data
    }
    
    # Test voice generation
    voice_result = await orchestrator.generate_voice_narration('test123', mock_record)
    
    if voice_result['success']:
        print(f"✅ Voice generation successful!")
        print(f"   Generated: {voice_result['voices_generated']} voice files")
        print(f"   Saved: {voice_result['voices_saved']} files to Google Drive")
        print(f"   Airtable updates: {len(voice_result['airtable_updates'])} fields")
        
        # Show sample URLs
        for field, url in voice_result['airtable_updates'].items():
            print(f"   {field}: {url}")
    else:
        print(f"❌ Voice generation failed: {voice_result.get('errors', [])}")
    
    print("\n🎬 Ready for JSON2Video integration")
    print("   Voice files can now be used in video creation")

if __name__ == "__main__":
    asyncio.run(test_voice_generation_workflow())