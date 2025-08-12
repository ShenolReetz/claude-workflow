#!/usr/bin/env python3
"""Check the last processed Airtable record"""

import asyncio
import json
import sys
sys.path.append('/home/claude-workflow')

from mcp_servers.Production_airtable_server import ProductionAirtableMCPServer

async def check_last_record():
    # Load config
    with open('config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    server = ProductionAirtableMCPServer(
        api_key=config['airtable_api_key'],
        base_id=config['airtable_base_id'],
        table_name=config['airtable_table_name']
    )
    
    # Get a non-pending record (last processed)
    import aiohttp
    async with aiohttp.ClientSession() as session:
        # Get records with Status != 'Pending', sorted by LastOptimizationDate
        params = {
            "filterByFormula": "NOT({Status} = 'Pending')",
            "maxRecords": 1,
            "sort[0][field]": "LastOptimizationDate",
            "sort[0][direction]": "desc"
        }
        
        async with session.get(server.base_url, headers=server.headers, params=params) as response:
            if response.status == 200:
                data = await response.json()
                records = data.get('records', [])
                if records:
                    record = records[0]
                    fields = record['fields']
                    
                    print("\n=== LAST PROCESSED RECORD ===")
                    print(f"Record ID: {record['id']}")
                    print(f"Title: {fields.get('Title', 'N/A')}")
                    print(f"Video Title: {fields.get('VideoTitle', 'N/A')}")
                    print(f"Status: {fields.get('Status', 'N/A')}")
                    print(f"Last Updated: {fields.get('LastOptimizationDate', 'N/A')}")
                    
                    print("\n=== URL FIELDS ===")
                    # Check video URLs
                    print(f"Final Video: {'✅' if fields.get('FinalVideo') else '❌'} {fields.get('FinalVideo', 'Not saved')[:50]}...")
                    print(f"YouTube URL: {'✅' if fields.get('YouTubeURL') else '❌'} {fields.get('YouTubeURL', 'Not saved')}")
                    print(f"WordPress URL: {'✅' if fields.get('WordPressURL') else '❌'} {fields.get('WordPressURL', 'Not saved')}")
                    print(f"TikTok URL: {'✅' if fields.get('TikTokURL') else '❌'} {fields.get('TikTokURL', 'Not saved')}")
                    
                    print("\n=== AUDIO FILES ===")
                    # Check audio files
                    print(f"Intro MP3: {'✅' if fields.get('IntroMp3') else '❌'} {'Saved' if fields.get('IntroMp3') else 'Not saved'}")
                    print(f"Outro MP3: {'✅' if fields.get('OutroMp3') else '❌'} {'Saved' if fields.get('OutroMp3') else 'Not saved'}")
                    for i in range(1, 6):
                        mp3_field = f'Product{i}Mp3'
                        has_audio = '✅' if fields.get(mp3_field) else '❌'
                        print(f"Product {i} MP3: {has_audio} {'Saved' if fields.get(mp3_field) else 'Not saved'}")
                    
                    print("\n=== IMAGE FILES ===")
                    # Check images
                    print(f"Intro Photo: {'✅' if fields.get('IntroPhoto') else '❌'} {fields.get('IntroPhoto', 'Not saved')[:50] if fields.get('IntroPhoto') else 'Not saved'}...")
                    print(f"Outro Photo: {'✅' if fields.get('OutroPhoto') else '❌'} {fields.get('OutroPhoto', 'Not saved')[:50] if fields.get('OutroPhoto') else 'Not saved'}...")
                    for i in range(1, 6):
                        photo_field = f'ProductNo{i}Photo'
                        has_photo = '✅' if fields.get(photo_field) else '❌'
                        print(f"Product {i} Photo: {has_photo} {fields.get(photo_field, 'Not saved')[:50] if fields.get(photo_field) else 'Not saved'}...")
                    
                    print("\n=== GOOGLE DRIVE ===")
                    # Check for any Google Drive related fields
                    for field_name, value in fields.items():
                        if 'drive' in field_name.lower() or 'google' in field_name.lower():
                            print(f"{field_name}: {value[:100] if value else 'Empty'}...")
                    
                    # Count filled fields
                    url_fields = ['FinalVideo', 'YouTubeURL', 'WordPressURL', 'TikTokURL']
                    audio_fields = ['IntroMp3', 'OutroMp3'] + [f'Product{i}Mp3' for i in range(1, 6)]
                    image_fields = ['IntroPhoto', 'OutroPhoto'] + [f'ProductNo{i}Photo' for i in range(1, 6)]
                    
                    urls_filled = sum(1 for f in url_fields if fields.get(f))
                    audio_filled = sum(1 for f in audio_fields if fields.get(f))
                    images_filled = sum(1 for f in image_fields if fields.get(f))
                    
                    print(f"\n=== SUMMARY ===")
                    print(f"URLs Saved: {urls_filled}/{len(url_fields)}")
                    print(f"Audio Files Saved: {audio_filled}/{len(audio_fields)}")
                    print(f"Images Saved: {images_filled}/{len(image_fields)}")
                    
                else:
                    print("No processed records found")
            else:
                print(f"Error: {response.status}")
                print(await response.text())

if __name__ == "__main__":
    asyncio.run(check_last_record())