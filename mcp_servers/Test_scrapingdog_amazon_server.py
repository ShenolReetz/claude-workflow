#!/usr/bin/env python3
"""
ScrapingDog Amazon Scraper - Using ScrapingDog API for reliable Amazon scraping
"""
import asyncio
import json
import logging
import re
from typing import Dict, List, Optional
from urllib.parse import quote
import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class ScrapingDogAmazonServer:
    """Amazon scraper using ScrapingDog API"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.api_key = config.get('scrapingdog_api_key', '')
        self.affiliate_tag = config.get('amazon_affiliate_tag', 'your-tag-20')
        self.base_url = 'https://api.scrapingdog.com/scrape'
        
        if not self.api_key:
            logger.warning("ScrapingDog API key not found in config!")
    
    async def search_product(self, product_name: str) -> Dict:
        """Search for a product on Amazon using ScrapingDog"""
        try:
            # Clean product name
            search_query = re.sub(r'[^\w\s\-]', '', product_name).strip()
            
            # Amazon search URL
            target_url = f"https://www.amazon.com/s?k={quote(search_query)}"
            
            # ScrapingDog parameters
            params = {
                'api_key': self.api_key,
                'url': target_url,
                'dynamic': 'false',
                'country': 'us'
            }
            
            logger.info(f"🔍 Searching Amazon via ScrapingDog for: {search_query}")
            
            async with httpx.AsyncClient(timeout=86400) as client:
                response = await client.get(self.base_url, params=params)
                
                if response.status_code != 200:
                    logger.error(f"ScrapingDog API error: {response.status_code}")
                    return {'success': False, 'error': f'API error: {response.status_code}'}
                
                # Parse the HTML response
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find products
                products = soup.select('[data-component-type="s-search-result"]')
                
                if not products:
                    logger.warning(f"No products found for: {product_name}")
                    return {'success': False, 'error': 'No products found'}
                
                # Extract first product details
                product = products[0]
                asin = product.get('data-asin', '')
                
                if not asin:
                    return {'success': False, 'error': 'No ASIN found'}
                
                # Extract product info
                title_elem = product.select_one('h2 a span')
                title = title_elem.text.strip() if title_elem else product_name
                
                price_elem = product.select_one('.a-price-whole')
                price = price_elem.text.strip() if price_elem else 'N/A'
                
                img_elem = product.select_one('img.s-image')
                image_url = img_elem.get('src', '') if img_elem else ''
                
                # Generate affiliate link
                affiliate_link = f"https://www.amazon.com/dp/{asin}?tag={self.affiliate_tag}"
                
                logger.info(f"✅ Found product: {title} (ASIN: {asin})")
                
                return {
                    'success': True,
                    'asin': asin,
                    'title': title,
                    'price': price,
                    'image_url': image_url,
                    'affiliate_link': affiliate_link,
                    'product_url': f"https://www.amazon.com/dp/{asin}"
                }
                
        except Exception as e:
            logger.error(f"Error searching for {product_name}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def get_product_details(self, asin: str) -> Dict:
        """Get detailed product information including all images"""
        try:
            target_url = f"https://www.amazon.com/dp/{asin}"
            
            params = {
                'api_key': self.api_key,
                'url': target_url,
                'dynamic': 'true',  # Use dynamic rendering for product pages
                'country': 'us'
            }
            
            logger.info(f"📖 Getting product details for ASIN: {asin}")
            
            async with httpx.AsyncClient(timeout=86400) as client:
                response = await client.get(self.base_url, params=params)
                
                if response.status_code != 200:
                    return {'success': False, 'error': f'API error: {response.status_code}'}
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract images
                images = []
                
                # Main image
                main_img = soup.select_one('#landingImage')
                if main_img and main_img.get('src'):
                    images.append(main_img['src'])
                
                # Gallery images  
                gallery_imgs = soup.select('#altImages img')
                for img in gallery_imgs[:10]:  # Limit to 10 images
                    src = img.get('src', '')
                    if src and 'ssl-images-amazon' in src:
                        # Get high-res version
                        high_res = src.replace('._AC_US40_', '._AC_SL1500_')
                        high_res = high_res.replace('._AC_SR38,50_', '._AC_SL1500_')
                        if high_res not in images:
                            images.append(high_res)
                
                # Product title
                title_elem = soup.select_one('#productTitle')
                title = title_elem.text.strip() if title_elem else 'Unknown Product'
                
                # Price
                price_elem = soup.select_one('.a-price-whole')
                if not price_elem:
                    price_elem = soup.select_one('#priceblock_dealprice, #priceblock_ourprice')
                price = price_elem.text.strip() if price_elem else 'N/A'
                
                # Rating
                rating_elem = soup.select_one('span.a-icon-alt')
                rating = rating_elem.text.split()[0] if rating_elem else 'N/A'
                
                return {
                    'success': True,
                    'asin': asin,
                    'title': title,
                    'price': price,
                    'rating': rating,
                    'images': images,
                    'image_count': len(images)
                }
                
        except Exception as e:
            logger.error(f"Error getting product details for {asin}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    
    async def get_amazon_product(self, asin: str, domain: str = 'com') -> Dict:
        """Get product using ScrapingDog Amazon Product API"""
        try:
            # Use the dedicated Amazon product endpoint
            url = 'https://api.scrapingdog.com/amazon/product'
            
            params = {
                'api_key': self.api_key,
                'domain': domain,
                'asin': asin,
                'country': 'us'
            }
            
            logger.info(f"📦 Getting Amazon product data for ASIN: {asin}")
            
            async with httpx.AsyncClient(timeout=86400) as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        'success': True,
                        'title': data.get('title', ''),
                        'price': data.get('price', 'N/A'),
                        'description': data.get('description', ''),
                        'images': data.get('images', []),
                        'brand': data.get('brand', ''),
                        'rating': data.get('average_rating', 0),
                        'features': data.get('feature_bullets', []),
                        'availability': data.get('availability_status', '')
                    }
                else:
                    return {'success': False, 'error': f'API error: {response.status_code}'}
                    
        except Exception as e:
            logger.error(f"Error getting product {asin}: {str(e)}")
            return {'success': False, 'error': str(e)}

    async def process_products_batch(self, products: List[Dict]) -> Dict:
        """Process multiple products"""
        results = []
        
        for i, product in enumerate(products, 1):
            product_name = product.get('title', f'Product {i}')
            logger.info(f"🔍 Processing Product{i}: {product_name}")
            
            # Search for product
            search_result = await self.search_product(product_name)
            
            if search_result['success']:
                # Get detailed info including images
                details = await self.get_product_details(search_result['asin'])
                if details['success']:
                    search_result['images'] = details.get('images', [])
                    search_result['rating'] = details.get('rating', 'N/A')
            
            search_result['product_number'] = i
            results.append(search_result)
            
            # Small delay between requests
            if i < len(products):
                await asyncio.sleep(1)
        
        successful = sum(1 for r in results if r['success'])
        logger.info(f"✅ Successfully processed {successful}/{len(products)} products")
        
        return {
            'success': True,
            'total_products': len(products),
            'successful': successful,
            'results': results
        }
