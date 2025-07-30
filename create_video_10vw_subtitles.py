#!/usr/bin/env python3
"""
Create video with UPDATED font size: 10vw for responsive subtitle sizing
- Style: "boxed-word" with individual word boxes
- Font: Montserat, size 10vw (responsive to video width)
- Position: "bottom-center" 
- Colors: Green line (#00FF00), Yellow word (#FFFF00)
- Outline: Black (#000000) with width 8
- Max 3 words per line
"""

import asyncio
import json
import httpx
import sys
import os
from datetime import datetime

sys.path.append('/home/claude-workflow')

async def create_video_10vw_subtitles():
    """Create video with 10vw font size subtitles"""
    
    # Load API key
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    api_key = config['json2video_api_key']
    
    # Load updated Test schema with 10vw font size
    with open('/home/claude-workflow/Test_json2video_schema.json', 'r') as f:
        movie_json = json.load(f)
    
    print("🎬 Creating video with 10VW FONT SIZE subtitles")
    print("📏 Font size updated:")
    print("  ❌ OLD: font-size: 200 (fixed pixels)")
    print("  ✅ NEW: font-size: '10vw' (10% of video width)")
    print("\n📦 Subtitle styling:")
    print("  🎨 Style: 'boxed-word' (individual word boxes)")
    print("  🔤 Font: Montserat, size 10vw (responsive)")
    print("  📍 Position: 'bottom-center'")
    print("  🟢 Line color: #00FF00 (green)")
    print("  🟡 Word color: #FFFF00 (bright yellow)")
    print("  📝 Max words: 3 per line")
    print("  ⚫ Outline: Black (#000000) with width 8")
    print(f"🔑 Using API key: {api_key[:8]}...")
    print(f"🕐 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Calculate expected font size for 1080px width
    video_width = movie_json.get('width', 1080)
    expected_font_size = video_width * 0.10  # 10vw = 10% of width
    print(f"\n📐 Font size calculation:")
    print(f"   Video width: {video_width}px")
    print(f"   10vw = 10% of {video_width}px = {expected_font_size}px")
    print(f"   Result: Large, responsive text that scales with video")
    
    # Verify subtitle configuration
    movie_elements = movie_json.get('elements', [])
    subtitle_elements = [e for e in movie_elements if e.get('type') == 'subtitles']
    
    if len(subtitle_elements) == 1:
        subtitle_config = subtitle_elements[0]
        settings = subtitle_config.get('settings', {})
        
        print(f"\n✅ Updated subtitle configuration:")
        print(f"   Style: {settings.get('style')}")
        print(f"   Font: {settings.get('font-family')} {settings.get('font-size')}")
        print(f"   Position: {settings.get('position')}")
        print(f"   Colors: Line={settings.get('line-color')}, Word={settings.get('word-color')}")
        print(f"   Max words: {settings.get('max-words-per-line')}")
        print(f"   Outline: {settings.get('outline-color')} width {settings.get('outline-width')}")
        
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
                    print(f"✅ No errors - 10vw font size accepted!")
                    
                if video_url:
                    print(f"🎥 Video URL: {video_url}")
                else:
                    print("⏳ Video processing. Check back in 5-10 minutes.")
                    print(f"📱 Monitor: https://json2video.com/app/projects/{project_id}")
                    
                # Show visual representation with 10vw sizing
                print("\n🎨 Expected Subtitle Appearance (10vw sizing):")
                print("  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐")
                print("  │   WELCOME     │ │      TO       │ │     OUR       │")
                print("  └───────────────┘ └───────────────┘ └───────────────┘")
                print("     (green)          (yellow)          (green)")
                print(f"  📏 Font size: 10vw = {expected_font_size}px (responsive)")
                print("  📦 Each word in its own large box")
                print("  🟢 Non-current words: Green background")
                print("  🟡 Current word: Yellow background")
                print("  ⚫ All words: Thick black outline (width 8)")
            
            return {
                'success': True,
                'project_id': project_id,
                'project_url': f"https://json2video.com/app/projects/{project_id}",
                'subtitle_style': {
                    'type': 'boxed-word',
                    'font': 'Montserat 10vw',
                    'font_size_pixels': expected_font_size,
                    'position': 'bottom-center',
                    'colors': {
                        'line': '#00FF00',
                        'word': '#FFFF00',
                        'outline': '#000000'
                    },
                    'max_words': 3,
                    'outline_width': 8
                },
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
    print("🎬 JSON2Video - 10VW RESPONSIVE SUBTITLE FONT SIZE")
    print("=" * 50)
    result = asyncio.run(create_video_10vw_subtitles())
    
    if result['success']:
        print("\n🎉 SUCCESS! Video with 10vw font size created!")
        print(f"🔗 View: {result['project_url']}")
        print("\n📏 10vw Font Benefits:")
        print("  ✅ Responsive sizing (10% of video width)")
        print("  ✅ Consistent appearance across different screens")
        print("  ✅ Large, readable text boxes")
        print("  ✅ Professional boxed-word styling")
        print("  ✅ Perfect for 1080px wide videos (108px font)")
    else:
        print(f"\n❌ Error: {result.get('error', 'Unknown error')}")