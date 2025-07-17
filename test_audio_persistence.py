#!/usr/bin/env python3

import asyncio
import json
from mcp_servers.Test_airtable_server import AirtableMCPServer

async def test_platform_content_effect():
    # Load API keys
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    server = AirtableMCPServer(
        api_key=config['airtable_api_key'],
        base_id=config['airtable_base_id'],
        table_name=config['airtable_table_name']
    )
    
    record_id = 'rec0CUkALU4Uxk27Y'
    
    # First, set audio fields
    print('Setting audio fields...')
    audio_fields = {
        'IntroMp3': 'https://drive.google.com/file/d/test_intro/view',
        'OutroMp3': 'https://drive.google.com/file/d/test_outro/view',
        'Product1Mp3': 'https://drive.google.com/file/d/test_product1/view',
        'Product2Mp3': 'https://drive.google.com/file/d/test_product2/view',
        'Product3Mp3': 'https://drive.google.com/file/d/test_product3/view',
        'Product4Mp3': 'https://drive.google.com/file/d/test_product4/view',
        'Product5Mp3': 'https://drive.google.com/file/d/test_product5/view'
    }
    
    await server.update_record(record_id, audio_fields)
    
    # Check audio fields after setting
    record = await server.get_record_by_id(record_id)
    audio_count_before = sum(1 for field in audio_fields.keys() if field in record['fields'])
    print(f'Audio fields present before platform update: {audio_count_before}/7')
    
    # Now simulate a platform content update
    print('Simulating platform content update...')
    platform_fields = {
        'YouTubeTitle': 'Test YouTube Title',
        'YouTubeDescription': 'Test YouTube Description',
        'TikTokTitle': 'Test TikTok Title',
        'TikTokDescription': 'Test TikTok Description',
        'InstagramTitle': 'Test Instagram Title',
        'InstagramCaption': 'Test Instagram Caption',
        'WordPressTitle': 'Test WordPress Title',
        'WordPressContent': 'Test WordPress Content',
        'VideoTitle': 'Test Video Title',
        'VideoDescription': 'Test Video Description',
        'VideoProductionRDY': 'Ready'
    }
    
    await server.update_record(record_id, platform_fields)
    
    # Check audio fields after platform update
    record = await server.get_record_by_id(record_id)
    audio_count_after = sum(1 for field in audio_fields.keys() if field in record['fields'])
    print(f'Audio fields present after platform update: {audio_count_after}/7')
    
    if audio_count_before != audio_count_after:
        print('❌ Audio fields were affected by platform content update!')
        for field in audio_fields.keys():
            if field not in record['fields']:
                print(f'  Missing: {field}')
    else:
        print('✅ Audio fields preserved during platform content update')

if __name__ == "__main__":
    asyncio.run(test_platform_content_effect())