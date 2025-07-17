#!/usr/bin/env python3
"""
Intro Image Generator
Creates intro images featuring all 5 products from the top 5 list
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

class IntroImageGenerator:
    """Generate intro images featuring all products"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.openai_api_key = config['openai_api_key']
        self.client = httpx.AsyncClient(timeout=86400)
        self.headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
    
    async def generate_intro_image(self, video_title: str, products: List[Dict], 
                                  category: str, record_id: str) -> Dict:
        """Generate intro image featuring all 5 products"""
        
        logger.info(f"🎨 Generating intro image for: {video_title}")
        
        # Build product list for prompt
        product_descriptions = []
        for i, product in enumerate(products[:5], 1):
            product_name = product.get('title', f'Product {i}')
            product_descriptions.append(f"{i}. {product_name}")
        
        # Create detailed prompt for intro image
        prompt = f"""Create a professional product showcase image for "{video_title}".

The image should feature all 5 products arranged in an appealing layout:
{chr(10).join(product_descriptions)}

Requirements:
- All 5 products should be visible and clearly displayed
- Arrange products in a dynamic, eye-catching composition
- Clean, modern background with subtle gradient
- Professional lighting that highlights each product
- Include subtle "#1-5" ranking indicators near each product
- Use warm, inviting colors that suggest quality and trust
- Products should appear to be floating or arranged on a clean surface
- Style should be suitable for a tech/product review video
- High resolution, commercial quality
- No text or logos overlaid on the image

Category: {category}
Style: Professional product photography, clean and modern
Lighting: Soft, even lighting with subtle shadows
Background: Clean gradient or solid color, not distracting
Composition: Dynamic arrangement showing all products clearly"""

        try:
            # Call OpenAI DALL-E 3 API
            response = await self.client.post(
                "https://api.openai.com/v1/images/generations",
                headers=self.headers,
                json={
                    "model": "dall-e-3",
                    "prompt": prompt,
                    "n": 1,
                    "size": "1024x1024",
                    "quality": "hd",
                    "response_format": "b64_json"
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                image_data = result['data'][0]['b64_json']
                
                # Save to Google Drive
                logger.info("☁️ Saving intro image to Google Drive...")
                drive_url = await self._save_to_drive(image_data, record_id, video_title)
                
                return {
                    'success': True,
                    'image_url': drive_url,
                    'prompt_used': prompt,
                    'products_featured': len(products),
                    'model': 'dall-e-3'
                }
            else:
                error_msg = f"OpenAI API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg
                }
                
        except Exception as e:
            logger.error(f"❌ Error generating intro image: {e}")
            return {
                'success': False,
                'error': str(e)
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
            from mcp_servers.airtable_server import AirtableMCPServer
            
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