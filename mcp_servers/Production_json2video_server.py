#!/usr/bin/env python3
"""
JSON2Video Enhanced MCP Server v2 - Production Version
Uses Test_json2video_schema.json structure with real data
"""

import asyncio
import json
import logging
import httpx
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JSON2VideoEnhancedMCPServerV2:
    """JSON2Video Enhanced MCP Server v2 - Uses Test schema with real data"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.json2video.com/v2"
        self.headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json"
        }
        self.client = httpx.AsyncClient(timeout=86400, headers=self.headers)
    
    def build_perfect_timing_video_with_test_schema(self, record_data: Dict) -> tuple:
        """Build video using Test_json2video_schema.json structure with real data"""
        
        # Extract data from record
        title = record_data.get('VideoTitle', 'Top 5 Products')
        
        # Create the exact Test schema structure with real data
        movie_json = {
            "resolution": "instagram-story",
            "width": 1080,
            "height": 1920,
            "quality": "high",
            "draft": False,
            "elements": [
                {
                    "type": "subtitles",
                    "language": "en-US",
                    "settings": {
                        "style": "classic",
                        "box-color": "#000000",
                        "outline-width": 10,
                        "word-color": "#e5e826",
                        "shadow-offset": 0,
                        "shadow-color": "#000000",
                        "max-words-per-line": 3,
                        "font-size": 80,
                        "font-family": "Luckiest Guy",
                        "position": "bottom-center",
                        "outline-color": "#000000",
                        "line-color": "#FFF4E9"
                    }
                }
            ],
            "scenes": []
        }
        
        # Add all scenes using the Test schema structure
        movie_json["scenes"] = [
            self._create_intro_scene_test_schema(record_data),
            self._create_product_scene_test_schema(record_data, 5),  # Product 5
            self._create_product_scene_test_schema(record_data, 4),  # Product 4
            self._create_product_scene_test_schema(record_data, 3),  # Product 3
            self._create_product_scene_test_schema(record_data, 2),  # Product 2
            self._create_product_scene_test_schema(record_data, 1),  # Product 1 (Winner)
            self._create_outro_scene_test_schema(record_data)
        ]
        
        project_name = f"Video_{record_data.get('record_id', 'unknown')}_{title[:30].replace(' ', '_')}"
        return movie_json, project_name
    
    def _create_intro_scene_test_schema(self, record_data: Dict) -> Dict:
        """Create intro scene using Test schema structure"""
        intro_photo = record_data.get('IntroPhoto') or record_data.get('ProductNo1Photo') or "https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=1080&h=1920&fit=crop&crop=center"
        # Import Google Drive audio configuration
        import sys
        sys.path.append('/home/claude-workflow/config')
        from google_drive_audio_config import get_audio_url
        
        # Get intro voice URL from record or use Google Drive configuration
        intro_voice_url = record_data.get('IntroVoiceURL')
        if not intro_voice_url:
            try:
                intro_voice_url = get_audio_url('intro')
            except Exception as e:
                print(f"⚠️ Could not get intro audio from Google Drive: {e}")
                intro_voice_url = "https://www.learningcontainer.com/wp-content/uploads/2020/02/Kalimba.mp3"
        
        return {
            "id": "intro_scene",
            "comment": "Intro Scene - 5 seconds",
            "duration": 5,
            "elements": [
                {
                    "id": "intro_bg",
                    "type": "image",
                    "comment": "Background Photo with Zoom",
                    "src": intro_photo,
                    "width": None,
                    "height": None,
                    "x": 0,
                    "y": 0,
                    "zoom": 5
                },
                {
                    "id": "intro_title",
                    "type": "text",
                    "comment": "Video Title - Montserrat Bold",
                    "text": record_data.get('VideoTitle', 'Top 5 Products'),
                    "style": "003",
                    "settings": {
                        "font-family": "Roboto",
                        "font-size": "6.5vw",
                        "color": "#e1da19"
                    },
                    "position": "custom",
                    "x": 2,
                    "y": 63,
                    "width": 1078,
                    "height": 282,
                    "cache": True
                },
                {
                    "id": "intro_audio",
                    "type": "audio",
                    "comment": "Intro Voice Narration",
                    "src": intro_voice_url
                },
                {
                    "id": "intro_subtitles",
                    "type": "subtitles",
                    "settings": {
                        "max-words-per-line": 4,
                        "font-size": 80,
                        "style": "classic-progressive",
                        "font-family": "Roboto",
                        "all-caps": True,
                        "outline-width": -1,
                        "offset-y": 900
                    },
                    "language": "en-US"
                }
            ],
            "transition": {
                "style": "smoothright",
                "duration": 0.5
            },
            "cache": True
        }
    
    def _create_product_scene_test_schema(self, record_data: Dict, product_num: int) -> Dict:
        """Create product scene using Test schema structure"""
        
        # Get fallback images
        fallback_images = [
            "https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=1080&h=1920&fit=crop&crop=center",  # Tech gadget
            "https://images.unsplash.com/photo-1593784991095-a205069470b6?w=1080&h=1920&fit=crop&crop=center",  # Speaker
            "https://images.unsplash.com/photo-1585792180666-f7347c490ee2?w=1080&h=1920&fit=crop&crop=center",  # Electronics
            "https://images.unsplash.com/photo-1583394838336-acd977736f90?w=1080&h=1920&fit=crop&crop=center",  # Headphones
            "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=1080&h=1920&fit=crop&crop=center"   # Tech device
        ]
        
        # Extract product data
        product_title = record_data.get(f'ProductNo{product_num}Title', f'Product {product_num}')
        product_photo = record_data.get(f'ProductNo{product_num}Photo') or fallback_images[(product_num - 1) % len(fallback_images)]
        product_rating = record_data.get(f'ProductNo{product_num}Rating', 4.5)
        product_reviews = record_data.get(f'ProductNo{product_num}Reviews', 1234)
        product_price = record_data.get(f'ProductNo{product_num}Price', 99)
        # Import Google Drive audio configuration
        import sys
        sys.path.append('/home/claude-workflow/config')
        from google_drive_audio_config import get_audio_url
        
        # Try to get specific audio file or use Google Drive configuration
        product_voice_url = record_data.get(f'Product{product_num}VoiceURL')
        if not product_voice_url:
            try:
                audio_type = f'product_{product_num}'
                product_voice_url = get_audio_url(audio_type)
            except Exception as e:
                print(f"⚠️ Could not get product {product_num} audio from Google Drive: {e}")
                # Fallback to a working audio file
                product_voice_url = "https://www.learningcontainer.com/wp-content/uploads/2020/02/Kalimba.mp3"
        
        # Convert to numeric values for components
        try:
            rating_value = float(str(product_rating))
        except:
            rating_value = 4.5
            
        try:
            reviews_value = int(str(product_reviews).replace(',', ''))
        except:
            reviews_value = 1234
            
        try:
            price_value = int(float(str(product_price).replace('$', '').replace(',', '')))
        except:
            price_value = 99
        
        # Winner styling for Product #1
        is_winner = (product_num == 1)
        title_text = f"#{product_num} {product_title}"
        if is_winner:
            title_text += " 🏆"
        
        return {
            "id": f"product_{product_num}_scene",
            "comment": f"Product {product_num} {'(Winner!) ' if is_winner else ''}(Countdown) - 9 seconds",
            "duration": 9,
            "elements": [
                {
                    "id": f"product{product_num}_bg",
                    "type": "image",
                    "comment": f"Product {product_num} Background Photo",
                    "src": product_photo,
                    "width": None,
                    "height": None,
                    "x": 0,
                    "y": 0,
                    "zoom": 5
                },
                {
                    "id": f"product{product_num}_title",
                    "type": "text",
                    "comment": f"Product {product_num} Title - #{product_num} Countdown",
                    "text": title_text,
                    "style": "003",
                    "settings": {
                        "font-family": "Roboto",
                        "font-size": "6.5vw",
                        "color": "#e1da19"
                    },
                    "position": "custom",
                    "x": 2,
                    "y": 63,
                    "width": 1078,
                    "height": 282,
                    "cache": True,
                    "duration": 7,
                    "start": 1,
                    "fade-in": 1,
                    "fade-out": 1
                },
                {
                    "id": f"product{product_num}_rating",
                    "type": "component",
                    "component": "advanced/070",
                    "comment": "Star Rating Component - Moved Up",
                    "settings": {
                        "rating": {
                            "symbol": "star",
                            "size": "6vw",
                            "color": "#e5e826",
                            "horizontal-align": "left",
                            "off-color": "rgba(255,255,255,0.1)",
                            "value": rating_value
                        }
                    },
                    "position": "custom",
                    "x": 40,
                    "y": 600,
                    "cache": True,
                    "duration": 7,
                    "start": 1,
                    "fade-in": 1,
                    "fade-out": 1
                },
                {
                    "id": f"product{product_num}_reviews",
                    "type": "component",
                    "component": "advanced/060",
                    "comment": "Review Count Component - Middle Position",
                    "settings": {
                        "counter": {
                            "duration": 3000,
                            "text-shadow": ".2vw .2vw .2vw rgba(50,50,50,0.5)",
                            "color": "white",
                            "font-size": "4vw",
                            "from": 0,
                            "font-family": "Anton",
                            "text": "__num__ Reviews",
                            "to": reviews_value
                        }
                    },
                    "position": "custom",
                    "x": 500,
                    "y": 600,
                    "cache": True,
                    "duration": 7,
                    "start": 1,
                    "fade-in": 1,
                    "fade-out": 1
                },
                {
                    "id": f"product{product_num}_price",
                    "type": "component",
                    "component": "advanced/060",
                    "comment": "Price Component - Rightmost Position",
                    "settings": {
                        "counter": {
                            "duration": 5000,
                            "color": "#e5e826",
                            "font-size": "6vw",
                            "from": 0,
                            "font-family": "Anton",
                            "text": "$__num__",
                            "to": price_value
                        }
                    },
                    "position": "custom",
                    "x": 800,
                    "y": 600,
                    "width": 280,
                    "cache": True,
                    "duration": 7,
                    "start": 1,
                    "fade-in": 1,
                    "fade-out": 1
                },
                {
                    "id": f"product{product_num}_audio",
                    "type": "audio",
                    "comment": f"Product {product_num} Voice Narration",
                    "src": product_voice_url
                },
                {
                    "id": f"product{product_num}_subtitles",
                    "type": "subtitles",
                    "settings": {
                        "font-size": 80,
                        "style": "classic-progressive",
                        "font-family": "Roboto",
                        "all-caps": True,
                        "outline-width": -1,
                        "offset-y": 900
                    },
                    "language": "en-US"
                }
            ],
            "cache": True,
            "transition": {
                "style": "slideright",
                "duration": 0.5
            }
        }
    
    def _create_outro_scene_test_schema(self, record_data: Dict) -> Dict:
        """Create outro scene using Test schema structure"""
        outro_photo = record_data.get('OutroPhoto') or record_data.get('ProductNo1Photo') or "https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=1080&h=1920&fit=crop&crop=center"
        outro_voice_url = record_data.get('OutroVoiceURL') or "https://www.learningcontainer.com/wp-content/uploads/2020/02/Kalimba.mp3"
        
        return {
            "id": "outro_scene",
            "comment": "Outro Scene - 5 seconds",
            "duration": 5,
            "elements": [
                {
                    "id": "outro_bg",
                    "type": "image",
                    "comment": "Background Photo with Zoom",
                    "src": outro_photo,
                    "width": None,
                    "height": None,
                    "x": 0,
                    "y": 0,
                    "zoom": 5
                },
                {
                    "id": "outro_thanks",
                    "type": "text",
                    "comment": "Thanks Message - Montserrat Bold",
                    "text": "Thanks for Watching!",
                    "style": "003",
                    "settings": {
                        "font-family": "Roboto",
                        "font-size": "6.5vw",
                        "color": "#e1da19"
                    },
                    "position": "custom",
                    "x": 2,
                    "y": 63,
                    "width": 1078,
                    "height": 282,
                    "cache": True
                },
                {
                    "id": "outro_button",
                    "type": "component",
                    "component": "advanced/050",
                    "settings": {
                        "button": {
                            "background": "#E3170A",
                            "border": "0.2vw solid rgba(0,0,0,20%)",
                            "border-radius": "3vw",
                            "padding": "0 15vw",
                            "box-shadow": "inset -1vw -1vw 1vw rgba(0,0,0,0.2)",
                            "text": "Subscribe!",
                            "text-shadow": ".3vw .3vw rgba(0,0,0,0.4)",
                            "font-size": "10vw",
                            "font-family": "Anton"
                        }
                    },
                    "position": "custom",
                    "x": 0,
                    "y": 600,
                    "width": 1080
                },
                {
                    "id": "outro_audio",
                    "type": "audio",
                    "comment": "Outro Voice Narration",
                    "src": outro_voice_url
                },
                {
                    "id": "outro_subtitles",
                    "type": "subtitles",
                    "settings": {
                        "max-words-per-line": 4,
                        "font-size": 80,
                        "style": "classic-progressive",
                        "font-family": "Roboto",
                        "all-caps": True,
                        "outline-width": -1,
                        "offset-y": 900
                    },
                    "language": "en-US"
                }
            ],
            "transition": {
                "style": "smoothright",
                "duration": 0.5
            },
            "cache": True
        }

    async def create_perfect_timing_video(self, record_data: Dict) -> Dict[str, Any]:
        """Create video using Test_json2video_schema.json structure with real data"""
        
        title = record_data.get('VideoTitle', 'Top 5 Products')
        logger.info(f"🎯 Creating video with Test schema: {title[:60]}")
        logger.info(f"⏱️ Duration: 55 seconds (5+45+5) - #Shorts compliant")
        logger.info(f"✨ Features: Test schema structure, proper components, real data")
        
        try:
            movie_json, project_name = self.build_perfect_timing_video_with_test_schema(record_data)
            result = await self.create_video(movie_json, project_name)
            return result
            
        except Exception as e:
            logger.error(f"❌ Video creation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'video_url': None,
                'project_id': None
            }
    
    async def create_video(self, movie_json: Dict, project_name: str) -> Dict[str, Any]:
        """Create video using JSON2Video API"""
        
        # Log the JSON structure for debugging
        logger.info(f"🎬 Creating video project: {project_name}")
        logger.info(f"📊 Scenes: {len(movie_json.get('scenes', []))}")
        
        try:
            # Make API request
            response = await self.client.post(
                f"{self.base_url}/movies",
                json=movie_json
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"📊 JSON2Video API Response: {result}")
                project_id = result.get('project') or result.get('id') or result.get('project_id') or result.get('projectId')
                logger.info(f"✅ Video project created: {project_id}")
                
                # Start monitoring
                video_url = await self.wait_for_video(project_id)
                
                if video_url:
                    return {
                        'success': True,
                        'video_url': video_url,
                        'project_id': project_id,
                        'project_name': project_name
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Video generation timed out or failed',
                        'project_id': project_id
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
    
    async def wait_for_video(self, project_id: str, max_attempts: int = 60) -> Optional[str]:
        """Poll for video completion with proper timing to avoid server overload"""
        
        # Initial 1-minute wait before first status check (Production mode)
        logger.info(f"⏰ Waiting 5 minutes before first status check for project {project_id} (PRODUCTION MODE)")
        await asyncio.sleep(300)  # 5 minutes = 300 seconds
        
        for attempt in range(max_attempts):
            try:
                logger.info(f"🔍 Status check attempt {attempt + 1} for project {project_id}")
                
                response = await self.client.get(
                    f"{self.base_url}/movies?project={project_id}"
                )
                
                if response.status_code == 200:
                    result = response.json()
                    # The movie data is nested under 'movie' key
                    movie_data = result.get('movie', {})
                    status = movie_data.get('status', '').lower()
                    
                    if status == 'done':
                        video_url = movie_data.get('url', '')
                        if video_url:
                            logger.info(f"✅ PERFECT TIMING video completed: {video_url}")
                            return video_url
                        else:
                            logger.warning(f"⚠️ Video done but no URL provided")
                    
                    elif status == 'error':
                        error_msg = movie_data.get('message', 'Unknown error')
                        logger.error(f"❌ Video creation failed: {error_msg}")
                        return None
                    
                    else:
                        # Still processing
                        progress = movie_data.get('progress', 0)
                        logger.info(f"🔄 Video processing... {progress}% (attempt {attempt + 1})")
                
                elif response.status_code == 404:
                    logger.error(f"❌ Project {project_id} not found (404). This usually means the video creation failed on the server side.")
                    return None
                else:
                    logger.warning(f"⚠️ Status check failed: {response.status_code}")
                    if response.status_code >= 400 and attempt > 5:
                        logger.error(f"❌ Too many errors. Stopping status checks for project {project_id}")
                        return None
                    
            except Exception as e:
                logger.error(f"❌ Error checking video status: {str(e)}")
                
            # Wait 1 minute before next status check to avoid server overload
            if attempt < max_attempts - 1:
                logger.info(f"⏰ Waiting 1 minute before next status check...")
                await asyncio.sleep(60)  # 1 minute = 60 seconds
                
        logger.error(f"❌ Video creation timed out after {max_attempts} attempts ({max_attempts} minutes in PRODUCTION MODE)")
        return None
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()