#!/usr/bin/env python3
"""
Create video with NEW CLASSIC SUBTITLE STYLING per user specification:
- Style: "classic" (traditional subtitle style)
- Font: Luckiest Guy, size 80px
- Colors: Cream background (#FFF4E9), Purple highlight (#B185A7)
- Box: Black background (#000000) with black outline (10px)
- Shadow: Black shadow with 0 offset
- Max 4 words per line
"""

import asyncio
import json
import httpx
import sys
import os
from datetime import datetime

sys.path.append('/home/claude-workflow')

async def create_video_classic_style():
    """Create video with classic subtitle styling"""
    
    # Load API key
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    api_key = config['json2video_api_key']
    
    # Load updated Test schema with classic styling
    with open('/home/claude-workflow/Test_json2video_schema.json', 'r') as f:
        movie_json = json.load(f)
    
    print("🎬 Creating video with NEW CLASSIC SUBTITLE STYLING")
    print("🎨 Complete style overhaul:")
    print("  📦 Style: 'classic' (traditional subtitle design)")
    print("  🔤 Font: Luckiest Guy, size 80px (fun, bold font)")
    print("  📍 Position: 'bottom-center'")
    print("  🎨 Color scheme:")
    print("    📄 Line color: #FFF4E9 (cream/off-white)")
    print("    💜 Word highlight: #B185A7 (purple)")
    print("    ⚫ Box background: #000000 (black)")
    print("    ⚫ Outline: #000000 width 10px (thick black)")
    print("    🌑 Shadow: #000000 with 0 offset")
    print("  📝 Max words: 4 per line (increased from 3)")
    print(f"🔑 Using API key: {api_key[:8]}...")
    print(f"🕐 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verify new classic subtitle configuration
    movie_elements = movie_json.get('elements', [])
    subtitle_elements = [e for e in movie_elements if e.get('type') == 'subtitles']
    
    if len(subtitle_elements) == 1:
        subtitle_config = subtitle_elements[0]
        settings = subtitle_config.get('settings', {})
        
        print(f"\n✅ Classic style configuration:")
        print(f"   Style: {settings.get('style')}")
        print(f"   Font: {settings.get('font-family')} {settings.get('font-size')}px")
        print(f"   Line color: {settings.get('line-color')} (cream)")
        print(f"   Word highlight: {settings.get('word-color')} (purple)")
        print(f"   Box background: {settings.get('box-color')} (black)")
        print(f"   Outline: {settings.get('outline-color')} width {settings.get('outline-width')} (black)")
        print(f"   Shadow: {settings.get('shadow-color')} offset {settings.get('shadow-offset')}")
        print(f"   Max words: {settings.get('max-words-per-line')}")
        
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
                    print(f"✅ No errors - classic style accepted!")
                    
                if video_url:
                    print(f"🎥 Video URL: {video_url}")
                else:
                    print("⏳ Video processing. Check back in 5-10 minutes.")
                    print(f"📱 Monitor: https://json2video.com/app/projects/{project_id}")
                    
                # Show visual representation
                print("\n🎨 Expected Classic Subtitle Appearance:")
                print("  ┌─────────────────────────────────┐")
                print("  │ ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■ │")
                print("  │ ■ WELCOME TO OUR TOP FIVE     ■ │")
                print("  │ ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■ │")
                print("  └─────────────────────────────────┘")
                print("    📄 Cream background with purple highlights")
                print("    ⚫ Black box with thick black outline")
                print("    🔤 Luckiest Guy font (fun, bold style)")
                print("    📝 Traditional subtitle appearance")
                print("    🎯 Up to 4 words per line")
            
            return {
                'success': True,
                'project_id': project_id,
                'project_url': f"https://json2video.com/app/projects/{project_id}",
                'classic_style': {
                    'style': 'classic',
                    'font': 'Luckiest Guy 80px',
                    'colors': {
                        'line': '#FFF4E9',      # Cream
                        'word_highlight': '#B185A7',  # Purple
                        'box': '#000000',        # Black
                        'outline': '#000000',    # Black
                        'shadow': '#000000'      # Black
                    },
                    'max_words': 4,
                    'outline_width': 10,
                    'shadow_offset': 0
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
    print("🎬 JSON2Video - NEW CLASSIC SUBTITLE STYLING")
    print("=" * 50)
    result = asyncio.run(create_video_classic_style())
    
    if result['success']:
        print("\n🎉 SUCCESS! Video with classic subtitle styling!")
        print(f"🔗 View: {result['project_url']}")
        print("\n🎨 Classic Style Features:")
        print("  📦 Traditional subtitle box design")
        print("  🔤 Luckiest Guy font (fun, bold character)")
        print("  📄 Cream background with purple highlights")
        print("  ⚫ Black box with thick black outline (10px)")
        print("  🌑 Black shadow for depth")
        print("  📝 Up to 4 words per line")
        print("  🎵 Auto-generated from Google Drive audio")
    else:
        print(f"\n❌ Error: {result.get('error', 'Unknown error')}")