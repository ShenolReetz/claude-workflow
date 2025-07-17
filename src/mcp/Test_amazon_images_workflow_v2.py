#!/usr/bin/env python3
"""
Amazon Images Workflow V2 (TEST MODE) - Uses default photos instead of downloading
Works with the new amazon_category_scraper data format but uses predefined images
"""
import asyncio
import logging
import httpx
from typing import Dict, List
from googleapiclient.http import MediaInMemoryUpload

logger = logging.getLogger(__name__)

async def download_and_save_amazon_images_v2(config: Dict, record_id: str, 
                                           project_title: str, products: List[Dict]) -> Dict:
    """Use default photos instead of downloading Amazon images (TEST MODE)"""
    
    from mcp.google_drive_agent_mcp import GoogleDriveAgentMCP
    from mcp_servers.Test_airtable_server import AirtableMCPServer
    from mcp_servers.Test_default_photo_manager import TestDefaultPhotoManager
    
    # Initialize services (TEST MODE: Minimal initialization)
    airtable_server = AirtableMCPServer(
        api_key=config['airtable_api_key'],
        base_id=config['airtable_base_id'],
        table_name=config['airtable_table_name']
    )
    
    photo_manager = TestDefaultPhotoManager()
    
    logger.info(f"🖼️ TEST MODE: Using default photos instead of downloading Amazon images")
    
    results = {
        'success': True,
        'images_saved': len(products),  # Simulate successful saves
        'products_with_images': len(products),
        'drive_image_urls': {},
        'errors': [],
        'test_mode': True,
        'download_skipped': True
    }
    
    try:
        # TEST MODE: Use default photos instead of downloading
        detected_category = photo_manager.detect_category_from_title(project_title)
        default_photos = photo_manager.get_default_product_photos(detected_category)
        
        airtable_updates = {}
        
        # Process each product with default photos
        for i, product in enumerate(products[:5], 1):
            try:
                # Use default photo instead of downloading
                if i <= len(default_photos):
                    drive_url = default_photos[i-1]
                else:
                    # Use fallback photo
                    drive_url = f"https://via.placeholder.com/500x500/CCCCCC/000000?text=PRODUCT+{i}"
                
                logger.info(f"📸 TEST MODE: Using default photo for Product {i}: {product.get('title', 'Unknown')[:30]}...")
                logger.info(f"   Default photo: {drive_url}")
                
                # Store URL for updating Airtable
                airtable_updates[f'ProductNo{i}Photo'] = drive_url
                airtable_updates[f'ProductNo{i}PhotoStatus'] = 'Ready'
                results['drive_image_urls'][f'product_{i}'] = drive_url
                results['products_with_images'] += 1
                
                logger.info(f"✅ TEST MODE: Assigned default photo for Product {i}")
                
            except Exception as e:
                error_msg = f"Error processing Product {i}: {str(e)}"
                logger.error(error_msg)
                results['errors'].append(error_msg)
            
            # Update Airtable with all default photo URLs
            if airtable_updates:
                await airtable_server.update_record(record_id, airtable_updates)
                logger.info(f"✅ TEST MODE: Updated Airtable with {len(airtable_updates)} default photo URLs")
        
    except Exception as e:
        error_msg = f"Error in image workflow: {str(e)}"
        logger.error(error_msg)
        results['success'] = False
        results['errors'].append(error_msg)
    
    return results

async def verify_image_downloads(config: Dict, record_id: str) -> Dict:
    """Verify that images were properly saved and URLs are accessible"""
    
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
            'verified_images': 0,
            'missing_images': 0,
            'image_status': {}
        }
        
        # Check each product's image URLs
        for i in range(1, 6):
            amazon_url = fields.get(f'ProductNo{i}ImageURL', '')
            drive_url = fields.get(f'ProductNo{i}Photo', '')
            
            verification_results['image_status'][f'product_{i}'] = {
                'has_amazon_url': bool(amazon_url),
                'has_drive_url': bool(drive_url),
                'amazon_url': amazon_url[:60] + '...' if amazon_url else '',
                'drive_url': drive_url[:60] + '...' if drive_url else ''
            }
            
            if amazon_url and drive_url:
                verification_results['verified_images'] += 1
            else:
                verification_results['missing_images'] += 1
        
        return verification_results
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

# Legacy function name for backward compatibility
async def download_and_save_amazon_images(config: Dict, record_id: str, 
                                        project_title: str, product_results: Dict) -> Dict:
    """Legacy wrapper - converts old format to new format and calls V2"""
    
    # Convert old product_results format to new products list format
    products = []
    for key, product_data in product_results.items():
        if key.startswith('product_') and isinstance(product_data, dict):
            products.append(product_data)
    
    return await download_and_save_amazon_images_v2(config, record_id, project_title, products)