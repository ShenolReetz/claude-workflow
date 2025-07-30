#!/usr/bin/env python3
"""
Test corrected JSON2Video template with deprecated properties removed
"""

import json
import asyncio
from mcp_servers.json2video_enhanced_server_v2 import JSON2VideoEnhancedMCPServerV2

async def test_corrected_video():
    """Generate a new test video with corrected template"""
    
    # Test data that matches the working reference
    test_data = {
        'VideoTitle': 'Top 5 Tech Products That Will Blow Your Mind - Schema Fixed',
        'VideoDescription': 'Check out these amazing tech finds with corrected schema!',
        'ProductNo1Title': '#1 Revolutionary AI Smartphone 🏆',
        'ProductNo1Rating': 5,
        'ProductNo1Reviews': 2847,
        'ProductNo1Price': 999,
        'ProductNo1Photo': 'https://drive.google.com/uc?id=1s5J3T82ISC3P6COkFjenhOT58JACwSfD&export=download',
        'ProductNo2Title': '#2 Wireless Gaming Headset Pro',
        'ProductNo2Rating': 5,
        'ProductNo2Reviews': 1923,
        'ProductNo2Price': 199,
        'ProductNo2Photo': 'https://drive.google.com/uc?id=10-vElXFcVhVU5FDJUEGdh4I_ZziDN2lJ&export=download',
        'ProductNo3Title': '#3 Ultra-Fast SSD Drive',
        'ProductNo3Rating': 5,
        'ProductNo3Reviews': 1456,
        'ProductNo3Price': 149,
        'ProductNo3Photo': 'https://drive.google.com/uc?id=1wQYvUpZsCLGx8A2o90cTcO88dSsXJnFE&export=download',
        'ProductNo4Title': '#4 Smart Home Security Camera',
        'ProductNo4Rating': 4,
        'ProductNo4Reviews': 1234,
        'ProductNo4Price': 89,
        'ProductNo4Photo': 'https://drive.google.com/uc?id=13VuwBBsIsv6gLYoiS3q6XfoRvVZGgQpZ&export=download',
        'ProductNo5Title': '#5 Portable Bluetooth Speaker',
        'ProductNo5Rating': 4,
        'ProductNo5Reviews': 987,
        'ProductNo5Price': 49,
        'ProductNo5Photo': 'https://drive.google.com/uc?id=1W7eRtz9cxkAOoAOF-5N7oc013YsOvSuX&export=download'
    }
    
    # Create corrected template based on working reference
    corrected_template = {
        "width": 1080,
        "scenes": [
            {
                "duration": 5,
                "comment": "Intro",
                "cache": True,
                "id": "intro_scene",
                "transition": {"duration": 0.5, "style": "smoothright"},
                "elements": [
                    {
                        "x": 0, "y": 0, "zoom": 5,
                        "id": "intro_bg",
                        "type": "image",
                        "src": test_data['ProductNo1Photo']
                    },
                    {
                        "settings": {
                            "color": "#e1da19",
                            "font-size": "6.5vw"
                        },
                        "cache": True,
                        "x": 2, "width": 1078, "y": 63,
                        "style": "003",
                        "id": "intro_title",
                        "position": "custom",
                        "text": test_data['VideoTitle'],
                        "type": "text",
                        "height": 282
                    },
                    {
                        "settings": {
                            "max-words-per-line": 4,
                            "font-size": 100,
                            "style": "classic-progressive",
                            "font-family": "Roboto",
                            "all-caps": True,
                            "outline-width": -1
                        },
                        "language": "en-US",
                        "id": "intro_subtitles",
                        "type": "subtitles"
                    }
                ]
            },
            # Product 1 Scene
            {
                "duration": 9,
                "comment": "Product 1 - Winner",
                "cache": True,
                "id": "product_1_scene",
                "transition": {"duration": 0.5, "style": "slideright"},
                "elements": [
                    {
                        "x": 0, "y": 0, "zoom": 5,
                        "id": "product1_bg",
                        "type": "image",
                        "src": test_data['ProductNo1Photo']
                    },
                    {
                        "settings": {
                            "color": "#e1da19",
                            "font-size": "6.5vw",
                            "font-family": "Roboto"
                        },
                        "cache": True,
                        "fade-out": 1, "fade-in": 1, "start": 1,
                        "type": "text", "duration": 7,
                        "x": 2, "width": 1078, "y": 63,
                        "style": "003",
                        "id": "product1_title",
                        "position": "custom",
                        "text": test_data['ProductNo1Title'],
                        "height": 282
                    },
                    {
                        "settings": {
                            "font-size": 100,
                            "style": "classic-progressive",
                            "font-family": "Roboto",
                            "all-caps": True,
                            "outline-width": -1
                        },
                        "language": "en-US",
                        "id": "product1_subtitles",
                        "type": "subtitles"
                    },
                    {
                        "duration": 7,
                        "settings": {
                            "rating": {
                                "symbol": "star",
                                "size": "8vw",
                                "color": "#e5e826",
                                "horizontal-align": "left",
                                "off-color": "rgba(255,255,255,0.1)",
                                "value": str(test_data['ProductNo1Rating'])
                            }
                        },
                        "component": "advanced/070",
                        "cache": True,
                        "fade-out": 1, "fade-in": 1, "start": 1,
                        "x": 120, "y": 600,
                        "id": "product1_rating",
                        "position": "custom",
                        "type": "component"
                    },
                    {
                        "duration": 7,
                        "settings": {
                            "counter": {
                                "duration": 3000,
                                "text-shadow": ".2vw .2vw .2vw rgba(50,50,50,0.5)",
                                "color": "white",
                                "font-size": "5vw",
                                "from": 0,
                                "font-family": "Anton",
                                "text": "__num__ Reviews",
                                "to": str(test_data['ProductNo1Reviews'])
                            }
                        },
                        "component": "advanced/060",
                        "fade-out": 1, "fade-in": 1,
                        "x": 120, "start": 1, "y": 750,
                        "id": "product1_reviews",
                        "position": "custom",
                        "type": "component"
                    },
                    {
                        "duration": 7,
                        "settings": {
                            "counter": {
                                "duration": 5000,
                                "color": "#e5e826",
                                "font-size": "10vw",
                                "from": 0,
                                "font-family": "Anton",
                                "text": "$__num__",
                                "to": str(test_data['ProductNo1Price'])
                            }
                        },
                        "component": "advanced/060",
                        "fade-out": 1, "fade-in": 1,
                        "width": 1000, "x": 360, "start": 1, "y": 850,
                        "id": "product1_price",
                        "position": "custom",
                        "type": "component"
                    }
                ]
            },
            # Outro Scene
            {
                "duration": 5,
                "comment": "Outro",
                "cache": True,
                "id": "outro_scene",
                "transition": {"duration": 0.5, "style": "smoothright"},
                "elements": [
                    {
                        "x": 0, "y": 0, "zoom": 5,
                        "id": "outro_bg",
                        "type": "image",
                        "src": test_data['ProductNo5Photo']
                    },
                    {
                        "settings": {
                            "color": "#e1da19",
                            "font-size": "6.5vw"
                        },
                        "cache": True,
                        "x": 2, "width": 1078, "y": 63,
                        "style": "003",
                        "id": "outro_title",
                        "position": "custom",
                        "text": "Thanks for Watching - Schema Fixed!",
                        "type": "text",
                        "height": 282
                    },
                    {
                        "settings": {
                            "max-words-per-line": 4,
                            "font-size": 100,
                            "style": "classic-progressive",
                            "font-family": "Roboto",
                            "all-caps": True,
                            "outline-width": -1
                        },
                        "language": "en-US",
                        "id": "outro_subtitles",
                        "type": "subtitles"
                    },
                    {
                        "settings": {
                            "button": {
                                "border": "0.2vw solid rgba(0,0,0,20%)",
                                "border-radius": "3vw",
                                "padding": "0 15vw",
                                "box-shadow": "inset -1vw -1vw 1vw rgba(0,0,0,0.2)",
                                "text-shadow": ".3vw .3vw rgba(0,0,0,0.4)",
                                "background": "#E3170A",
                                "font-size": "10vw",
                                "font-family": "Anton",
                                "text": "Subscribe!"
                            }
                        },
                        "component": "advanced/050",
                        "x": 0, "width": 1080, "y": 600,
                        "id": "outro_subscribe_button",
                        "position": "custom",
                        "type": "component"
                    }
                ]
            }
        ],
        "resolution": "instagram-story",
        "height": 1920,
        "quality": "high",
        "draft": False
    }
    
    print("🎬 Creating corrected JSON2Video project...")
    print(f"Title: {test_data['VideoTitle']}")
    
    # Initialize JSON2Video server with API key
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    server = JSON2VideoEnhancedMCPServerV2(config['json2video_api_key'])
    
    try:
        # Create video project using correct method
        result = await server.create_video(corrected_template, test_data['VideoTitle'])
        
        if result.get('success'):
            project_id = result.get('project_id')
            print(f"✅ Video project created successfully!")
            print(f"🆔 Project ID: {project_id}")
            print(f"🔗 Status URL: https://api.json2video.com/v2/movies?project={project_id}")
            print(f"📊 Video will be monitored by Video Status Specialist")
            
            # Save project details for monitoring
            project_details = {
                'project_id': project_id,
                'title': test_data['VideoTitle'],
                'created_at': result.get('created_at', 'Unknown'),
                'template_fixes': [
                    'Removed deprecated vertical-align property from all subtitle elements',
                    'Used only supported subtitle properties: font-size, style, font-family, all-caps, outline-width',
                    'Maintained proper positioning with x, y coordinates for other elements',
                    'Based template on proven working reference schema'
                ],
                'monitoring_url': f"https://api.json2video.com/v2/movies?project={project_id}",
                'expected_duration': '19 seconds (5s intro + 9s product + 5s outro)'
            }
            
            with open(f'/home/claude-workflow/corrected_video_project_{project_id}.json', 'w') as f:
                json.dump(project_details, f, indent=2)
            
            print(f"📝 Project details saved to corrected_video_project_{project_id}.json")
            
            return project_id
            
        else:
            print(f"❌ Video creation failed: {result.get('error', 'Unknown error')}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating video: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(test_corrected_video())