#!/usr/bin/env python3
"""Debug YouTube 403 error"""

import asyncio
import json
import sys
sys.path.append('/home/claude-workflow')

async def debug_youtube():
    # Load config
    with open('config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    # Check last video URL from workflow
    from mcp_servers.Production_airtable_server import ProductionAirtableMCPServer
    import aiohttp
    
    server = ProductionAirtableMCPServer(
        api_key=config['airtable_api_key'],
        base_id=config['airtable_base_id'],
        table_name=config['airtable_table_name']
    )
    
    async with aiohttp.ClientSession() as session:
        # Get the last record with a FinalVideo URL
        params = {
            "filterByFormula": "AND({FinalVideo} != '', {Status} != 'Pending')",
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
                    video_url = record['fields'].get('FinalVideo')
                    
                    print("\n=== VIDEO URL DEBUG ===")
                    print(f"Record ID: {record['id']}")
                    print(f"Video URL: {video_url}")
                    
                    if video_url:
                        print("\n=== URL ANALYSIS ===")
                        if video_url.startswith('http'):
                            print("✅ URL is HTTP/HTTPS")
                            
                            # Try to download with different methods
                            print("\n=== DOWNLOAD TEST ===")
                            
                            # Test 1: Simple GET request
                            async with session.get(video_url) as resp:
                                print(f"Direct GET: Status {resp.status}")
                                if resp.status == 403:
                                    print("❌ 403 Forbidden - URL requires authentication or is private")
                                elif resp.status == 404:
                                    print("❌ 404 Not Found - URL is invalid or expired")
                                elif resp.status == 200:
                                    print("✅ URL is accessible")
                                    content_type = resp.headers.get('Content-Type', '')
                                    content_length = resp.headers.get('Content-Length', 'unknown')
                                    print(f"Content-Type: {content_type}")
                                    print(f"Content-Length: {content_length}")
                                
                            # Test 2: Check if it's a JSON2Video URL
                            if 'json2video.com' in video_url:
                                print("\n=== JSON2VIDEO URL DETECTED ===")
                                print("This is a JSON2Video URL - need to download the actual video file")
                                print("The URL might be a project link, not a direct video file")
                                
                                # Extract project ID if present
                                if '/project/' in video_url:
                                    project_id = video_url.split('/project/')[-1].split('/')[0]
                                    print(f"Project ID: {project_id}")
                                    
                                    # The actual video URL might be different
                                    actual_video_url = f"https://json2video.com/api/v1/videos/{project_id}/download"
                                    print(f"Trying download URL: {actual_video_url}")
                                    
                                    async with session.get(actual_video_url) as resp:
                                        print(f"Download URL Status: {resp.status}")
                            
                            # Test 3: Check if it's a Google Drive URL
                            elif 'drive.google.com' in video_url:
                                print("\n=== GOOGLE DRIVE URL DETECTED ===")
                                print("Google Drive URLs need special handling")
                                
                                if '/file/d/' in video_url:
                                    file_id = video_url.split('/file/d/')[1].split('/')[0]
                                    print(f"File ID: {file_id}")
                                    
                                    # Try direct download URL
                                    download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
                                    print(f"Direct download URL: {download_url}")
                                    
                                    async with session.get(download_url) as resp:
                                        print(f"Direct download status: {resp.status}")
                                        if resp.status == 403:
                                            print("❌ File requires authentication or has restricted sharing")
                                            print("Solution: Make sure the file is shared publicly")
                        else:
                            print("❌ URL doesn't start with HTTP - might be a data URL or invalid")
                    else:
                        print("❌ No video URL found in record")
                else:
                    print("No records with video found")
            else:
                print(f"Airtable error: {response.status}")

if __name__ == "__main__":
    asyncio.run(debug_youtube())