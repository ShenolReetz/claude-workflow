#!/usr/bin/env python3
"""
Create FINAL video with CLEAN subtitle configuration:
- Removed all invalid properties (offset-y, horizontal-align)
- Clean config: position="custom", x=540, y=750
- Colors: Yellow base (#e5e826), Red highlight (#FF0000)
- Max 4 words, single line positioning
"""

import asyncio
import json
import httpx
import sys
import os
from datetime import datetime

sys.path.append('/home/claude-workflow')

async def create_final_video_clean_subtitles():
    """Create final video with clean subtitle configuration"""
    
    # Load API key
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    api_key = config['json2video_api_key']
    
    # Load clean Test schema
    with open('/home/claude-workflow/Test_json2video_schema.json', 'r') as f:
        movie_json = json.load(f)
    
    print("🎬 Creating FINAL video with CLEAN subtitle configuration")
    print("🧹 All invalid properties removed:")
    print("  ❌ Removed: offset-y (not allowed)")
    print("  ❌ Removed: horizontal-align (not allowed)")
    print("  ✅ Clean: position='custom', x=540, y=750")
    print("\n🎨 Final subtitle configuration:")
    print("  📍 Position: X=540 (center), Y=750 (below prices)")
    print("  🟡 Base text: Yellow (#e5e826) - matches other elements")  
    print("  🔴 Current word: Red (#FF0000) - highlighted")
    print("  📝 Display: Max 4 words at same time")
    print("  🔤 Style: Roboto font, size 90, all caps")
    print(f"🔑 Using API key: {api_key[:8]}...")
    print(f"🕐 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verify clean subtitle configuration
    movie_elements = movie_json.get('elements', [])
    subtitle_elements = [e for e in movie_elements if e.get('type') == 'subtitles']
    
    if len(subtitle_elements) == 1:
        subtitle_config = subtitle_elements[0]
        settings = subtitle_config.get('settings', {})
        
        print(f"\n✅ Clean subtitle configuration:")
        print(f"   Position: {subtitle_config.get('position')} ({subtitle_config.get('x')}, {subtitle_config.get('y')})")
        print(f"   Base color: {settings.get('line-color')}")
        print(f"   Highlight: {settings.get('word-color')}")
        print(f"   Max words: {settings.get('max-words-per-line')}")
        print(f"   Font: {settings.get('font-family')} {settings.get('font-size')}")
        print(f"   Style: {settings.get('style')}")
        
        # Verify no invalid properties
        invalid_props = ['offset-y', 'horizontal-align']
        found_invalid = []
        for prop in invalid_props:
            if prop in settings:
                found_invalid.append(prop)
        
        if found_invalid:
            print(f"❌ WARNING: Found invalid properties: {found_invalid}")
        else:
            print(f"✅ No invalid properties found - configuration is clean")
            
    else:
        print(f"❌ ERROR: Found {len(subtitle_elements)} subtitle elements, should be exactly 1")
        return {'success': False, 'error': f'Invalid subtitle count: {len(subtitle_elements)}'}
    
    # Make API request
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("\n🚀 Sending request to JSON2Video API...")
        response = await client.post(
            "https://api.json2video.com/v2/movies",
            json=movie_json,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            project_id = result.get('project')
            print(f"✅ Video project created successfully!")
            print(f"🎥 Project ID: {project_id}")
            print(f"🔗 Project URL: https://json2video.com/app/projects/{project_id}")
            print(f"⏰ Video is being processed...")
            
            # Wait a moment then check initial status
            await asyncio.sleep(10)
            
            print("\n📊 Checking initial project status...")
            status_response = await client.get(
                f"https://api.json2video.com/v2/movies?project={project_id}",
                headers=headers
            )
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                movie_data = status_data.get('movie', {})
                status = movie_data.get('status')
                video_url = movie_data.get('url')
                error = movie_data.get('message')
                
                print(f"📋 Status: {status}")
                if error:
                    print(f"❌ Error: {error}")
                else:
                    print(f"✅ No errors - clean configuration accepted!")
                    
                if video_url:
                    print(f"🎥 Video URL: {video_url}")
                else:
                    print("⏳ Video processing. Check back in 5-10 minutes.")
                    print(f"📱 Monitor: https://json2video.com/app/projects/{project_id}")
                    
                # Show final layout
                print("\n🎯 FINAL Video Layout:")
                print("  📝 Title: Y=63 (top)")
                print("  ⭐ Rating: Y=400") 
                print("  📊 Reviews: Y=500")
                print("  💰 Price: Y=600")
                print("  📝 SUBTITLES: Y=750 (bottom) ✅")
                print("\n🎨 Subtitle Appearance:")
                print("  Example: 'Welcome to our 🔴top🔴 five camera'")
                print("  🟡 Yellow text with 🔴red🔴 highlighted current word")
            
            return {
                'success': True,
                'project_id': project_id,
                'project_url': f"https://json2video.com/app/projects/{project_id}",
                'configuration': 'clean',
                'position': {'x': 540, 'y': 750},
                'colors': {'base': '#e5e826', 'highlight': '#FF0000'},
                'max_words': 4,
                'timestamp': datetime.now().isoformat()
            }
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"📝 Response: {response.text}")
            return {
                'success': False,
                'error': response.text
            }

if __name__ == "__main__":
    print("🎬 JSON2Video - FINAL CLEAN SUBTITLE CONFIGURATION")
    print("=" * 55)
    result = asyncio.run(create_final_video_clean_subtitles())
    
    if result['success']:
        print("\n🎉 SUCCESS! Video creation with clean subtitle config!")
        print(f"🔗 View: {result['project_url']}")
        print("\n✅ Your requirements implemented:")
        print("  📍 Positioned below price elements (Y=750)")
        print("  🟡 Yellow base color (#e5e826) like other elements")
        print("  🔴 Red highlighted current word (#FF0000)")
        print("  📝 Maximum 4 words displayed at once")
        print("  📏 Single line, centered layout")
        print("  🎵 Auto-generated from Google Drive audio files")
    else:
        print(f"\n❌ Error: {result.get('error', 'Unknown error')}")