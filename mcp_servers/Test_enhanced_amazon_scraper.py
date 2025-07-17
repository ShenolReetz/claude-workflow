#!/usr/bin/env python3
import asyncio
import json
import logging
import re
import random
from typing import Dict, List, Optional
from datetime import datetime
import httpx
from bs4 import BeautifulSoup
import urllib.parse

logger = logging.getLogger(__name__)

class EnhancedAmazonScraper:
    def __init__(self, config: Dict):
        self.config = config
        self.affiliate_tag = config.get('amazon_affiliate_tag', 'your-tag-20')
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9'
        }
    
    async def scrape_product_with_images(self, product_name: str) -> Dict:
        """Scrape product including images"""
        try:
            search_query = re.sub(r'[^\w\s\-]', '', product_name).strip()
            search_url = f"https://www.amazon.com/s?k={urllib.parse.quote(search_query)}"
            
            await asyncio.sleep(random.uniform(2, 4))
            
            async with httpx.AsyncClient(timeout=86400, headers=self.headers) as client:
                response = await client.get(search_url)
                
                if response.status_code == 503:
                    self.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
                    await asyncio.sleep(5)
                    response = await client.get(search_url)
                
                if response.status_code != 200:
                    return {'success': False, 'error': f'HTTP {response.status_code}'}
                
                soup = BeautifulSoup(response.text, 'html.parser')
                products = soup.select('[data-component-type="s-search-result"]')
                
                if not products:
                    return {'success': False, 'error': 'No products found'}
                
                product = products[0]
                asin = product.get('data-asin', '')
                
                if not asin:
                    return {'success': False, 'error': 'No ASIN found'}
                
                title_elem = product.select_one('h2 a span')
                title = title_elem.text.strip() if title_elem else product_name
                
                price_elem = product.select_one('.a-price-whole')
                price = price_elem.text.strip() if price_elem else 'N/A'
                
                img_elem = product.select_one('img.s-image')
                main_image = img_elem.get('src', '') if img_elem else ''
                
                await asyncio.sleep(2)
                product_url = f"https://www.amazon.com/dp/{asin}"
                product_response = await client.get(product_url)
                
                images = [main_image] if main_image else []
                
                if product_response.status_code == 200:
                    product_soup = BeautifulSoup(product_response.text, 'html.parser')
                    img_containers = product_soup.select('#altImages img')
                    for img in img_containers[:5]:
                        src = img.get('src', '')
                        if src and 'ssl-images-amazon' in src:
                            high_res = src.replace('._AC_US40_', '._AC_SL1500_')
                            if high_res not in images:
                                images.append(high_res)
                
                affiliate_link = f"https://www.amazon.com/dp/{asin}?tag={self.affiliate_tag}"
                
                return {
                    'success': True,
                    'asin': asin,
                    'title': title,
                    'price': price,
                    'affiliate_link': affiliate_link,
                    'images': images
                }
                
        except Exception as e:
            logger.error(f"Error scraping {product_name}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def download_image(self, image_url: str) -> Optional[bytes]:
        """Download image data"""
        try:
            async with httpx.AsyncClient(timeout=86400) as client:
                response = await client.get(image_url)
                if response.status_code == 200:
                    return response.content
        except Exception as e:
            logger.error(f"Error downloading image: {str(e)}")
        return None
