#!/usr/bin/env python3
"""
Amazon-Guided OpenAI Image Generation
Uses Amazon product photos as reference for generating enhanced OpenAI images
"""
import asyncio
import logging
from typing import Dict, List
import httpx
from googleapiclient.http import MediaInMemoryUpload

logger = logging.getLogger(__name__)

async def generate_amazon_guided_openai_images(config: Dict, record_id: str, 
                                             project_title: str, products: List[Dict]) -> Dict:
    """Generate OpenAI images using Amazon photos as reference and save to Google Drive"""
    
    from mcp.google_drive_agent_mcp import GoogleDriveAgentMCP
    from mcp_servers.airtable_server import AirtableMCPServer
    from mcp_servers.image_generation_server import ImageGenerationMCPServer
    
    # Initialize services
    drive_agent = GoogleDriveAgentMCP(config)
    drive_service = await drive_agent.initialize()
    
    airtable_server = AirtableMCPServer(
        api_key=config['airtable_api_key'],
        base_id=config['airtable_base_id'],
        table_name=config['airtable_table_name']
    )
    
    image_generator = ImageGenerationMCPServer(config['openai_api_key'])
    
    results = {
        'success': True,
        'images_generated': 0,
        'images_saved': 0,
        'products_processed': 0,
        'openai_image_urls': {},
        'drive_image_urls': {},
        'errors': []
    }
    
    try:
        # Get folder structure - use same Photos folder as Amazon images
        folder_structure = await drive_agent.drive_server.create_project_structure(project_title[:50])
        photos_folder = folder_structure.get('photos')
        
        if not photos_folder:
            raise Exception("Failed to create Photos folder structure")
            
        logger.info(f"📁 Using Photos folder: {photos_folder}")
        
        # HTTP client for downloading generated images
        async with httpx.AsyncClient(timeout=60.0) as client:
            airtable_updates = {}
            
            # Process each product with Amazon reference
            for i, product in enumerate(products[:5], 1):
                try:
                    product_name = product.get('title', '')
                    amazon_image_url = product.get('image_url', '')
                    
                    if not product_name:
                        logger.warning(f"No product name for Product {i}")
                        continue
                    
                    logger.info(f"🎨 Generating OpenAI image for Product {i}: {product_name[:40]}...")
                    
                    # Generate image using Amazon reference
                    if amazon_image_url:
                        product_details = {
                            'price': product.get('price', ''),
                            'rating': product.get('rating', ''),
                            'reviews': product.get('reviews', ''),
                            'asin': product.get('asin', '')
                        }
                        
                        openai_image_url = await image_generator.generate_product_image_with_amazon_reference(
                            product_name, i, amazon_image_url, product_details
                        )
                        logger.info(f"✅ Generated Amazon-guided image using reference: {amazon_image_url[:50]}...")
                    else:
                        # Fallback to regular generation
                        logger.warning(f"No Amazon reference for Product {i}, using standard generation")
                        openai_image_url = await image_generator.generate_product_image(product_name, i)
                    
                    if not openai_image_url:
                        logger.error(f"Failed to generate image for Product {i}")
                        continue
                    
                    results['images_generated'] += 1
                    results['openai_image_urls'][f'product_{i}'] = openai_image_url
                    
                    # Download the generated image
                    logger.info(f"📥 Downloading generated image for Product {i}...")
                    response = await client.get(openai_image_url)
                    response.raise_for_status()
                    
                    # Generate filename for OpenAI image
                    filename = f"Product{i}_OpenAI_guided.jpg"
                    
                    # Upload to Google Drive Photos folder
                    logger.info(f"📤 Uploading {filename} to Google Drive...")
                    media = MediaInMemoryUpload(
                        response.content,
                        mimetype='image/jpeg',
                        resumable=True
                    )
                    
                    file_metadata = {
                        'name': filename,
                        'parents': [photos_folder]
                    }
                    
                    uploaded_file = drive_service.files().create(
                        body=file_metadata,
                        media_body=media,
                        fields='id,webViewLink,webContentLink'
                    ).execute()
                    
                    # Get the Drive URL
                    drive_url = uploaded_file.get('webViewLink', '')
                    
                    # Update Airtable with OpenAI Drive image URL
                    airtable_updates[f'ProductNo{i}OpenAIImageURL'] = drive_url
                    
                    results['images_saved'] += 1
                    results['products_processed'] += 1
                    results['drive_image_urls'][f'product_{i}'] = drive_url
                    
                    logger.info(f"✅ Saved {filename} to Google Drive: {drive_url[:50]}...")
                    
                    # Rate limiting - important for OpenAI API
                    if i < len(products):
                        logger.info(f"⏳ Rate limiting: waiting 5 seconds...")
                        await asyncio.sleep(5)
                    
                except Exception as e:
                    error_msg = f"Error processing Product {i}: {str(e)}"
                    logger.error(error_msg)
                    results['errors'].append(error_msg)
            
            # Update Airtable with all OpenAI Drive image URLs
            if airtable_updates:
                logger.info(f"💾 Updating Airtable with {len(airtable_updates)} OpenAI image URLs...")
                await airtable_server.update_record(record_id, airtable_updates)
                logger.info(f"✅ Updated Airtable with OpenAI image URLs")
        
    except Exception as e:
        error_msg = f"Error in Amazon-guided image generation: {str(e)}"
        logger.error(error_msg)
        results['success'] = False
        results['errors'].append(error_msg)
    
    return results

