#!/usr/bin/env python3
"""
Check the video URL from the latest created video
"""
import asyncio
import sys
sys.path.append('/home/claude-workflow')

from mcp_servers.Production_airtable_server import ProductionAirtableMCPServer
import json

async def get_latest_video_url():
    """Get the video URL from the latest workflow run"""
    
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
    
    print("🔍 Checking for video URLs in latest records...")
    
    try:
        # Get recent records that might have videos
        async with server._get_session() as session:
            params = {
                "maxRecords": 5,
                "sort[0][field]": "ID", 
                "sort[0][direction]": "desc"
            }
            
            async with session.get(server.base_url, headers=server.headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    records = data.get('records', [])
                    
                    for record in records:
                        title = record['fields'].get('Title', 'N/A')
                        status = record['fields'].get('Status', 'N/A')
                        video_url = record['fields'].get('VideoURL', '')
                        project_id = record['fields'].get('JSON2VideoProjectID', '')
                        created_at = record['fields'].get('VideoCreatedAt', '')
                        
                        print(f"\n📋 Record: {title[:50]}...")
                        print(f"   Status: {status}")
                        print(f"   Record ID: {record['id']}")
                        
                        if video_url:
                            print(f"   🎬 VIDEO URL: {video_url}")
                        else:
                            print(f"   ⚠️ No VideoURL field found")
                            
                        if project_id:
                            print(f"   🆔 JSON2Video Project ID: {project_id}")
                            print(f"   📅 Created: {created_at}")
                            
                            # Also provide the project URL
                            project_url = f"https://app.json2video.com/projects/{project_id}"
                            print(f"   🌐 Project Dashboard: {project_url}")
                        else:
                            print(f"   ⚠️ No JSON2VideoProjectID found")
                            
                        # Check if this might be our TV Mount Stands record
                        if 'TV Mount' in title or 'Mount Stands' in title:
                            print(f"   🎯 ← This appears to be the latest TV Mount Stands video!")
                            
                        print("-" * 60)
                else:
                    print(f"❌ Error fetching records: {response.status}")
                    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(get_latest_video_url())