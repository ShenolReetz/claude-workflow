#!/usr/bin/env python3
"""
ScrapingDog Amazon MCP Server - Production version with real API calls
Purpose: Professional Amazon scraping using ScrapingDog API for production use
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
import httpx
import json
import urllib.parse
from bs4 import BeautifulSoup
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScrapingDogAmazonMCPServer:
    """Production ScrapingDog Amazon MCP Server with real API calls"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.scrapingdog.com/scrape"
        logger.info("🔥 Production ScrapingDog Amazon Server initialized")
    
    async def scrape_products_with_reviews(self, search_query: str, max_products: int = 20) -> Dict[str, Any]:
        """Scrape real Amazon products using ScrapingDog API"""
        
        logger.info(f"🔍 Scraping products for '{search_query}' using ScrapingDog API")
        
        try:
            # Clean and prepare search query
            clean_query = urllib.parse.quote_plus(search_query.strip())
            amazon_url = f"https://www.amazon.com/s?k={clean_query}&ref=sr_st_relevancerank"
            
            # ScrapingDog API parameters
            params = {
                'api_key': self.api_key,
                'url': amazon_url,
                'premium': 'true',  # Use premium proxy for better success rate
                'country': 'US'     # Target US Amazon
            }
            
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(self.base_url, params=params)
                
                if response.status_code != 200:
                    logger.error(f"ScrapingDog API error: HTTP {response.status_code}")
                    return {
                        'success': False,
                        'error': f'ScrapingDog API returned HTTP {response.status_code}',
                        'products': []
                    }
                
                # Parse the HTML response
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find product containers
                product_containers = soup.select('[data-component-type="s-search-result"]')
                
                if not product_containers:
                    logger.warning(f"No products found for query: {search_query}")
                    return {
                        'success': True,
                        'products': [],
                        'message': f'No products found for "{search_query}"'
                    }
                
                products = []
                
                for container in product_containers[:max_products]:
                    try:
                        product_data = await self._extract_product_data(container)
                        if product_data:
                            products.append(product_data)
                    except Exception as e:
                        logger.warning(f"Error extracting product data: {str(e)}")
                        continue
                
                logger.info(f"✅ Successfully scraped {len(products)} products")
                
                return {
                    'success': True,
                    'products': products,
                    'total_found': len(products),
                    'search_query': search_query
                }
                
        except httpx.TimeoutException:
            logger.error("ScrapingDog API timeout")
            return {
                'success': False,
                'error': 'API timeout - Amazon scraping took too long',
                'products': []
            }
        except Exception as e:
            logger.error(f"Error scraping Amazon products: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'products': []
            }
    
    async def _extract_product_data(self, container) -> Optional[Dict[str, Any]]:
        """Extract product data from a container element"""
        
        try:
            # Extract ASIN
            asin = container.get('data-asin', '')
            if not asin:
                return None
            
            # Extract title
            title_elem = container.select_one('h2 a span')
            title = title_elem.get_text().strip() if title_elem else ''
            
            if not title:
                return None
            
            # Extract price
            price_elem = container.select_one('.a-price-whole')
            if not price_elem:
                price_elem = container.select_one('.a-price')
            
            price = ''
            if price_elem:
                price_text = price_elem.get_text().strip()
                # Clean price text
                price = re.sub(r'[^\d.,]', '', price_text)
                if price:
                    price = f"${price}"
                else:
                    price = "Price unavailable"
            else:
                price = "Price unavailable"
            
            # Extract rating
            rating_elem = container.select_one('.a-icon-alt')
            rating = 0.0
            if rating_elem:
                rating_text = rating_elem.get_text()
                rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                if rating_match:
                    rating = float(rating_match.group(1))
            
            # Extract review count
            review_elem = container.select_one('a .a-size-base')
            review_count = 0
            if review_elem:
                review_text = review_elem.get_text()
                # Extract numbers from review text like "2,847" or "1,234"
                review_match = re.search(r'([\d,]+)', review_text)
                if review_match:
                    review_count = int(review_match.group(1).replace(',', ''))
            
            # Extract image URL
            img_elem = container.select_one('img.s-image')
            image_url = ''
            if img_elem:
                image_url = img_elem.get('src', '') or img_elem.get('data-src', '')
                # Convert to higher resolution if possible
                image_url = image_url.replace('_AC_UL320_', '_AC_UL1500_')
            
            # Generate Amazon product URL
            product_url = f"https://www.amazon.com/dp/{asin}"
            
            product_data = {
                'title': title,
                'image_url': image_url,
                'rating': rating,
                'review_count': review_count,
                'price': price,
                'asin': asin,
                'url': product_url
            }
            
            # Only return products with meaningful data
            if title and asin:
                return product_data
            
            return None
            
        except Exception as e:
            logger.warning(f"Error extracting product data: {str(e)}")
            return None
    
    async def scrape_amazon_products_advanced(self, search_query: str, max_products: int = 10) -> Dict[str, Any]:
        """Advanced Amazon product scraping with enhanced data extraction"""
        
        logger.info(f"🚀 Advanced scraping for '{search_query}'")
        
        # Use the main scraping method
        result = await self.scrape_products_with_reviews(search_query, max_products)
        
        if result['success'] and result['products']:
            # Enhance products with additional processing
            enhanced_products = []
            
            for product in result['products']:
                # Clean title
                product['title'] = self._clean_product_title(product['title'])
                
                # Validate data
                if self._validate_product_data(product):
                    enhanced_products.append(product)
            
            result['products'] = enhanced_products
            result['enhanced'] = True
            
            logger.info(f"✅ Advanced scraping complete: {len(enhanced_products)} validated products")
        
        return result
    
    def _clean_product_title(self, title: str) -> str:
        """Clean and optimize product title"""
        
        if not title:
            return "Unknown Product"
        
        # Remove excessive whitespace
        title = re.sub(r'\s+', ' ', title.strip())
        
        # Remove common Amazon clutter
        title = re.sub(r'\s*\(.*?\)\s*', ' ', title)  # Remove parentheses
        title = re.sub(r'\s*\[.*?\]\s*', ' ', title)  # Remove brackets
        
        # Limit length for readability
        if len(title) > 80:
            title = title[:77] + "..."
        
        return title.strip()
    
    def _validate_product_data(self, product: Dict[str, Any]) -> bool:
        """Validate that product has required data"""
        
        required_fields = ['title', 'asin']
        
        for field in required_fields:
            if not product.get(field):
                return False
        
        # Ensure rating is reasonable
        rating = product.get('rating', 0)
        if rating < 0 or rating > 5:
            product['rating'] = 4.0  # Default reasonable rating
        
        # Ensure review count is reasonable
        review_count = product.get('review_count', 0)
        if review_count < 0:
            product['review_count'] = 0
        
        return True


# Test function for development
async def test_scrapingdog_server():
    """Test the ScrapingDog server"""
    
    # Note: This requires a real ScrapingDog API key
    # Replace with your actual API key for testing
    test_api_key = "your_scrapingdog_api_key_here"
    
    server = ScrapingDogAmazonMCPServer(test_api_key)
    
    # Test search
    result = await server.scrape_products_with_reviews("wireless headphones", max_products=5)
    
    if result['success']:
        print(f"✅ Found {len(result['products'])} products")
        for i, product in enumerate(result['products'][:3], 1):
            print(f"   {i}. {product['title'][:50]}...")
            print(f"      Rating: {product['rating']}, Reviews: {product['review_count']}")
            print(f"      Price: {product['price']}")
    else:
        print(f"❌ Test failed: {result['error']}")


if __name__ == "__main__":
    asyncio.run(test_scrapingdog_server())