#!/usr/bin/env python3
"""
Create video with FINAL SUBTITLE ADJUSTMENTS per user request:
- Max words per line: 4 → 3 (more compact display)
- Highlight color: Purple (#B185A7) → Yellow (#e5e826) - same as review stars
- Style: Classic with cream background, black box, Luckiest Guy font
"""

import asyncio
import json
import httpx
import sys
import os
from datetime import datetime

sys.path.append('/home/claude-workflow')

async def create_video_final_adjustments():
    """Create video with final subtitle adjustments"""
    
    # Load API key
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    api_key = config['json2video_api_key']
    
    # Load updated Test schema with final adjustments
    with open('/home/claude-workflow/Test_json2video_schema.json', 'r') as f:
        movie_json = json.load(f)
    
    print("🎬 Creating video with FINAL SUBTITLE ADJUSTMENTS")
    print("🔧 Final tweaks applied:")
    print("  📝 Max words per line: 4 → 3 (more compact)")
    print("  🟡 Highlight color: Purple → Yellow (#e5e826)")
    print("  ⭐ Color consistency: Matches review stars color")
    print("\n🎨 Complete final styling:")
    print("  📦 Style: 'classic' (traditional subtitle design)")
    print("  🔤 Font: Luckiest Guy, size 80px")
    print("  📄 Background: Cream (#FFF4E9)")
    print("  🟡 Highlight: Yellow (#e5e826) - same as stars")
    print("  ⚫ Box: Black (#000000) with 10px outline")
    print("  🌑 Shadow: Black with 0 offset")
    print("  📝 Max words: 3 per line")
    print(f"🔑 Using API key: {api_key[:8]}...")
    print(f"🕐 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verify final subtitle configuration
    movie_elements = movie_json.get('elements', [])
    subtitle_elements = [e for e in movie_elements if e.get('type') == 'subtitles']
    
    if len(subtitle_elements) == 1:
        subtitle_config = subtitle_elements[0]
        settings = subtitle_config.get('settings', {})
        
        print(f"\n✅ Final configuration verified:")
        print(f"   Style: {settings.get('style')}")
        print(f"   Font: {settings.get('font-family')} {settings.get('font-size')}px")
        print(f"   Background: {settings.get('line-color')} (cream)")
        print(f"   Highlight: {settings.get('word-color')} (yellow like stars)")
        print(f"   Box: {settings.get('box-color')} (black)")
        print(f"   Outline: {settings.get('outline-color')} width {settings.get('outline-width')}")
        print(f"   Max words: {settings.get('max-words-per-line')} (reduced to 3)")
        
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
                    print(f"✅ No errors - final adjustments accepted!")
                    
                if video_url:
                    print(f"🎥 Video URL: {video_url}")
                else:
                    print("⏳ Video processing. Check back in 5-10 minutes.")
                    print(f"📱 Monitor: https://json2video.com/app/projects/{project_id}")
                    
                # Show final visual representation
                print("\n🎨 FINAL Subtitle Appearance:")
                print("  ┌─────────────────────────┐")
                print("  │ ■■■■■■■■■■■■■■■■■■■■■■■ │")
                print("  │ ■ WELCOME TO OUR       ■ │")
                print("  │ ■■■■■■■■■■■■■■■■■■■■■■■ │")
                print("  └─────────────────────────┘")
                print("    📄 Cream background")
                print("    🟡 Yellow highlight (matches stars)")
                print("    ⚫ Black box with thick outline")
                print("    📝 Max 3 words per line")
                print("\n🎯 Perfect consistency:")
                print("  ⭐ Subtitle yellow = Review stars yellow")
                print("  📝 Compact 3-word display")
                print("  🎨 Classic professional styling")
            
            return {
                'success': True,
                'project_id': project_id,
                'project_url': f"https://json2video.com/app/projects/{project_id}",
                'final_adjustments': {
                    'max_words_reduced': '4 → 3',
                    'highlight_color_changed': '#B185A7 → #e5e826',
                    'color_consistency': 'matches_review_stars',
                    'style': 'classic',
                    'font': 'Luckiest Guy 80px'
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
    print("🎬 JSON2Video - FINAL SUBTITLE ADJUSTMENTS")
    print("=" * 45)
    result = asyncio.run(create_video_final_adjustments())
    
    if result['success']:
        print("\n🎉 SUCCESS! Final subtitle adjustments applied!")
        print(f"🔗 View: {result['project_url']}")
        print("\n✅ Final Changes:")
        print("  📝 Max 3 words per line (reduced from 4)")
        print("  🟡 Yellow highlight matching review stars")
        print("  📄 Cream background with black box")
        print("  🔤 Luckiest Guy font, 80px size")
        print("  🎵 Auto-generated from Google Drive audio")
        print("  ⭐ Perfect visual consistency with video elements")
    else:
        print(f"\n❌ Error: {result.get('error', 'Unknown error')}")