async def verify_openai_image_generation(config: Dict, record_id: str) -> Dict:
    """Verify that OpenAI images were properly generated and saved"""
    
    from mcp_servers.airtable_server import AirtableMCPServer
    
    airtable_server = AirtableMCPServer(
        api_key=config['airtable_api_key'],
        base_id=config['airtable_base_id'],
        table_name=config['airtable_table_name']
    )
    
    try:
        # Get record from Airtable
        record = await airtable_server.get_record_by_id(record_id)
        
        if not record:
            return {'success': False, 'error': 'Record not found'}
        
        fields = record.get('fields', {})
        verification_results = {
            'success': True,
            'verified_openai_images': 0,
            'missing_openai_images': 0,
            'image_comparison': {}
        }
        
        # Check each product's image URLs (Amazon vs OpenAI)
        for i in range(1, 6):
            amazon_url = fields.get(f'ProductNo{i}ImageURL', '')
            amazon_drive_url = fields.get(f'ProductNo{i}DriveImageURL', '')
            openai_drive_url = fields.get(f'ProductNo{i}OpenAIImageURL', '')
            
            verification_results['image_comparison'][f'product_{i}'] = {
                'has_amazon_url': bool(amazon_url),
                'has_amazon_drive_url': bool(amazon_drive_url),
                'has_openai_drive_url': bool(openai_drive_url),
                'amazon_url': amazon_url[:60] + '...' if amazon_url else '',
                'amazon_drive_url': amazon_drive_url[:60] + '...' if amazon_drive_url else '',
                'openai_drive_url': openai_drive_url[:60] + '...' if openai_drive_url else ''
            }
            
            if openai_drive_url:
                verification_results['verified_openai_images'] += 1
            else:
                verification_results['missing_openai_images'] += 1
        
        return verification_results
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

# Test function
async def test_amazon_guided_generation():
    """Test the Amazon-guided OpenAI image generation"""
    
    import json
    
    # Load config
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    # Test products (simulated from Amazon scraper)
    test_products = [
        {
            'title': 'Apple AirPods Pro (2nd Generation)',
            'asin': 'B0BV9F196L',
            'price': '$199.99',
            'rating': '4.5',
            'reviews': '41609',
            'image_url': 'https://m.media-amazon.com/images/I/71AWFpvx0XL._AC_UY218_.jpg'
        }
    ]
    
    print("🧪 Testing Amazon-guided OpenAI image generation...")
    
    results = await generate_amazon_guided_openai_images(
        config=config,
        record_id='test_record',
        project_title='Test Amazon Guided Images',
        products=test_products
    )
    
    print(f"✅ Test Results:")
    print(f"  Images Generated: {results['images_generated']}")
    print(f"  Images Saved: {results['images_saved']}")
    print(f"  Products Processed: {results['products_processed']}")
    if results['errors']:
        print(f"  Errors: {results['errors']}")

if __name__ == "__main__":
    asyncio.run(test_amazon_guided_generation())