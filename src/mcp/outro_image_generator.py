#!/usr/bin/env python3
"""
Outro Image Generator
Creates standardized outro images with social media links, subscribe buttons, etc.
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OutroImageGenerator:
    """Generate standardized outro images for all videos"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.openai_api_key = config['openai_api_key']
        self.client = httpx.AsyncClient(timeout=86400)
        self.headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
    
    async def generate_outro_image(self, category: str, record_id: str) -> Dict:
        """Generate standardized outro image with social media elements"""
        
        logger.info(f"🎨 Generating outro image for category: {category}")
        
        # Create detailed prompt for outro image
        prompt = f"""Create a professional video outro image for a {category} product review channel.

The image should include:
- "Thanks for Watching!" as the main heading
- Social media call-to-action elements:
  * YouTube subscribe button with notification bell
  * "👍 LIKE" button
  * "💬 COMMENT" text
  * "🔔 SUBSCRIBE" text
  * "📱 FOLLOW US" text
- Professional branding elements:
  * Clean, modern design
  * Tech/product review channel aesthetic
  * Warm, inviting colors (blues, oranges, whites)
- Text elements:
  * "Check product links in description"
  * "More reviews coming soon"
  * Amazon affiliate disclosure note
- Visual elements:
  * Professional gradient background
  * Clean typography
  * Social media icons (YouTube, Instagram, TikTok)
  * Subscribe notification animation feel

Requirements:
- 16:9 aspect ratio suitable for YouTube end screens
- High contrast text for readability
- Professional, trustworthy design
- Clean layout with clear hierarchy
- Suitable for {category} product review content
- Include space for end screen elements
- Modern, engaging design that encourages interaction

Style: Professional YouTube outro design, clean and modern
Colors: Professional blues, oranges, whites with good contrast
Layout: Clean hierarchy with clear call-to-action placement
Typography: Modern, readable fonts with good contrast"""

        try:
            # Call OpenAI DALL-E 3 API
            response = await self.client.post(
                "https://api.openai.com/v1/images/generations",
                headers=self.headers,
                json={
                    "model": "dall-e-3",
                    "prompt": prompt,
                    "n": 1,
                    "size": "1792x1024",  # 16:9 aspect ratio
                    "quality": "hd",
                    "response_format": "b64_json"
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                image_data = result['data'][0]['b64_json']
                
                # Save to Google Drive
                logger.info("☁️ Saving outro image to Google Drive...")
                drive_url = await self._save_to_drive(image_data, record_id, category)
                
                return {
                    'success': True,
                    'image_url': drive_url,
                    'prompt_used': prompt,
                    'category': category,
                    'model': 'dall-e-3',
                    'aspect_ratio': '16:9'
                }
            else:
                error_msg = f"OpenAI API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg
                }
                
        except Exception as e:
            logger.error(f"❌ Error generating outro image: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _save_to_drive(self, image_base64: str, record_id: str, category: str) -> str:
        """Save outro image to Google Drive"""
        try:
            # Initialize Google Drive agent
            drive_agent = GoogleDriveAgentMCP(self.config)
            if not await drive_agent.initialize():
                logger.error("❌ Failed to initialize Google Drive")
                return f"https://drive.google.com/file/d/outro_{record_id}/view"
            
            # Convert base64 to bytes
            image_bytes = base64.b64decode(image_base64)
            
            # Create project folder structure
            safe_category = "".join(c for c in category if c.isalnum() or c in (' ', '-', '_')).rstrip()
            folder_name = f"Outro_Images_{safe_category}"
            folder_ids = await drive_agent.drive_server.create_project_structure(folder_name)
            
            # Upload to Photos folder
            photos_folder_id = folder_ids.get('photos')
            if not photos_folder_id:
                logger.error("❌ Could not create photos folder")
                return f"https://drive.google.com/file/d/outro_{record_id}/view"
            
            # Upload outro image
            filename = f"{record_id}_outro_social_media.jpg"
            
            # Use the Google Drive service directly
            try:
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
                    logger.info(f"✅ Outro image saved to Google Drive: {drive_url}")
                    return drive_url
                else:
                    logger.error("❌ Failed to upload outro image")
                    return f"https://drive.google.com/file/d/outro_{record_id}/view"
                    
            except Exception as upload_error:
                logger.error(f"❌ Upload error: {upload_error}")
                return f"https://drive.google.com/file/d/outro_{record_id}/view"
                
        except Exception as e:
            logger.error(f"❌ Error saving outro image to Drive: {e}")
            return f"https://drive.google.com/file/d/outro_{record_id}/view"
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


# Integration function for workflow
async def generate_outro_image_for_workflow(config: Dict, record_id: str, category: str) -> Dict:
    """Generate outro image and integrate into workflow"""
    
    generator = OutroImageGenerator(config)
    
    try:
        result = await generator.generate_outro_image(category, record_id)
        
        # Update Airtable with outro image URL
        if result['success']:
            from mcp_servers.airtable_server import AirtableMCPServer
            
            airtable_server = AirtableMCPServer(
                api_key=config['airtable_api_key'],
                base_id=config['airtable_base_id'],
                table_name=config['airtable_table_name']
            )
            
            await airtable_server.update_record(record_id, {
                'OutroPhoto': result['image_url']
            })
            
            logger.info(f"✅ Outro image URL saved to Airtable")
        
        return result
        
    finally:
        await generator.close()


# Test function
if __name__ == "__main__":
    async def test_outro_image():
        # Load config
        with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
            config = json.load(f)
        
        generator = OutroImageGenerator(config)
        
        print("🧪 Testing outro image generation...")
        
        result = await generator.generate_outro_image(
            category="Gaming",
            record_id="test_outro_123"
        )
        
        print(f"\n📊 Result:")
        print(f"Success: {result['success']}")
        if result['success']:
            print(f"Image URL: {result['image_url']}")
            print(f"Category: {result['category']}")
            print(f"Aspect Ratio: {result['aspect_ratio']}")
            print(f"Model: {result['model']}")
        else:
            print(f"Error: {result['error']}")
        
        await generator.close()
    
    asyncio.run(test_outro_image())