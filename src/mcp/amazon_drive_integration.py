#!/usr/bin/env python3
import asyncio
import logging
from typing import Dict, List
from googleapiclient.http import MediaInMemoryUpload
import sys
sys.path.append('/home/claude-workflow')

from mcp_servers.enhanced_amazon_scraper import EnhancedAmazonScraper
from mcp.google_drive_agent_mcp import GoogleDriveAgentMCP

logger = logging.getLogger(__name__)

async def save_amazon_images_to_drive(config: Dict, record_id: str, 
                                    project_title: str, products: List[Dict]) -> Dict:
    """Save Amazon product images to Google Drive"""
    
    scraper = EnhancedAmazonScraper(config)
    drive_agent = GoogleDriveAgentMCP(config)
    drive_service = await drive_agent.initialize()
    
    results = {
        'success': True,
        'products_processed': 0,
        'images_saved': 0,
        'affiliate_links': []
    }
    
    n8n_folder_id = await drive_agent._find_or_create_folder('N8N Projects', None)
    project_folder_id = await drive_agent._find_or_create_folder(
        project_title[:50], n8n_folder_id
    )
    photos_folder_id = await drive_agent._find_or_create_folder(
        'Photos', project_folder_id
    )
    affiliate_folder_id = await drive_agent._find_or_create_folder(
        'Affiliate Links', project_folder_id
    )
    
    for i, product in enumerate(products, 1):
        if not product.get('title'):
            continue
            
        logger.info(f"📦 Processing Product {i}: {product['title']}")
        
        scrape_result = await scraper.scrape_product_with_images(product['title'])
        
        if scrape_result['success']:
            product_folder = await drive_agent._find_or_create_folder(
                f"Product{i}_{product['title'][:30].replace(' ', '_')}", 
                photos_folder_id
            )
            
            for idx, img_url in enumerate(scrape_result['images'], 1):
                img_data = await scraper.download_image(img_url)
                if img_data:
                    filename = f"Product{i}_img{idx}.jpg"
                    
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
            
            results['affiliate_links'].append({
                'product_num': i,
                'title': product['title'],
                'affiliate_link': scrape_result['affiliate_link'],
                'asin': scrape_result['asin']
            })
        
        results['products_processed'] += 1
        await asyncio.sleep(3)
    
    affiliate_content = "Amazon Affiliate Links\n" + "=" * 30 + "\n\n"
    for link_info in results['affiliate_links']:
        affiliate_content += f"Product {link_info['product_num']}: {link_info['title']}\n"
        affiliate_content += f"ASIN: {link_info['asin']}\n"
        affiliate_content += f"Link: {link_info['affiliate_link']}\n\n"
    
    media = MediaInMemoryUpload(
        affiliate_content.encode('utf-8'),
        mimetype='text/plain'
    )
    
    drive_service.files().create(
        body={
            'name': 'affiliate_links.txt',
            'parents': [affiliate_folder_id]
        },
        media_body=media,
        fields='id'
    ).execute()
    
    logger.info(f"✅ Amazon image workflow complete: {results}")
    return results
