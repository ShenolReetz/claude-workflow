#!/usr/bin/env python3
"""
Intro Image Generator (TEST MODE)
Uses default photos instead of generating new ones for faster testing
"""

import asyncio
import json
import logging
import httpx
from typing import Dict, List, Optional
import base64
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.mcp.google_drive_agent_mcp import GoogleDriveAgentMCP
from mcp_servers.Test_default_photo_manager import TestDefaultPhotoManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntroImageGenerator:
    """Generate intro images (TEST MODE: Uses default photos)"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.openai_api_key = config['openai_api_key']
        self.client = httpx.AsyncClient(timeout=86400)
        self.headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
        self.photo_manager = TestDefaultPhotoManager()
    
    async def generate_intro_image(self, video_title: str, products: List[Dict], 
                                  category: str, record_id: str) -> Dict:
        """Generate intro image (TEST MODE: Uses default photo)"""
        
        logger.info(f"🎨 TEST MODE: Using default intro image for: {video_title}")
        
        try:
            # Get default intro photo instead of generating
            intro_photo_url = self.photo_manager.get_intro_photo()
            
            logger.info("✅ TEST MODE: Using default intro photo (no generation needed)")
            logger.info(f"📸 Default intro photo: {intro_photo_url}")
            
            return {
                'success': True,
                'image_url': intro_photo_url,
                'prompt_used': 'TEST MODE: Using default photo',
                'products_featured': len(products),
                'model': 'default-photo',
                'test_mode': True,
                'generation_skipped': True
            }
                
        except Exception as e:
            logger.error(f"❌ Error getting default intro image: {e}")
            return {
                'success': False,
                'error': str(e),
                'test_mode': True
            }
    
    async def _save_to_drive(self, image_base64: str, record_id: str, video_title: str) -> str:
        """Save intro image to Google Drive"""
        try:
            # Initialize Google Drive agent
            drive_agent = GoogleDriveAgentMCP(self.config)
            if not await drive_agent.initialize():
                logger.error("❌ Failed to initialize Google Drive")
                return f"https://drive.google.com/file/d/intro_{record_id}/view"
            
            # Convert base64 to bytes
            image_bytes = base64.b64decode(image_base64)
            
            # Create project folder structure
            safe_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            folder_ids = await drive_agent.drive_server.create_project_structure(safe_title)
            
            # Upload to Photos folder
            photos_folder_id = folder_ids.get('photos')
            if not photos_folder_id:
                logger.error("❌ Could not create photos folder")
                return f"https://drive.google.com/file/d/intro_{record_id}/view"
            
            # Upload intro image using audio file upload method as template
            filename = f"{record_id}_intro_all_products.jpg"
            
            # Use the Google Drive service directly
            try:
                # Convert bytes to base64 for upload
                import base64 as b64
                image_base64 = b64.b64encode(image_bytes).decode()
                
                # Create file metadata
                file_metadata = {
                    'name': filename,
                    'parents': [photos_folder_id]
                }
                
                # Upload file
                from googleapiclient.http import MediaInMemoryUpload
                
                media = MediaInMemoryUpload(
                    image_bytes,
                    mimetype='image/jpeg'
                )
                
                file_result = drive_agent.drive_server.service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()
                
                file_id = file_result.get('id')
                
                if file_id:
                    # Make file publicly viewable
                    try:
                        drive_agent.drive_server.service.permissions().create(
                            fileId=file_id,
                            body={'role': 'reader', 'type': 'anyone'}
                        ).execute()
                    except Exception as e:
                        logger.warning(f"Could not make file public: {e}")
                    
                    drive_url = f"https://drive.google.com/file/d/{file_id}/view?usp=drivesdk"
                    logger.info(f"✅ Intro image saved to Google Drive: {drive_url}")
                    return drive_url
                else:
                    logger.error("❌ Failed to upload intro image")
                    return f"https://drive.google.com/file/d/intro_{record_id}/view"
                    
            except Exception as upload_error:
                logger.error(f"❌ Upload error: {upload_error}")
                return f"https://drive.google.com/file/d/intro_{record_id}/view"
                
        except Exception as e:
            logger.error(f"❌ Error saving intro image to Drive: {e}")
            return f"https://drive.google.com/file/d/intro_{record_id}/view"
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


# Integration function for workflow
async def generate_intro_image_for_workflow(config: Dict, record_id: str, 
                                          video_title: str, products: List[Dict],
                                          category: str) -> Dict:
    """Generate intro image and integrate into workflow"""
    
    generator = IntroImageGenerator(config)
    
    try:
        result = await generator.generate_intro_image(
            video_title, products, category, record_id
        )
        
        # Update Airtable with intro image URL
        if result['success']:
            from mcp_servers.Test_airtable_server import AirtableMCPServer
            
            airtable_server = AirtableMCPServer(
                api_key=config['airtable_api_key'],
                base_id=config['airtable_base_id'],
                table_name=config['airtable_table_name']
            )
            
            await airtable_server.update_record(record_id, {
                'IntroPhoto': result['image_url']
            })
            
            logger.info(f"✅ Intro image URL saved to Airtable")
        
        return result
        
    finally:
        await generator.close()


# Test function
if __name__ == "__main__":
    async def test_intro_image():
        # Load config
        with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
            config = json.load(f)
        
        # Test data
        test_products = [
            {"title": "SteelSeries Arctis Nova Pro Gaming Headset"},
            {"title": "Razer BlackShark V2 Pro Wireless Headset"},
            {"title": "HyperX Cloud Alpha Gaming Headset"},
            {"title": "Logitech G Pro X Gaming Headset"},
            {"title": "Corsair Virtuoso RGB Wireless Gaming Headset"}
        ]
        
        generator = IntroImageGenerator(config)
        
        print("🧪 Testing intro image generation...")
        
        result = await generator.generate_intro_image(
            video_title="Top 5 Gaming Headsets That'll Transform Your Gaming Experience",
            products=test_products,
            category="Gaming",
            record_id="test_record_123"
        )
        
        print(f"\n📊 Result:")
        print(f"Success: {result['success']}")
        if result['success']:
            print(f"Image URL: {result['image_url']}")
            print(f"Products featured: {result['products_featured']}")
            print(f"Model: {result['model']}")
        else:
            print(f"Error: {result['error']}")
        
        await generator.close()
    
    asyncio.run(test_intro_image())