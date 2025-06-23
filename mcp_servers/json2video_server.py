# mcp_servers/json2video_server.py
import json
import logging
import httpx
from typing import Dict, List, Optional, Any
import asyncio
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JSON2VideoMCPServer:
    """JSON2Video MCP Server for video creation"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.json2video.com/v2"
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        self.client = httpx.AsyncClient(timeout=60.0, headers=self.headers)
    
    def build_test_video_template(self, record_data: Dict) -> tuple:
        """Build minimal test video: 8 seconds total"""
        
        # Extract data from record
        title = record_data.get('VideoTitle', 'Test Video')
        
        # Get products for countdown
        products = []
        for i in range(1, 6):
            product_title = record_data.get(f'ProductNo{i}Title')
            if product_title:
                products.append({
                    'title': product_title,
                    'description': record_data.get(f'ProductNo{i}Description', '')
                })
        
        # Build JSON2Video movie structure (NOT a template reference)
        movie_json = {
            "comment": f"Test video: {title[:30]}",
            "resolution": "instagram-story",  # 9:16 vertical format (1080x1920)
            "quality": "medium",  # medium quality for testing
            "scenes": []
        }
        
        # Intro scene - 2 seconds
        intro_scene = {
            "comment": "Intro scene",
            "duration": 2,
            "elements": [
                {
                    "type": "text",
                    "text": title[:50],
                    "duration": 2
                }
            ],
            "background-color": "#1a1a2e"
        }
        movie_json["scenes"].append(intro_scene)
        
        # Product countdown scene - 4 seconds (1 product only for test)
        if products:
            product = products[0]  # Only first product for test
            product_scene = {
                "comment": "Product #1",
                "duration": 4,
                "elements": [
                    {
                        "type": "text",
                        "text": product['title'][:40],
                        "duration": 4
                    }
                ],
                "background-color": "#16213e"
            }
            movie_json["scenes"].append(product_scene)
        
        # Outro scene - 2 seconds
        outro_scene = {
            "comment": "Outro scene",
            "duration": 2,
            "elements": [
                {
                    "type": "text",
                    "text": "Thanks for watching!",
                    "duration": 2
                }
            ],
            "background-color": "#1a1a2e"
        }
        movie_json["scenes"].append(outro_scene)
        
        project_name = f"TEST_{title[:30]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return movie_json, project_name
    
    def complete_test_template(self, template: Dict, product_title: str, voice_text: str) -> Dict:
        """Complete the test template (compatibility method)"""
        return template
    
    async def create_test_video(self, record_data: Dict) -> Dict[str, Any]:
        """Create a minimal test video with only 1 product"""
        
        title = record_data.get('VideoTitle', 'Test Video')
        logger.info(f"🧪 Creating TEST video (8 seconds): {title[:60]}")
        logger.info(f"⏱️ TEST video duration: 8 seconds (2+4+2)")
        logger.info(f"💰 Minimal cost for testing")
        
        try:
            movie_json, project_name = self.build_test_video_template(record_data)
            result = await self.create_video(movie_json, project_name)
            return result
            
        except Exception as e:
            logger.error(f"❌ Test video creation failed: {str(e)}")
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
            
            # Send the movie JSON directly (not as a template)
            response = await self.client.post(
                f"{self.base_url}/movies",
                json=movie_json
            )
            
            logger.info(f"📡 Response status: {response.status_code}")
            
            if response.status_code in [200, 201, 202]:
                result = response.json()
                
                # The response should contain a project ID
                project_id = result.get('project', '')
                
                logger.info(f"✅ Video creation started. Project ID: {project_id}")
                logger.info(f"📊 Response: {json.dumps(result, indent=2)}")
                
                # Wait for video to be ready
                video_url = await self.wait_for_video(project_id)
                
                return {
                    'success': True,
                    'movie_id': project_id,
                    'video_url': video_url,
                    'project_name': project_name
                }
            else:
                error_msg = f"API error: {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f" - {json.dumps(error_data)}"
                except:
                    error_msg += f" - {response.text}"
                
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
        """Poll for video completion using project ID"""
        
        for attempt in range(max_attempts):
            try:
                await asyncio.sleep(5)  # Wait 5 seconds between checks
                
                # Check status using project parameter
                response = await self.client.get(
                    f"{self.base_url}/movies",
                    params={"project": project_id}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check if movie data exists in response
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

# MCP integration functions
async def run_json2video_generation(config: Dict, record_id: str) -> Dict:
    """Main function to create video from Airtable record"""
    
    from mcp_servers.airtable_server import AirtableMCPServer
    
    logger.info(f"🎬 Starting video creation for record: {record_id}")
    
    # Initialize servers
    airtable_server = AirtableMCPServer(
        config['airtable_api_key'],
        config['airtable_base_id'],
        config['airtable_table_name']
    )
    
    json2video_server = JSON2VideoMCPServer(config['json2video_api_key'])
    
    try:
        # Get record data
        record = await airtable_server.get_record(record_id)
        if not record:
            raise ValueError(f"Record {record_id} not found")
        
        record_data = record['fields']
        
        # Check if we have the required data
        video_title = record_data.get('VideoTitle')
        if not video_title:
            raise ValueError("No VideoTitle found in record")
        
        # Count products
        product_count = 0
        for i in range(1, 6):
            if record_data.get(f'ProductNo{i}Title'):
                product_count += 1
        
        logger.info(f"📦 Found video title and {product_count} products")
        logger.info(f"🎬 Creating video: {video_title[:60]}")
        
        # Create test video
        result = await json2video_server.create_test_video(record_data)
        
        # Update Airtable with results
        if result['success']:
            update_fields = {
                'VideoMovieID': result.get('movie_id', ''),
                'VideoURL': result.get('video_url', ''),
                'VideoCreatedAt': datetime.now().isoformat()
            }
            await airtable_server.update_record(record_id, update_fields)
            logger.info(f"✅ Updated Airtable with video info")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Error in video generation: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }
    finally:
        await json2video_server.close()

# Test function
if __name__ == "__main__":
    import os
    
    # Test configuration
    test_config = {
        'json2video_api_key': os.getenv('JSON2VIDEO_API_KEY', 'your-api-key-here'),
        'airtable_api_key': os.getenv('AIRTABLE_API_KEY'),
        'airtable_base_id': 'appTtNBJ8dAnjvkPP',
        'airtable_table_name': 'Video Titles'
    }
    
    # Test with a record ID
    test_record_id = 'rec00Yb60qB6jOXSE'  # Replace with actual record ID
    
    asyncio.run(run_json2video_generation(test_config, test_record_id))
