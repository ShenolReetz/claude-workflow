#!/usr/bin/env python3
"""
Amazon-Guided OpenAI Image Generation (TEST MODE)
Uses default photos instead of generating new images for faster testing
"""
import asyncio
import logging
from typing import Dict, List
import httpx
from googleapiclient.http import MediaInMemoryUpload

logger = logging.getLogger(__name__)

async def generate_amazon_guided_openai_images(config: Dict, record_id: str, 
                                             project_title: str, products: List[Dict]) -> Dict:
    """Use default photos instead of generating OpenAI images (TEST MODE)"""
    
    from mcp.google_drive_agent_mcp import GoogleDriveAgentMCP
    from mcp_servers.Test_airtable_server import AirtableMCPServer
    from mcp_servers.Test_image_generation_server import ImageGenerationMCPServer
    from mcp_servers.Test_default_photo_manager import TestDefaultPhotoManager
    
    # Initialize services (TEST MODE: Minimal initialization)
    airtable_server = AirtableMCPServer(
        api_key=config['airtable_api_key'],
        base_id=config['airtable_base_id'],
        table_name=config['airtable_table_name']
    )
    
    photo_manager = TestDefaultPhotoManager()
    
    logger.info(f"🎨 TEST MODE: Using default photos instead of generating OpenAI images")
    
    results = {
        'success': True,
        'images_generated': len(products),  # Simulate generated images
        'images_saved': len(products),     # Simulate saved images
        'products_processed': len(products),
        'openai_image_urls': {},
        'drive_image_urls': {},
        'errors': [],
        'test_mode': True,
        'generation_skipped': True
    }
    
    try:
        # TEST MODE: Use default photos for guided image generation
        detected_category = photo_manager.detect_category_from_title(project_title)
        default_photos = photo_manager.get_default_product_photos(detected_category)
        
        logger.info(f"🎨 TEST MODE: Using category '{detected_category}' default photos")
        logger.info(f"📊 Available default photos: {len(default_photos)}")
        
        # Return success without actually generating or saving anything
        for i, product in enumerate(products[:5], 1):
            if i <= len(default_photos):
                default_url = default_photos[i-1]
                results['openai_image_urls'][f'product_{i}'] = default_url
                results['drive_image_urls'][f'product_{i}'] = default_url
                logger.info(f"✅ TEST MODE: Product {i} assigned default photo")
        
        logger.info(f"✅ TEST MODE: Completed guided image generation simulation")
        logger.info(f"📊 Simulated {results['images_generated']} generated images")
        
    except Exception as e:
        error_msg = f"Error in TEST MODE guided image generation: {str(e)}"
        logger.error(error_msg)
        results['success'] = False
        results['errors'].append(error_msg)
    
    return results

async def verify_openai_image_generation(config: Dict, record_id: str) -> Dict:
    """Verify that OpenAI images were properly generated and saved"""
    
    from mcp_servers.Test_airtable_server import AirtableMCPServer
    
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
            amazon_drive_url = fields.get(f'ProductNo{i}Photo', '')
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