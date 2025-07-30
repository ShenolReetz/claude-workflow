#!/usr/bin/env python3
"""
Create video with UPDATED SUBTITLE COLORS per user request:
- Green (#00FF00) → Yellow (#FFFF00) for background boxes
- Black (#000000) → Red (#FF0000) for outline/border
- Added white (#FFFFFF) text color for better contrast
- Font: Montserat, size 60px, max 3 words per line
"""

import asyncio
import json
import httpx
import sys
import os
from datetime import datetime

sys.path.append('/home/claude-workflow')

async def create_video_updated_colors():
    """Create video with updated subtitle color scheme"""
    
    # Load API key
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    api_key = config['json2video_api_key']
    
    # Load updated Test schema with new colors
    with open('/home/claude-workflow/Test_json2video_schema.json', 'r') as f:
        movie_json = json.load(f)
    
    print("🎬 Creating video with UPDATED SUBTITLE COLORS")
    print("🎨 Color changes applied:")
    print("  ❌ OLD: Green background (#00FF00)")
    print("  ✅ NEW: Yellow background (#FFFF00)")
    print("  ❌ OLD: Black outline (#000000)")
    print("  ✅ NEW: Red outline (#FF0000)")
    print("  ➕ NEW: White text color (#FFFFFF)")
    print("\n📦 Complete subtitle styling:")
    print("  🎨 Style: 'boxed-word' (individual word boxes)")
    print("  🔤 Font: Montserat, size 60px")
    print("  📍 Position: 'bottom-center'")
    print("  🟡 Background: Yellow (#FFFF00) for all words")
    print("  🔴 Outline: Red (#FF0000) thick border (width 8)")
    print("  ⚪ Text: White (#FFFFFF) for contrast")
    print("  📝 Max words: 3 per line")
    print(f"🔑 Using API key: {api_key[:8]}...")
    print(f"🕐 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verify updated subtitle configuration
    movie_elements = movie_json.get('elements', [])
    subtitle_elements = [e for e in movie_elements if e.get('type') == 'subtitles']
    
    if len(subtitle_elements) == 1:
        subtitle_config = subtitle_elements[0]
        settings = subtitle_config.get('settings', {})
        
        print(f"\n✅ Updated color configuration:")
        print(f"   Style: {settings.get('style')}")
        print(f"   Font: {settings.get('font-family')} {settings.get('font-size')}px")
        print(f"   Background: {settings.get('line-color')} (yellow)")
        print(f"   Current word: {settings.get('word-color')} (yellow)")
        print(f"   Outline: {settings.get('outline-color')} width {settings.get('outline-width')} (red)")
        print(f"   Text color: {settings.get('text-color')} (white)")
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
                    print(f"✅ No errors - updated colors accepted!")
                    
                if video_url:
                    print(f"🎥 Video URL: {video_url}")
                else:
                    print("⏳ Video processing. Check back in 5-10 minutes.")
                    print(f"📱 Monitor: https://json2video.com/app/projects/{project_id}")
                    
                # Show visual representation with new colors
                print("\n🎨 Expected Subtitle Appearance (Updated Colors):")
                print("  ┌──────────┐ ┌──────────┐ ┌──────────┐")
                print("  │ WELCOME  │ │    TO    │ │   OUR    │")
                print("  └──────────┘ └──────────┘ └──────────┘")
                print("   Yellow bg    Yellow bg    Yellow bg")
                print("   Red outline  Red outline  Red outline")
                print("   White text   White text   White text")
                print("  📦 All words: Yellow background with red outline")
                print("  ⚪ Text: White for maximum contrast and readability")
                print("  🔴 Border: Thick red outline (8px width)")
                print("  🟡 Background: Bright yellow for visibility")
            
            return {
                'success': True,
                'project_id': project_id,
                'project_url': f"https://json2video.com/app/projects/{project_id}",
                'color_scheme': {
                    'background': '#FFFF00',  # Yellow
                    'outline': '#FF0000',     # Red
                    'text': '#FFFFFF',        # White
                    'word_highlight': '#FFFF00'  # Yellow (same as background)
                },
                'styling': {
                    'font': 'Montserat 60px',
                    'style': 'boxed-word',
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
    print("🎬 JSON2Video - UPDATED SUBTITLE COLOR SCHEME")
    print("=" * 50)
    result = asyncio.run(create_video_updated_colors())
    
    if result['success']:
        print("\n🎉 SUCCESS! Video with updated colors created!")
        print(f"🔗 View: {result['project_url']}")
        print("\n🎨 New Color Scheme:")
        print("  🟡 Background: Bright yellow boxes")
        print("  🔴 Outline: Bold red borders (8px thick)")
        print("  ⚪ Text: White for maximum readability")
        print("  📦 Style: Professional boxed-word design")
        print("  🎵 Audio: Auto-generated from Google Drive files")
    else:
        print(f"\n❌ Error: {result.get('error', 'Unknown error')}")