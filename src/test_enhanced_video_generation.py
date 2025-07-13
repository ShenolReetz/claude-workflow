#!/usr/bin/env python3
"""Test enhanced video generation with reviews and ratings"""

import asyncio
import json
import sys
sys.path.append('/home/claude-workflow')

from mcp_servers.json2video_enhanced_server import JSON2VideoEnhancedMCPServer

async def test_enhanced_video_structure():
    """Test the enhanced video generation structure"""
    
    print("🎬 Testing Enhanced JSON2Video Generation")
    print("=" * 60)
    
    # Load config
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    # Test data with full product information
    test_record = {
        'VideoTitle': '🔥 Top 5 Car Amplifiers for INSANE Bass in 2025! 🚗',
        
        # Product 1 (shown as #5 in countdown)
        'ProductNo1Title': 'Rockford Fosgate T3000-1bdCP',
        'ProductNo1Description': 'Delivers 3000 watts of pure power with advanced thermal management and Class BD technology for the ultimate bass experience.',
        'ProductNo1ImageURL': 'https://images-na.ssl-images-amazon.com/images/I/71xKx1HLPVL._AC_SL1500_.jpg',
        'ProductNo1ReviewCount': '3456',
        'ProductNo1Rating': 4.7,
        
        # Product 2 (shown as #4)
        'ProductNo2Title': 'JL Audio XD1000/1v2',
        'ProductNo2Description': 'Compact monoblock with 1000W RMS, NexD2 switching technology, and studio-quality sound reproduction.',
        'ProductNo2ImageURL': 'https://images-na.ssl-images-amazon.com/images/I/81qKx1HLPVL._AC_SL1500_.jpg',
        'ProductNo2ReviewCount': '2891',
        'ProductNo2Rating': 4.8,
        
        # Product 3 (shown as #3)
        'ProductNo3Title': 'Kicker CXA1200.1',
        'ProductNo3Description': 'Powerful 1200W mono amp with FIT2 technology, optimized for precise bass control and efficiency.',
        'ProductNo3ImageURL': 'https://images-na.ssl-images-amazon.com/images/I/71qKx1HLPVL._AC_SL1500_.jpg',
        'ProductNo3ReviewCount': '5234',
        'ProductNo3Rating': 4.5,
        
        # Product 4 (shown as #2)
        'ProductNo4Title': 'Alpine MRV-M1200',
        'ProductNo4Description': 'Alpine excellence with 1200W RMS, variable bass boost, and sophisticated protection circuitry.',
        'ProductNo4ImageURL': 'https://images-na.ssl-images-amazon.com/images/I/61qKx1HLPVL._AC_SL1500_.jpg',
        'ProductNo4ReviewCount': '4123',
        'ProductNo4Rating': 4.6,
        
        # Product 5 (shown as #1 - WINNER)
        'ProductNo5Title': 'Skar Audio RP-2000.1D',
        'ProductNo5Description': 'The champion! 2000W RMS Class D monoblock with remote bass knob and competition-grade components.',
        'ProductNo5ImageURL': 'https://images-na.ssl-images-amazon.com/images/I/91qKx1HLPVL._AC_SL1500_.jpg',
        'ProductNo5ReviewCount': '12567',
        'ProductNo5Rating': 4.9,
    }
    
    # Initialize enhanced server
    server = JSON2VideoEnhancedMCPServer(config['json2video_api_key'])
    
    try:
        print("\n📋 Building enhanced video template...")
        movie_json, project_name = server.build_production_video_template(test_record)
        
        print(f"\n✨ Video Details:")
        print(f"   Project Name: {project_name}")
        print(f"   Resolution: {movie_json['resolution']}")
        print(f"   Quality: {movie_json['quality']}")
        print(f"   Total Scenes: {len(movie_json['scenes'])}")
        print(f"   Total Duration: 60 seconds")
        
        print("\n🎬 Scene Breakdown:")
        total_duration = 0
        for i, scene in enumerate(movie_json['scenes']):
            duration = scene['duration']
            total_duration += duration
            element_count = len(scene.get('elements', []))
            transition = scene.get('transition', {}).get('type', 'none')
            
            print(f"\n   Scene {i+1}: {scene['comment']}")
            print(f"   - Duration: {duration}s")
            print(f"   - Elements: {element_count}")
            print(f"   - Transition: {transition}")
            
            # Show key elements
            for element in scene.get('elements', []):
                if element['type'] == 'component':
                    component = element.get('component', '')
                    if 'counter' in str(element.get('settings', {})):
                        print(f"   - Review Counter Component")
                    elif 'rating' in str(element.get('settings', {})):
                        print(f"   - Star Rating Component")
                    elif 'badge' in str(element.get('settings', {})):
                        print(f"   - Winner Badge Component")
        
        print(f"\n⏱️ Total Duration: {total_duration} seconds")
        
        # Analyze product scenes
        print("\n📊 Product Analysis:")
        for i in range(5, 0, -1):
            if f'ProductNo{i}Title' in test_record:
                reviews = test_record.get(f'ProductNo{i}ReviewCount', '0')
                rating = test_record.get(f'ProductNo{i}Rating', 0)
                print(f"   #{6-i}: {test_record[f'ProductNo{i}Title']}")
                print(f"      Reviews: {reviews} | Rating: {rating}⭐")
        
        # Save template for inspection
        output_file = '/home/claude-workflow/test_output/enhanced_video_template.json'
        import os
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(movie_json, f, indent=2)
        print(f"\n💾 Template saved to: {output_file}")
        
        # Test API connectivity
        print("\n🔗 Testing API connection...")
        test_response = await server.client.get(
            f"{server.base_url}/movies",
            headers=server.headers
        )
        if test_response.status_code == 200:
            print("✅ API connection successful")
        else:
            print(f"❌ API connection failed: {test_response.status_code}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await server.close()
        print("\n✅ Test completed")

if __name__ == "__main__":
    asyncio.run(test_enhanced_video_structure())