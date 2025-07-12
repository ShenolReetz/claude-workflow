#!/usr/bin/env python3
"""
Amazon Images Workflow V2 - Downloads and saves product images to Google Drive
Works with the new amazon_category_scraper data format
"""
import asyncio
import logging
import httpx
from typing import Dict, List
from googleapiclient.http import MediaInMemoryUpload

logger = logging.getLogger(__name__)

async def download_and_save_amazon_images_v2(config: Dict, record_id: str, 
                                           project_title: str, products: List[Dict]) -> Dict:
    """Download Amazon product images and save to Google Drive using new scraper format"""
    
    from mcp.google_drive_agent_mcp import GoogleDriveAgentMCP
    from mcp_servers.airtable_server import AirtableMCPServer
    
    # Initialize services
    drive_agent = GoogleDriveAgentMCP(config)
    drive_service = await drive_agent.initialize()
    airtable_server = AirtableMCPServer(
        api_key=config['airtable_api_key'],
        base_id=config['airtable_base_id'],
        table_name=config['airtable_table_name']
    )
    
    results = {
        'success': True,
        'images_saved': 0,
        'products_with_images': 0,
        'drive_image_urls': {},
        'errors': []
    }
    
    try:
        # Get folder structure
        n8n_folder = await drive_agent._find_or_create_folder('N8N Projects', None)
        project_folder = await drive_agent._find_or_create_folder(project_title[:50], n8n_folder)
        photos_folder = await drive_agent._find_or_create_folder('Photos', project_folder)
        
        # HTTP client for downloading images
        async with httpx.AsyncClient(timeout=30.0) as client:
            airtable_updates = {}
            
            # Process each product
            for i, product in enumerate(products[:5], 1):
                try:
                    image_url = product.get('image_url', '')
                    if not image_url:
                        logger.warning(f"No image URL for Product {i}")
                        continue
                    
                    logger.info(f"📸 Downloading image for Product {i}: {product['title'][:30]}...")
                    
                    # Download image
                    response = await client.get(image_url)
                    response.raise_for_status()
                    
                    # Generate filename
                    filename = f"Product{i}_{product['asin']}_amazon.jpg"
                    
                    # Upload to Google Drive
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
                    
                    # Update Airtable with Drive image URL
                    airtable_updates[f'ProductNo{i}DriveImageURL'] = drive_url
                    
                    results['images_saved'] += 1
                    results['products_with_images'] += 1
                    results['drive_image_urls'][f'product_{i}'] = drive_url
                    
                    logger.info(f"✅ Saved {filename} to Google Drive")
                    
                except Exception as e:
                    error_msg = f"Error processing Product {i}: {str(e)}"
                    logger.error(error_msg)
                    results['errors'].append(error_msg)
            
            # Update Airtable with all Drive image URLs
            if airtable_updates:
                await airtable_server.update_record(record_id, airtable_updates)
                logger.info(f"✅ Updated Airtable with {len(airtable_updates)} Drive image URLs")
        
    except Exception as e:
        error_msg = f"Error in image workflow: {str(e)}"
        logger.error(error_msg)
        results['success'] = False
        results['errors'].append(error_msg)
    
    return results

async def verify_image_downloads(config: Dict, record_id: str) -> Dict:
    """Verify that images were properly saved and URLs are accessible"""
    
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
            'verified_images': 0,
            'missing_images': 0,
            'image_status': {}
        }
        
        # Check each product's image URLs
        for i in range(1, 6):
            amazon_url = fields.get(f'ProductNo{i}ImageURL', '')
            drive_url = fields.get(f'ProductNo{i}DriveImageURL', '')
            
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