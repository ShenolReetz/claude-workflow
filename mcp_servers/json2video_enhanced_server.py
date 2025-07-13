# mcp_servers/json2video_enhanced_server.py
import json
import logging
import httpx
from typing import Dict, List, Optional, Any
import asyncio
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JSON2VideoEnhancedMCPServer:
    """Enhanced JSON2Video MCP Server with reviews, ratings, and advanced elements"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.json2video.com/v2"
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        self.client = httpx.AsyncClient(timeout=60.0, headers=self.headers)
    
    def build_production_video_template(self, record_data: Dict) -> tuple:
        """Build full production video: 60 seconds with reviews and ratings"""
        
        # Extract data from record
        title = record_data.get('VideoTitle', 'Top 5 Products')
        
        # Build JSON2Video movie structure with advanced features
        movie_json = {
            "comment": f"Production video: {title[:30]}",
            "resolution": "instagram-story",  # 9:16 vertical format (1080x1920)
            "quality": "high",  # High quality for production
            "scenes": []
        }
        
        # 1. INTRO SCENE - 5 seconds with animations
        intro_scene = {
            "comment": "Intro scene with animations",
            "duration": 5,
            "transition": {
                "type": "fade",
                "duration": 1
            },
            "elements": [
                # Background gradient
                {
                    "type": "shape",
                    "shape": "rectangle",
                    "width": 1080,
                    "height": 1920,
                    "x": 0,
                    "y": 0,
                    "fill-color": {
                        "type": "linear-gradient",
                        "colors": ["#1a1a2e", "#16213e"],
                        "direction": "vertical"
                    }
                },
                # Main title with zoom animation
                {
                    "type": "text",
                    "text": title,
                    "font-family": "Montserrat",
                    "font-weight": "bold",
                    "font-size": 72,
                    "font-color": "#FFFFFF",
                    "text-align": "center",
                    "x": "center",
                    "y": 400,
                    "width": 900,
                    "duration": 5,
                    "animations": [
                        {
                            "type": "scale",
                            "from": 0,
                            "to": 1,
                            "start": 0,
                            "duration": 1,
                            "easing": "easeOutBack"
                        }
                    ]
                },
                # Subtitle
                {
                    "type": "text",
                    "text": "Let's count down the best products!",
                    "font-family": "Open Sans",
                    "font-size": 36,
                    "font-color": "#FFD700",
                    "text-align": "center",
                    "x": "center",
                    "y": 600,
                    "width": 800,
                    "start": 1,
                    "duration": 4,
                    "animations": [
                        {
                            "type": "fade",
                            "from": 0,
                            "to": 1,
                            "start": 0,
                            "duration": 1
                        }
                    ]
                }
            ],
            "background-color": "#1a1a2e"
        }
        movie_json["scenes"].append(intro_scene)
        
        # 2. PRODUCT COUNTDOWN SCENES - 10 seconds each (5 products)
        for i in range(5, 0, -1):  # Countdown from 5 to 1
            product_title = record_data.get(f'ProductNo{i}Title')
            if not product_title:
                continue
                
            product_scene = self._create_product_scene(
                rank=6-i,  # Display rank (1-5)
                countdown_number=i,  # Countdown number (5-1)
                title=product_title,
                description=record_data.get(f'ProductNo{i}Description', ''),
                image_url=record_data.get(f'ProductNo{i}ImageURL', ''),
                review_count=record_data.get(f'ProductNo{i}ReviewCount', '0'),
                rating=record_data.get(f'ProductNo{i}Rating', 4.0),
                is_winner=(i == 1)  # Special effects for #1
            )
            movie_json["scenes"].append(product_scene)
        
        # 3. OUTRO SCENE - 5 seconds with CTA
        outro_scene = {
            "comment": "Outro scene with CTA",
            "duration": 5,
            "transition": {
                "type": "cross-dissolve",
                "duration": 1
            },
            "elements": [
                # Background
                {
                    "type": "shape",
                    "shape": "rectangle",
                    "width": 1080,
                    "height": 1920,
                    "x": 0,
                    "y": 0,
                    "fill-color": "#1a1a2e"
                },
                # Thanks message
                {
                    "type": "text",
                    "text": "Thanks for Watching!",
                    "font-family": "Montserrat",
                    "font-weight": "bold",
                    "font-size": 64,
                    "font-color": "#FFFFFF",
                    "text-align": "center",
                    "x": "center",
                    "y": 400,
                    "width": 900,
                    "animations": [
                        {
                            "type": "scale",
                            "from": 0.8,
                            "to": 1.2,
                            "start": 0,
                            "duration": 2,
                            "easing": "easeInOutSine",
                            "loop": True
                        }
                    ]
                },
                # CTA Button
                {
                    "type": "component",
                    "component": "basic/027",  # Button component
                    "settings": {
                        "button_text": "🛒 CHECK LINKS BELOW",
                        "button_color": "#FFD700",
                        "text_color": "#000000",
                        "corner_radius": 30,
                        "font_size": 32
                    },
                    "x": "center",
                    "y": 600,
                    "width": 600,
                    "start": 1,
                    "duration": 4,
                    "animations": [
                        {
                            "type": "pulse",
                            "scale": 1.1,
                            "duration": 1,
                            "loop": True
                        }
                    ]
                },
                # Social icons
                {
                    "type": "text",
                    "text": "👍 LIKE | 🔔 SUBSCRIBE | 💬 COMMENT",
                    "font-family": "Open Sans",
                    "font-size": 28,
                    "font-color": "#FFD700",
                    "text-align": "center",
                    "x": "center",
                    "y": 800,
                    "width": 800,
                    "start": 2,
                    "duration": 3
                }
            ]
        }
        movie_json["scenes"].append(outro_scene)
        
        project_name = f"PROD_{title[:30]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return movie_json, project_name
    
    def _create_product_scene(self, rank: int, countdown_number: int, title: str, 
                             description: str, image_url: str, review_count: str, 
                             rating: float, is_winner: bool = False) -> Dict:
        """Create a product scene with reviews and ratings"""
        
        # Determine transition based on position
        transitions = {
            5: {"type": "wipe", "direction": "up", "duration": 0.8},
            4: {"type": "slide", "direction": "left", "duration": 0.6},
            3: {"type": "slide", "direction": "left", "duration": 0.6},
            2: {"type": "cross-dissolve", "duration": 0.8},
            1: {"type": "zoom", "duration": 0.8}
        }
        
        scene = {
            "comment": f"Product #{countdown_number} - {title[:30]}",
            "duration": 10,
            "transition": transitions.get(countdown_number, {"type": "fade", "duration": 0.5}),
            "elements": []
        }
        
        # Background gradient
        bg_colors = ["#16213e", "#0f3460"] if not is_winner else ["#FFD700", "#FFA500"]
        scene["elements"].append({
            "type": "shape",
            "shape": "rectangle",
            "width": 1080,
            "height": 1920,
            "x": 0,
            "y": 0,
            "fill-color": {
                "type": "linear-gradient",
                "colors": bg_colors,
                "direction": "diagonal"
            }
        })
        
        # Countdown number (large)
        scene["elements"].append({
            "type": "text",
            "text": f"#{countdown_number}",
            "font-family": "Bebas Neue",
            "font-size": 200,
            "font-color": "#FFFFFF" if not is_winner else "#000000",
            "text-align": "center",
            "x": "center",
            "y": 100,
            "opacity": 0.3,
            "animations": [
                {
                    "type": "scale",
                    "from": 2,
                    "to": 1,
                    "start": 0,
                    "duration": 0.5,
                    "easing": "easeOutBounce"
                }
            ]
        })
        
        # Product image
        if image_url:
            scene["elements"].append({
                "type": "image",
                "src": image_url,
                "x": "center",
                "y": 350,
                "width": 600,
                "height": 600,
                "object-fit": "contain",
                "start": 0.5,
                "duration": 9.5,
                "animations": [
                    {
                        "type": "slide",
                        "from": {"x": -1080, "y": 350},
                        "to": {"x": "center", "y": 350},
                        "start": 0,
                        "duration": 0.8,
                        "easing": "easeOutCubic"
                    }
                ]
            })
        
        # Product title
        scene["elements"].append({
            "type": "text",
            "text": title,
            "font-family": "Montserrat",
            "font-weight": "bold",
            "font-size": 48,
            "font-color": "#FFFFFF" if not is_winner else "#000000",
            "text-align": "center",
            "x": "center",
            "y": 1000,
            "width": 900,
            "start": 1,
            "duration": 9,
            "animations": [
                {
                    "type": "fade",
                    "from": 0,
                    "to": 1,
                    "start": 0,
                    "duration": 0.5
                }
            ]
        })
        
        # Review component - Stars
        scene["elements"].append({
            "type": "component",
            "component": "advanced/070",  # Star rating component
            "settings": {
                "rating": {
                    "value": rating,
                    "max_value": 5,
                    "star_size": 48,
                    "star_color": "#FFD700",
                    "empty_star_color": "#333333"
                }
            },
            "x": "center",
            "y": 1150,
            "width": 300,
            "start": 1.5,
            "duration": 8.5
        })
        
        # Review count
        scene["elements"].append({
            "type": "component",
            "component": "advanced/060",  # Counter component
            "settings": {
                "counter": {
                    "value": review_count,
                    "suffix": " Reviews",
                    "animation_duration": 2,
                    "format": "comma",
                    "font_size": 36,
                    "font_color": "#FFD700"
                }
            },
            "x": "center",
            "y": 1250,
            "width": 400,
            "start": 2,
            "duration": 8
        })
        
        # Product description (truncated)
        desc_lines = description.split('. ')[:2]  # First 2 sentences
        desc_text = '. '.join(desc_lines) + '.' if desc_lines else description[:100]
        
        scene["elements"].append({
            "type": "text",
            "text": desc_text,
            "font-family": "Open Sans",
            "font-size": 32,
            "font-color": "#E0E0E0" if not is_winner else "#333333",
            "text-align": "center",
            "line-height": 1.4,
            "x": "center",
            "y": 1350,
            "width": 850,
            "start": 2.5,
            "duration": 7.5
        })
        
        # Special winner badge for #1
        if is_winner:
            scene["elements"].append({
                "type": "component",
                "component": "basic/036",  # Badge component
                "settings": {
                    "badge_text": "🏆 WINNER",
                    "badge_color": "#FF0000",
                    "text_color": "#FFFFFF",
                    "font_size": 48
                },
                "x": "center",
                "y": 200,
                "width": 300,
                "animations": [
                    {
                        "type": "rotate",
                        "from": -10,
                        "to": 10,
                        "duration": 2,
                        "loop": True,
                        "easing": "easeInOutSine"
                    }
                ]
            })
        
        return scene
    
    async def create_production_video(self, record_data: Dict) -> Dict[str, Any]:
        """Create a full production video with all features"""
        
        title = record_data.get('VideoTitle', 'Top 5 Products')
        logger.info(f"🎬 Creating PRODUCTION video (60 seconds): {title[:60]}")
        logger.info(f"⏱️ Duration: 60 seconds (5+50+5)")
        logger.info(f"✨ Features: Reviews, Ratings, Animations, Transitions")
        
        try:
            movie_json, project_name = self.build_production_video_template(record_data)
            result = await self.create_video(movie_json, project_name)
            return result
            
        except Exception as e:
            logger.error(f"❌ Production video creation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def create_video(self, movie_json: Dict, project_name: str) -> Dict[str, Any]:
        """Submit video creation request to JSON2Video API"""
        try:
            logger.info(f"🎬 Submitting video to JSON2Video API: {project_name}")
            logger.info(f"📐 Resolution: {movie_json.get('resolution', 'default')}")
            logger.info(f"🎨 Scenes: {len(movie_json.get('scenes', []))}")
            
            # Add voice-over if available
            if hasattr(self, 'voice_data') and self.voice_data:
                movie_json['voice'] = {
                    'speaker': 'en-US-Neural2-F',  # Google TTS voice
                    'audio_files': self.voice_data
                }
            
            # Send the movie JSON
            response = await self.client.post(
                f"{self.base_url}/movies",
                json=movie_json
            )
            
            logger.info(f"📡 Response status: {response.status_code}")
            
            if response.status_code in [200, 201, 202]:
                result = response.json()
                project_id = result.get('project', '')
                
                logger.info(f"✅ Video creation started. Project ID: {project_id}")
                
                # Wait for video to be ready
                video_url = await self.wait_for_video(project_id)
                
                return {
                    'success': True,
                    'movie_id': project_id,
                    'video_url': video_url,
                    'project_name': project_name,
                    'duration': 60,
                    'features': ['reviews', 'ratings', 'animations', 'transitions']
                }
            else:
                error_msg = f"API error: {response.status_code} - {response.text}"
                logger.error(f"❌ {error_msg}")
                return {
                    'success': False,
                    'error': error_msg
                }
                
        except Exception as e:
            logger.error(f"❌ Exception during video creation: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def wait_for_video(self, project_id: str, max_attempts: int = 120) -> Optional[str]:
        """Poll for video completion - longer wait for production videos"""
        
        for attempt in range(max_attempts):
            try:
                await asyncio.sleep(5)  # Wait 5 seconds between checks
                
                response = await self.client.get(
                    f"{self.base_url}/movies",
                    params={"project": project_id}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    movie_data = data.get('movie', {})
                    status = movie_data.get('status', '')
                    
                    logger.info(f"⏳ Video status: {status} (attempt {attempt + 1}/{max_attempts})")
                    
                    if status == 'done':
                        video_url = movie_data.get('url', '')
                        logger.info(f"✅ Video ready: {video_url}")
                        return video_url
                    elif status == 'error':
                        error_msg = movie_data.get('message', 'Unknown error')
                        logger.error(f"❌ Video generation failed: {error_msg}")
                        return None
                        
            except Exception as e:
                logger.error(f"Error checking video status: {e}")
        
        logger.error("❌ Video generation timeout")
        return None
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

# Test function
if __name__ == "__main__":
    import os
    
    # Test data with reviews and ratings
    test_record = {
        'VideoTitle': '🔥 Top 5 Gaming Headsets in 2025! 🎮',
        'ProductNo1Title': 'SteelSeries Arctis Nova Pro',
        'ProductNo1Description': 'Premium wireless gaming headset with active noise cancellation and hi-res audio.',
        'ProductNo1ImageURL': 'https://example.com/headset1.jpg',
        'ProductNo1ReviewCount': '15234',
        'ProductNo1Rating': 4.8,
        
        'ProductNo2Title': 'Razer BlackShark V2 Pro',
        'ProductNo2Description': 'Ultra-lightweight wireless headset with THX Spatial Audio.',
        'ProductNo2ImageURL': 'https://example.com/headset2.jpg',
        'ProductNo2ReviewCount': '9876',
        'ProductNo2Rating': 4.6,
        
        # ... more products
    }
    
    async def test_enhanced_video():
        with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
            config = json.load(f)
        
        server = JSON2VideoEnhancedMCPServer(config['json2video_api_key'])
        
        print("🧪 Testing enhanced video generation...")
        print(f"📋 Title: {test_record['VideoTitle']}")
        print(f"⭐ Features: Reviews, Ratings, Animations")
        
        # Build the movie JSON to inspect
        movie_json, project_name = server.build_production_video_template(test_record)
        
        print(f"\n📊 Generated movie structure:")
        print(f"   - Scenes: {len(movie_json['scenes'])}")
        print(f"   - Duration: 60 seconds")
        print(f"   - Resolution: {movie_json['resolution']}")
        
        # Show scene breakdown
        for i, scene in enumerate(movie_json['scenes']):
            print(f"   - Scene {i+1}: {scene['comment']} ({scene['duration']}s)")
        
        await server.close()
    
    asyncio.run(test_enhanced_video())