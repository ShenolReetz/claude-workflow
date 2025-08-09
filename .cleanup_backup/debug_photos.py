#!/usr/bin/env python3
"""
Debug script to show what photo URLs are being stored in Airtable
"""
import asyncio
import sys
sys.path.append('/home/claude-workflow')

from mcp_servers.Production_airtable_server import ProductionAirtableMCPServer
import json

async def check_photo_storage():
    """Check what photo URLs are stored in Airtable"""
    
    config = {
        'airtable_api_key': 'patuus6XXiHK6EP8j.f230def2424a446ca5da8dfbe70c64a324ad0162dde2ef91ffda381394f75c70',
        'airtable_base_id': 'appTtNBJ8dAnjvkPP',
        'airtable_table_name': 'Video Titles'
    }
    
    server = ProductionAirtableMCPServer(
        config['airtable_api_key'],
        config['airtable_base_id'], 
        config['airtable_table_name']
    )
    
    print("🔍 Checking photo storage in Airtable...")
    
    # Get recent records
    records = await server.list_records(limit=5, status_filter='TextControlStatus')
    
    for record in records:
        title = record['fields'].get('Title', 'N/A')
        status = record['fields'].get('Status', 'N/A')
        print(f"\n📋 Record: {title[:50]}...")
        print(f"   Status: {status}")
        
        # Check photo fields
        for i in range(1, 6):
            photo_url = record['fields'].get(f'ProductNo{i}Photo', '')
            generated_photo = record['fields'].get(f'ProductNo{i}GeneratedPhoto', '')
            product_title = record['fields'].get(f'ProductNo{i}Title', '')
            
            if photo_url or product_title:
                print(f"   🖼️ Product {i}: {product_title[:40]}...")
                if photo_url:
                    if photo_url.startswith('http'):
                        print(f"      📷 Original: {photo_url[:80]}...")
                        # Check if it's Amazon URL
                        if 'amazon.com' in photo_url or 'media-amazon.com' in photo_url:
                            print(f"      ✅ Amazon image URL detected")
                        elif 'drive.google.com' in photo_url:
                            print(f"      ✅ Google Drive URL detected")
                        elif 'oaidalleapiprodscus.blob.core.windows.net' in photo_url:
                            print(f"      🎨 Generated DALL-E image URL")
                    else:
                        print(f"      📷 Original: {photo_url}")
                
                if generated_photo:
                    print(f"      🎨 Generated: {generated_photo[:80]}...")

if __name__ == "__main__":
    asyncio.run(check_photo_storage())