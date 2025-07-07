#!/usr/bin/env python3
"""
Amazon Images Workflow - Downloads and saves product images to Google Drive
"""
import asyncio
import logging
from typing import Dict, List
from googleapiclient.http import MediaInMemoryUpload

logger = logging.getLogger(__name__)

async def download_and_save_amazon_images(config: Dict, record_id: str, 
                                        project_title: str, affiliate_results: Dict) -> Dict:
    """Download Amazon product images and save to Google Drive"""
    
    from mcp.google_drive_agent_mcp import GoogleDriveAgentMCP
    from mcp_servers.amazon_affiliate_server import AmazonAffiliateMCP
    
    # Initialize services
    drive_agent = GoogleDriveAgentMCP(config)
    drive_service = await drive_agent.initialize()
    amazon_mcp = AmazonAffiliateMCP(config)
    
    results = {
        'success': True,
        'images_saved': 0,
        'products_with_images': 0
    }
    
    # Get folder structure
    n8n_folder = await drive_agent._find_or_create_folder('N8N Projects', None)
    project_folder = await drive_agent._find_or_create_folder(project_title[:50], n8n_folder)
    photos_folder = await drive_agent._find_or_create_folder('Photos', project_folder)
    
    # Process each product that has images
    for product_num, result in affiliate_results.items():
        if result.get('success') and result.get('images'):
            logger.info(f"📸 Saving images for Product {product_num}")
            
            # Create product folder
            product_folder = await drive_agent._find_or_create_folder(
                f"Product{product_num}", photos_folder
            )
            
            # Download and save each image
            for idx, img_url in enumerate(result['images'], 1):
                try:
                    img_data = await amazon_mcp.download_image(img_url)
                    if img_data:
                        filename = f"Product{product_num}_amazon_img{idx}.jpg"
                        
                        media = MediaInMemoryUpload(
                            img_data,
                            mimetype='image/jpeg',
                            resumable=True
                        )
                        
                        file_metadata = {
                            'name': filename,
                            'parents': [product_folder]
                        }
                        
                        drive_service.files().create(
                            body=file_metadata,
                            media_body=media,
                            fields='id'
                        ).execute()
                        
                        results['images_saved'] += 1
                        logger.info(f"✅ Saved {filename}")
                        
                except Exception as e:
                    logger.error(f"Error saving image: {str(e)}")
            
            results['products_with_images'] += 1
    
    return results
