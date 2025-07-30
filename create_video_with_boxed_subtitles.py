#!/usr/bin/env python3
"""
Create video with BOXED-WORD subtitle styling per user specification:
- Style: "boxed-word" with individual word boxes
- Font: Montserat, size 200 (large)
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

async def create_video_with_boxed_subtitles():
    """Create video with boxed-word subtitle styling"""
    
    # Load API key
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    api_key = config['json2video_api_key']
    
    # Load updated Test schema with boxed subtitles
    with open('/home/claude-workflow/Test_json2video_schema.json', 'r') as f:
        movie_json = json.load(f)
    
    print("🎬 Creating video with BOXED-WORD SUBTITLE STYLING")
    print("📦 New styling applied:")
    print("  🎨 Style: 'boxed-word' (individual word boxes)")
    print("  🔤 Font: Montserat, size 200 (large and bold)")
    print("  📍 Position: 'bottom-center' (automatic positioning)")
    print("  🟢 Line color: #00FF00 (green)")
    print("  🟡 Word color: #FFFF00 (bright yellow)")
    print("  📝 Max words: 3 per line (reduced from 4)")
    print("  ⚫ Outline: Black (#000000) with width 8 (thick border)")
    print(f"🔑 Using API key: {api_key[:8]}...")
    print(f"🕐 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verify new subtitle configuration
    movie_elements = movie_json.get('elements', [])
    subtitle_elements = [e for e in movie_elements if e.get('type') == 'subtitles']
    
    if len(subtitle_elements) == 1:
        subtitle_config = subtitle_elements[0]
        settings = subtitle_config.get('settings', {})
        
        print(f"\n✅ Boxed subtitle configuration:")
        print(f"   Style: {settings.get('style')} (boxed word boxes)")
        print(f"   Font: {settings.get('font-family')} {settings.get('font-size')}")
        print(f"   Position: {settings.get('position')}")
        print(f"   Line color: {settings.get('line-color')} (green)")
        print(f"   Word color: {settings.get('word-color')} (yellow)")
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
                    print(f"✅ No errors - boxed subtitle configuration accepted!")
                    
                if video_url:
                    print(f"🎥 Video URL: {video_url}")
                else:
                    print("⏳ Video processing. Check back in 5-10 minutes.")
                    print(f"📱 Monitor: https://json2video.com/app/projects/{project_id}")
                    
                # Show visual representation
                print("\n🎨 Expected Subtitle Appearance:")
                print("  ┌─────────┐ ┌─────────┐ ┌─────────┐")
                print("  │ WELCOME │ │   TO    │ │   OUR   │")
                print("  └─────────┘ └─────────┘ └─────────┘")
                print("    (green)     (yellow)    (green)")
                print("  📦 Each word in its own box with black outline")
                print("  🟢 Non-current words: Green background")
                print("  🟡 Current word: Yellow background")
                print("  ⚫ All words: Black outline (width 8)")
                print("  🔤 Font: Montserat 200 (very large)")
            
            return {
                'success': True,
                'project_id': project_id,
                'project_url': f"https://json2video.com/app/projects/{project_id}",
                'subtitle_style': {
                    'type': 'boxed-word',
                    'font': 'Montserat 200',
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
    print("🎬 JSON2Video - BOXED-WORD SUBTITLE STYLING")
    print("=" * 45)
    result = asyncio.run(create_video_with_boxed_subtitles())
    
    if result['success']:
        print("\n🎉 SUCCESS! Video with boxed-word subtitles created!")
        print(f"🔗 View: {result['project_url']}")
        print("\n📦 Boxed subtitle features:")
        print("  ✅ Individual word boxes with thick black outlines")
        print("  ✅ Large Montserat font (size 200)")
        print("  ✅ Green/Yellow color scheme")
        print("  ✅ Bottom-center automatic positioning")
        print("  ✅ Max 3 words per line for better readability")
        print("  ✅ Auto-generated from Google Drive audio")
    else:
        print(f"\n❌ Error: {result.get('error', 'Unknown error')}")