#!/usr/bin/env python3

import asyncio
import json
from mcp_servers.Test_airtable_server import AirtableMCPServer
from mcp_servers.Test_default_audio_manager import TestDefaultAudioManager

async def test_audio_manager_direct():
    # Load API keys
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    server = AirtableMCPServer(
        api_key=config['airtable_api_key'],
        base_id=config['airtable_base_id'],
        table_name=config['airtable_table_name']
    )
    
    record_id = 'rec0CUkALU4Uxk27Y'
    
    # Clear audio fields first
    print('Clearing audio fields...')
    clear_fields = {
        'IntroMp3': '',
        'OutroMp3': '',
        'Product1Mp3': '',
        'Product2Mp3': '',
        'Product3Mp3': '',
        'Product4Mp3': '',
        'Product5Mp3': ''
    }
    
    await server.update_record(record_id, clear_fields)
    
    # Check audio fields after clearing
    record = await server.get_record_by_id(record_id)
    audio_count_before = sum(1 for field in clear_fields.keys() if record['fields'].get(field))
    print(f'Audio fields present before default audio manager: {audio_count_before}/7')
    
    # Now use default audio manager
    print('Using default audio manager...')
    audio_manager = TestDefaultAudioManager()
    
    # Get some mock Amazon result data
    amazon_result = {
        'products': [
            {'title': 'Test Product 1'},
            {'title': 'Test Product 2'},
            {'title': 'Test Product 3'},
            {'title': 'Test Product 4'},
            {'title': 'Test Product 5'}
        ]
    }
    
    # Generate audio updates
    audio_updates = audio_manager.populate_airtable_with_default_audio(amazon_result, 'electronics')
    
    print(f'Audio updates generated: {len(audio_updates)} fields')
    for field, value in audio_updates.items():
        if 'Mp3' in field:
            print(f'  {field}: {value[:50]}...')
    
    # Apply the updates
    if audio_updates:
        await server.update_record(record_id, audio_updates)
        print('✅ Audio updates applied to Airtable')
    
    # Check audio fields after applying updates
    record = await server.get_record_by_id(record_id)
    audio_count_after = sum(1 for field in clear_fields.keys() if record['fields'].get(field))
    print(f'Audio fields present after default audio manager: {audio_count_after}/7')
    
    if audio_count_after == 7:
        print('✅ Default audio manager successfully populated all audio fields')
    else:
        print('❌ Default audio manager failed to populate all audio fields')
        for field in clear_fields.keys():
            if not record['fields'].get(field):
                print(f'  Missing: {field}')

if __name__ == "__main__":
    asyncio.run(test_audio_manager_direct())