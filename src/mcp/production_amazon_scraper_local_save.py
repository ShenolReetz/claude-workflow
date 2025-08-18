#!/usr/bin/env python3
"""
Amazon Scraper with Local Image Storage
========================================
Downloads and saves Amazon product images locally
for use as references in image generation.
"""

import aiohttp
import asyncio
from typing import Dict, List, Optional
import logging
from pathlib import Path
from src.utils.dual_storage_manager import get_storage_manager

logger = logging.getLogger(__name__)


async def download_and_save_amazon_images_local(record: Dict, config: Dict) -> Dict:
    """
    Download Amazon scraped images and save them locally
    These can be used as references for image generation
    """
    try:
        storage_manager = get_storage_manager(config)
        fields = record.get('fields', {})
        record_id = record.get('record_id', 'unknown')
        
        logger.info(f"📥 Downloading Amazon product images for local storage...")
        
        # Download tasks
        tasks = []
        for i in range(1, 6):
            amazon_url = fields.get(f'ProductNo{i}Photo', '')
            if amazon_url and amazon_url.startswith('http'):
                task = download_single_image(
                    storage_manager=storage_manager,
                    url=amazon_url,
                    product_num=i,
                    record_id=record_id
                )
                tasks.append((i, task))
        
        if not tasks:
            logger.warning("No Amazon images to download")
            return {
                'success': True,
                'images_downloaded': 0,
                'updated_record': record
            }
        
        # Download all images concurrently
        results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
        
        # Process results
        success_count = 0
        local_paths = {}
        
        for (product_num, _), result in zip(tasks, results):
            if isinstance(result, Exception):
                logger.error(f"Failed to download product {product_num} image: {result}")
            elif result and result.get('success'):
                local_path = result.get('local_path')
                if local_path:
                    # Store both original URL and local path
                    fields[f'ProductNo{product_num}Photo_AmazonURL'] = fields.get(f'ProductNo{product_num}Photo', '')
                    fields[f'ProductNo{product_num}Photo_Local'] = local_path
                    local_paths[f'product{product_num}'] = local_path
                    success_count += 1
                    logger.info(f"✅ Saved Amazon image for product {product_num}: {local_path}")
        
        record['fields'] = fields
        
        logger.info(f"📊 Downloaded {success_count}/{len(tasks)} Amazon images locally")
        
        return {
            'success': True,
            'images_downloaded': success_count,
            'local_paths': local_paths,
            'updated_record': record
        }
        
    except Exception as e:
        logger.error(f"Error downloading Amazon images: {e}")
        return {
            'success': False,
            'error': str(e),
            'updated_record': record
        }


async def download_single_image(storage_manager, url: str, product_num: int, record_id: str) -> Dict:
    """Download a single Amazon image"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=30) as response:
                if response.status == 200:
                    content = await response.read()
                    
                    # Save with descriptive filename
                    filename = f"amazon_product{product_num}.jpg"
                    
                    result = await storage_manager.save_media(
                        content=content,
                        filename=filename,
                        media_type="image",
                        record_id=record_id,
                        upload_to_drive=False  # Local only
                    )
                    
                    return result
                else:
                    return {'success': False, 'error': f'HTTP {response.status}'}
                    
    except Exception as e:
        return {'success': False, 'error': str(e)}