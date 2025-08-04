#!/usr/bin/env python3
"""
JSON2Video Enhanced MCP Server v2 - Production Version FIXED
Uses the EXACT Test_json2video_schema.json structure
"""

import asyncio
import json
import logging
import httpx
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JSON2VideoEnhancedMCPServerV2:
    """JSON2Video Enhanced MCP Server v2 - Uses Test_json2video_schema.json"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.json2video.com/v2"
        self.headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json"
        }
        self.client = httpx.AsyncClient(timeout=86400, headers=self.headers)
    
    def build_perfect_timing_video_with_test_schema(self, record_data: Dict) -> tuple:
        """Build video using Production_json2video_schema.json for production workflow"""
        
        # Load the production schema
        try:
            with open('/home/claude-workflow/Production_json2video_schema.json', 'r') as f:
                movie_json = json.load(f)
        except Exception as e:
            logger.error(f"❌ Could not load Production_json2video_schema.json: {e}")
            # Fallback to basic structure
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
        
        # Replace all placeholder values with actual Airtable data
        movie_json_str = json.dumps(movie_json)
        movie_json_str = self._replace_placeholders_with_airtable_data(movie_json_str, record_data)
        movie_json = json.loads(movie_json_str)
        
        title = record_data.get('VideoTitle', 'Top 5 Products')
        project_name = f"Video_{record_data.get('record_id', 'unknown')}_{title[:30].replace(' ', '_')}"
        return movie_json, project_name
    
    def _replace_placeholders_with_airtable_data(self, json_str: str, record_data: Dict) -> str:
        """Replace {{placeholder}} values with actual Airtable data"""
        # DO NOT use hardcoded audio - use dynamically generated ElevenLabs audio from Airtable
        
        # Video content
        json_str = json_str.replace('{{VideoTitle}}', str(record_data.get('VideoTitle', 'Top 5 Products')))
        json_str = json_str.replace('{{OutroText}}', str(record_data.get('OutroCallToAction', 'Thanks for Watching!')))
        
        # Images
        json_str = json_str.replace('{{IntroPhoto}}', str(record_data.get('IntroPhoto', 'https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=1080&h=1920&fit=crop&crop=center')))
        json_str = json_str.replace('{{OutroPhoto}}', str(record_data.get('OutroPhoto', 'https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=1080&h=1920&fit=crop&crop=center')))
        
        # Audio files - Use ElevenLabs generated audio from Airtable (correct field names)
        intro_audio = record_data.get('IntroMp3', '')
        outro_audio = record_data.get('OutroMp3', '')
        
        # DEBUG: Log what we found
        logger.info(f"🔍 DEBUG: IntroMp3 from database: '{intro_audio}'")
        logger.info(f"🔍 DEBUG: OutroMp3 from database: '{outro_audio}'")
        
        if not intro_audio:
            logger.error("❌ CRITICAL: IntroMp3 is empty - this will cause video creation to fail!")
        if not outro_audio:
            logger.error("❌ CRITICAL: OutroMp3 is empty - this will cause video creation to fail!")
        
        json_str = json_str.replace('{{IntroAudio}}', intro_audio)
        json_str = json_str.replace('{{OutroAudio}}', outro_audio)
        
        logger.info(f"🎵 Using ElevenLabs intro audio: {intro_audio[:50] if intro_audio else 'EMPTY!'}...")
        logger.info(f"🎵 Using ElevenLabs outro audio: {outro_audio[:50] if outro_audio else 'EMPTY!'}...")
        
        # Product data (1-5)
        for i in range(1, 6):
            # Product titles with ranking
            product_title = record_data.get(f'ProductNo{i}Title', f'Product {i}')
            if i == 1:
                product_title = f"#{i} {product_title} 🏆"  # Winner trophy
            else:
                product_title = f"#{i} {product_title}"
            json_str = json_str.replace(f'{{{{ProductNo{i}Title}}}}', str(product_title))
            
            # Product images - Use OpenAI generated images from ProductNoXPhoto field
            product_photo = record_data.get(f'ProductNo{i}Photo')
            
            # OpenAI images should be in ProductNoXPhoto field after generation
            if not product_photo:
                logger.warning(f"⚠️ No image found in ProductNo{i}Photo field - using placeholder")
                product_photo = 'https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=1080&h=1920&fit=crop&crop=center'
            else:
                logger.info(f"🖼️ Using image for Product {i}: {product_photo[:50]}...")
                
            json_str = json_str.replace(f'{{{{ProductNo{i}Photo}}}}', str(product_photo))
            
            # Product audio - Use ElevenLabs generated audio from Airtable (correct field names)
            product_audio = record_data.get(f'Product{i}Mp3', '')
            
            # DEBUG: Log what we found
            logger.info(f"🔍 DEBUG: Product{i}Mp3 from database: '{product_audio}'")
            
            if not product_audio:
                logger.error(f"❌ CRITICAL: Product{i}Mp3 is empty - this will cause video creation to fail!")
            
            json_str = json_str.replace(f'{{{{ProductNo{i}Audio}}}}', product_audio)
            
            if product_audio:
                logger.info(f"🎵 Using ElevenLabs audio for Product {i}: {product_audio[:50]}...")
            else:
                logger.warning(f"⚠️ No ElevenLabs audio found for Product {i}")
            
            # Product ratings, reviews, prices (ensure numeric values)
            rating = float(record_data.get(f'ProductNo{i}Rating', 4.5))
            reviews = int(record_data.get(f'ProductNo{i}Reviews', 1000))
            price = int(float(str(record_data.get(f'ProductNo{i}Price', 25)).replace('$', '').replace(',', '')))
            
            json_str = json_str.replace(f'{{{{ProductNo{i}Rating}}}}', str(rating))
            json_str = json_str.replace(f'{{{{ProductNo{i}Reviews}}}}', str(reviews))
            json_str = json_str.replace(f'{{{{ProductNo{i}Price}}}}', str(price))
            
            logger.info(f"📦 Product {i}: {product_title} | ⭐{rating} | 👥{reviews} | 💰${price}")
        
        logger.info("✅ All placeholders replaced with dynamic Airtable data")
        return json_str
    
    # Note: Scene updating logic replaced by direct placeholder replacement in schema
    
    async def create_video_project_with_status_monitoring(self, movie_json: dict, project_name: str = "Untitled") -> dict:
        """Create video project and monitor status until completion"""
        
        logger.info(f"🎬 Creating video project: {project_name}")
        logger.info(f"📊 Scenes: {len(movie_json.get('scenes', []))}")
        
        try:
            # Send the movie_json directly, not wrapped in another object
            response = await self.client.post(
                f"{self.base_url}/movies",
                json=movie_json
            )
            
            result = response.json()
            logger.info(f"📊 JSON2Video API Response: {result}")
            
            if result.get('success'):
                project_id = result.get('project')
                logger.info(f"✅ Video project created: {project_id}")
                
                # Wait before checking status
                logger.info(f"⏰ Waiting 5 minutes before first status check for project {project_id} (PRODUCTION MODE)")
                await asyncio.sleep(300)  # 5 minutes
                
                # Check status periodically
                max_attempts = 40  # 40 minutes max
                for attempt in range(max_attempts):
                    status = await self.check_video_status(project_id)
                    
                    if status.get('status') == 'done':
                        logger.info(f"✅ Video completed: {status.get('url')}")
                        return {
                            'success': True,
                            'project_id': project_id,
                            'video_url': status.get('url'),
                            'video_duration': status.get('duration'),
                            'rendering_time': status.get('rendering_time')
                        }
                    elif status.get('status') == 'error':
                        logger.error(f"❌ Video generation failed: {status.get('message')}")
                        return {
                            'success': False,
                            'project_id': project_id,
                            'error': status.get('message', 'Unknown error'),
                            'video_url': None
                        }
                    
                    logger.info(f"⏳ Status: {status.get('status')} - Attempt {attempt + 1}/{max_attempts}")
                    await asyncio.sleep(60)  # Wait 1 minute between checks
                
                # Timeout
                return {
                    'success': False,
                    'project_id': project_id,
                    'error': 'Video generation timeout after 40 minutes',
                    'video_url': None
                }
                
            else:
                logger.error(f"❌ Failed to create video project: {result}")
                return {
                    'success': False,
                    'error': result.get('message', 'Unknown error'),
                    'video_url': None,
                    'project_id': None
                }
                
        except Exception as e:
            logger.error(f"❌ Exception during video creation: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'video_url': None,
                'project_id': None
            }
    
    async def check_video_status(self, project_id: str) -> dict:
        """Check the status of a video project"""
        try:
            response = await self.client.get(
                f"{self.base_url}/movies",
                params={"project": project_id}
            )
            
            result = response.json()
            if result.get('success') and result.get('movie'):
                return result['movie']
            else:
                return {'status': 'error', 'message': 'Failed to get status'}
                
        except Exception as e:
            logger.error(f"❌ Error checking video status: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    async def create_perfect_timing_video(self, record_data: Dict) -> Dict:
        """Create video with perfect timing using exact Test schema - WRAPPER METHOD"""
        movie_json, project_name = self.build_perfect_timing_video_with_test_schema(record_data)
        return await self.create_video_project_with_status_monitoring(movie_json, project_name)
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()