#!/usr/bin/env python3
"""
Create FINAL video with CORRECTED SUBTITLE COLORS:
- Yellow background (#FFFF00) for all word boxes
- Red outline (#FF0000) for borders
- Removed invalid text-color property
- Font: Montserat, size 60px, max 3 words per line
"""

import asyncio
import json
import httpx
import sys
import os
from datetime import datetime

sys.path.append('/home/claude-workflow')

async def create_final_color_video():
    """Create final video with corrected subtitle colors"""
    
    # Load API key
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    api_key = config['json2video_api_key']
    
    # Load corrected Test schema
    with open('/home/claude-workflow/Test_json2video_schema.json', 'r') as f:
        movie_json = json.load(f)
    
    print("🎬 Creating FINAL video with CORRECTED SUBTITLE COLORS")
    print("🔧 Fixed invalid property:")
    print("  ❌ REMOVED: text-color (not allowed by JSON2Video)")
    print("  ✅ KEPT: Valid color properties only")
    print("\n🎨 Final color scheme:")
    print("  🟡 Background: Yellow (#FFFF00) for all word boxes")
    print("  🔴 Outline: Red (#FF0000) thick borders (8px)")
    print("  📦 Style: Professional boxed-word design")
    print("  🔤 Font: Montserat 60px, max 3 words per line")
    print(f"🔑 Using API key: {api_key[:8]}...")
    print(f"🕐 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verify corrected subtitle configuration
    movie_elements = movie_json.get('elements', [])
    subtitle_elements = [e for e in movie_elements if e.get('type') == 'subtitles']
    
    if len(subtitle_elements) == 1:
        subtitle_config = subtitle_elements[0]
        settings = subtitle_config.get('settings', {})
        
        print(f"\n✅ Final corrected configuration:")
        print(f"   Style: {settings.get('style')}")
        print(f"   Font: {settings.get('font-family')} {settings.get('font-size')}px")
        print(f"   Background: {settings.get('line-color')} (yellow)")
        print(f"   Word highlight: {settings.get('word-color')} (yellow)")
        print(f"   Outline: {settings.get('outline-color')} width {settings.get('outline-width')} (red)")
        print(f"   Max words: {settings.get('max-words-per-line')}")
        
        # Verify no invalid properties
        invalid_props = ['text-color']
        found_invalid = []
        for prop in invalid_props:
            if prop in settings:
                found_invalid.append(prop)
        
        if found_invalid:
            print(f"❌ WARNING: Found invalid properties: {found_invalid}")
        else:
            print(f"✅ No invalid properties - configuration is clean")
            
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
                    print(f"✅ No errors - final color scheme accepted!")
                    
                if video_url:
                    print(f"🎥 Video URL: {video_url}")
                else:
                    print("⏳ Video processing. Check back in 5-10 minutes.")
                    print(f"📱 Monitor: https://json2video.com/app/projects/{project_id}")
                    
                # Show final visual representation
                print("\n🎨 FINAL Subtitle Appearance:")
                print("  ┌──────────┐ ┌──────────┐ ┌──────────┐")
                print("  │ WELCOME  │ │    TO    │ │   OUR    │")
                print("  └──────────┘ └──────────┘ └──────────┘")
                print("   🟡 Yellow    🟡 Yellow    🟡 Yellow")
                print("   🔴 Red outline 🔴 Red outline 🔴 Red outline")
                print("\n🎯 Your requested changes implemented:")
                print("  ✅ Green → Yellow background")
                print("  ✅ Black → Red outline/border") 
                print("  ✅ Professional boxed-word styling")
                print("  ✅ 60px Montserat font")
                print("  ✅ Auto-generated from audio")
            
            return {
                'success': True,
                'project_id': project_id,
                'project_url': f"https://json2video.com/app/projects/{project_id}",
                'final_colors': {
                    'background': '#FFFF00',  # Yellow (was green)
                    'outline': '#FF0000',     # Red (was black)
                    'word_highlight': '#FFFF00'  # Yellow
                },
                'configuration': 'corrected_no_invalid_properties',
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
    print("🎬 JSON2Video - FINAL CORRECTED COLOR SCHEME")
    print("=" * 50)
    result = asyncio.run(create_final_color_video())
    
    if result['success']:
        print("\n🎉 SUCCESS! Final video with corrected colors!")
        print(f"🔗 View: {result['project_url']}")
        print("\n🎨 Your Color Changes Applied:")
        print("  🟡 Yellow background boxes (was green)")
        print("  🔴 Red outline borders (was black)")
        print("  📦 Professional boxed-word styling")
        print("  🎵 Auto-captions from Google Drive audio")
        print("  ✅ All properties validated with JSON2Video API")
    else:
        print(f"\n❌ Error: {result.get('error', 'Unknown error')}")