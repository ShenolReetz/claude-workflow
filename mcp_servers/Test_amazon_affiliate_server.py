#!/usr/bin/env python3
"""
Amazon Affiliate MCP Server
Server implementation for Amazon affiliate link generation
"""

import asyncio
import json
import re
import time
import random
import logging
from typing import List, Dict, Optional, Any
from urllib.parse import quote_plus

import httpx
from bs4 import BeautifulSoup

# ScrapingDog integration
try:
    from mcp_servers.Test_scrapingdog_amazon_server import ScrapingDogAmazonServer
    SCRAPINGDOG_AVAILABLE = True
except ImportError:
    SCRAPINGDOG_AVAILABLE = False
    ScrapingDogAmazonServer = None

# Test default affiliate manager
from mcp_servers.Test_default_affiliate_manager import TestDefaultAffiliateManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AmazonAffiliateMCPServer:
    """Amazon Affiliate MCP Server - handles the actual Amazon API interactions"""
    
    def __init__(self, associate_id: str, config: Dict[str, Any]):
        self.associate_id = associate_id
        self.config = config
        
        # Initialize default affiliate manager for TEST MODE
        self.affiliate_manager = TestDefaultAffiliateManager()
        
        # Rate limiting for Amazon searches
        self.last_request_time = 0
        self.min_delay = 2  # Minimum 2 seconds between requests
        self.max_delay = 5  # Maximum 5 seconds between requests
        
        # HTTP client with proper headers to avoid blocking
        self.client = httpx.AsyncClient(
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0'
            },
            timeout=86400,
            follow_redirects=True
        )
        
        # Initialize ScrapingDog if available
        self.scrapingdog = None
        if SCRAPINGDOG_AVAILABLE and config.get('scrapingdog_api_key'):
            try:
                self.scrapingdog = ScrapingDogAmazonServer(config)
                logger.info("✅ ScrapingDog enabled for Amazon searches")
            except Exception as e:
                logger.warning(f"Failed to initialize ScrapingDog: {e}")


    async def rate_limit(self):
        """Implement rate limiting for Amazon requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_delay:
            delay = random.uniform(self.min_delay, self.max_delay)
            logger.info(f"Rate limiting: waiting {delay:.2f} seconds")
            await asyncio.sleep(delay)
        
        self.last_request_time = time.time()

    def clean_search_query(self, product_title: str) -> str:
        """Clean product title for better Amazon search results"""
        # Remove common words that might confuse search
        stop_words = ['top', 'best', 'good', 'great', 'review', 'reviews', '2025', '2024', 'for', 'new', 'latest']
        
        # Remove numbers from titles like "Top 5"
        title = re.sub(r'\btop\s+\d+\b', '', product_title.lower())
        title = re.sub(r'\b\d+\s+(best|top|new)\b', '', title)
        
        # Split title and remove stop words
        words = title.split()
        cleaned_words = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Take first 5-6 words to keep search focused
        return ' '.join(cleaned_words[:6])

    def build_affiliate_link(self, asin: str) -> str:
        """Build official Amazon affiliate link from ASIN"""
        return f"https://www.amazon.com/dp/{asin}/ref=nosim?tag={self.associate_id}"

    async def search_amazon_product(self, product_title: str) -> Optional[Dict[str, str]]:
        """
        Search Amazon for a product and return ASIN + basic info
        
        Args:
            product_title: The product name to search for
            
        Returns:
            Dict with 'asin', 'title', 'url', 'image', 'price' or None if not found
        """

        # Try ScrapingDog first if available
        if self.scrapingdog:
            try:
                logger.info(f"🔍 Using ScrapingDog for: {product_title}")
                result = await self.scrapingdog.search_product(product_title)
                if result.get('success'):
                    return {
                        'asin': result['asin'],
                        'title': result['title'],
                        'price': result.get('price', 'N/A'),
                        'url': result.get('product_url', ''),
                        'affiliate_link': result['affiliate_link'],
                        'image_url': result.get('image_url', '')
                    }
            except Exception as e:
                logger.warning(f"ScrapingDog error: {e}, falling back to direct search")
        
        # Original search logic with retry for 503 errors
        max_retries = 3
        retry_delay = 5  # Start with 5 seconds
        
        for attempt in range(max_retries):
            try:
                await self.rate_limit()
                
                # Clean and encode the search query
                search_query = self.clean_search_query(product_title)
                encoded_query = quote_plus(search_query)
                
                # Amazon search URL
                search_url = f"https://www.amazon.com/s?k={encoded_query}&ref=nb_sb_noss"
                
                logger.info(f"Searching Amazon for: '{search_query}' (from: {product_title}) - Attempt {attempt + 1}/{max_retries}")
                
                response = await self.client.get(search_url)
                
                # Check for 503 errors specifically
                if response.status_code == 503:
                    if attempt < max_retries - 1:
                        logger.warning(f"Amazon returned 503 Service Unavailable (attempt {attempt + 1}/{max_retries})")
                        logger.info(f"Retrying in {retry_delay} seconds...")
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                        continue
                    else:
                        logger.error(f"Amazon 503 error after {max_retries} attempts, giving up")
                        return None
                
                response.raise_for_status()
                break  # Success, exit retry loop
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Error on attempt {attempt + 1}/{max_retries}: {e}")
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                else:
                    logger.error(f"Error searching Amazon for '{product_title}': {str(e)}")
                    return None
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find product results (excluding sponsored content)
        products = self.extract_products_from_search(soup)
        
        if products:
            # Return the first non-sponsored product
            product = products[0]
            logger.info(f"Found product: {product['title'][:50]}... ASIN: {product['asin']}")
            return product
        else:
            logger.warning(f"No products found for: {search_query}")
            return None

    def extract_products_from_search(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract product information from Amazon search results"""
        products = []
        
        # Look for product containers (Amazon uses different selectors)
        selectors = [
            '[data-component-type="s-search-result"]',
            '.s-result-item[data-component-type="s-search-result"]',
            '[data-asin]:not([data-asin=""])'
        ]
        
        items = []
        for selector in selectors:
            items = soup.select(selector)
            if items:
                logger.info(f"Found {len(items)} items using selector: {selector}")
                break
        
        for item in items[:10]:  # Only take first 10 results
            try:
                # Skip sponsored content
                sponsored_indicators = [
                    '.s-sponsored-label-text',
                    '[data-component-type="sp-sponsored-result"]',
                    '.AdHolder',
                    '.s-label-sponsored'
                ]
                
                is_sponsored = any(item.select(indicator) for indicator in sponsored_indicators)
                if is_sponsored:
                    continue
                
                # Extract ASIN from data attribute or URL
                asin = self.extract_asin_from_element(item)
                if not asin:
                    continue
                
                # Extract title
                title_selectors = [
                    'h2 a span',
                    '.s-title-instructions-style span',
                    'h2 span'
                ]
                
                title = None
                for title_selector in title_selectors:
                    title_element = item.select_one(title_selector)
                    if title_element:
                        title = title_element.get_text(strip=True)
                        break
                
                if not title or len(title) < 5:
                    continue
                
                # Extract image
                img_element = item.select_one('img')
                image_url = None
                if img_element:
                    image_url = img_element.get('src') or img_element.get('data-src')
                
                # Build product URL
                product_url = f"https://www.amazon.com/dp/{asin}"
                
                products.append({
                    'asin': asin,
                    'title': title,
                    'url': product_url,
                    'image': image_url
                })
                
                # We found a good product, that's enough
                if len(products) >= 1:
                    break
                
            except Exception as e:
                logger.warning(f"Error extracting product from element: {str(e)}")
                continue
        
        return products

    def extract_asin_from_element(self, element) -> Optional[str]:
        """Extract ASIN from product element"""
        # Try data-asin attribute first
        asin = element.get('data-asin')
        if asin and len(asin) == 10:
            return asin
        
        # Try to find ASIN in URLs within the element
        links = element.select('a[href]')
        for link in links:
            href = link.get('href', '')
            asin_match = re.search(r'/dp/([A-Z0-9]{10})', href)
            if asin_match:
                return asin_match.group(1)
        
        return None

    async def search_and_generate_link(self, product_title: str, product_number: int) -> Dict[str, Any]:
        """Search for a single product and generate affiliate link"""
        try:
            product_info = await self.search_amazon_product(product_title)
            
            if product_info:
                affiliate_link = self.build_affiliate_link(product_info['asin'])
                return {
                    'success': True,
                    'product_number': product_number,
                    'title': product_title,
                    'asin': product_info['asin'],
                    'affiliate_link': affiliate_link,
                    'amazon_title': product_info['title']
                }
            else:
                return {
                    'success': False,
                    'product_number': product_number,
                    'title': product_title,
                    'error': 'Product not found on Amazon'
                }
        
        except Exception as e:
            return {
                'success': False,
                'product_number': product_number,
                'title': product_title,
                'error': str(e)
            }

    async def generate_affiliate_links_batch(self, record_id: str, product_titles: List[Dict]) -> Dict[str, Any]:
        """Generate affiliate links for a batch of products (TEST MODE: Uses default links)"""
        logger.info(f"🔗 TEST MODE: Using default affiliate links instead of scraping")
        logger.info(f"📦 Processing {len(product_titles)} products with pre-generated data")
        
        affiliate_links = {}
        results = []
        
        # Extract category from first product title for category-specific links
        category = self._detect_category(product_titles[0]['title'] if product_titles else '')
        
        for product_info in product_titles:
            product_number = product_info['number']
            product_title = product_info['title']
            
            logger.info(f"🔍 TEST MODE: Using default data for Product{product_number}: {product_title}")
            
            # Get default affiliate data instead of scraping
            affiliate_data = self.affiliate_manager.get_affiliate_link(product_number, category)
            
            # Format result to match expected structure
            result = {
                'success': True,
                'affiliate_link': affiliate_data['affiliate_link'],
                'price': affiliate_data['price'],
                'rating': affiliate_data['rating'],
                'reviews': affiliate_data['reviews'],
                'title': affiliate_data['title'],
                'description': affiliate_data['description'],
                'product_number': product_number,
                'source': 'TEST_MODE_DEFAULT'
            }
            
            affiliate_link_key = f'ProductNo{product_number}AffiliateLink'
            affiliate_links[affiliate_link_key] = result['affiliate_link']
            
            # Also add pricing data to affiliate_links for Airtable update
            affiliate_links[f'ProductNo{product_number}Price'] = result['price']
            affiliate_links[f'ProductNo{product_number}Rating'] = result['rating']
            affiliate_links[f'ProductNo{product_number}Reviews'] = result['reviews']
            
            logger.info(f"✅ TEST MODE: Using default affiliate link for Product{product_number}")
            logger.info(f"💰 Price: {result['price']} | Rating: {result['rating']}⭐ | Reviews: {result['reviews']}")
            
            results.append(result)
        
        logger.info(f"✅ TEST MODE: Generated {len(affiliate_links)} affiliate fields using defaults")
        logger.info(f"💸 Cost savings: Avoided {len(product_titles)} Amazon API calls")
        
        return {
            'record_id': record_id,
            'affiliate_links': affiliate_links,
            'results': results
        }
    
    def _detect_category(self, title: str) -> Optional[str]:
        """Detect product category from title for category-specific affiliate links"""
        title_lower = title.lower()
        
        # Category mappings
        if any(word in title_lower for word in ['gaming', 'computer', 'tech', 'electronics', 'rgb']):
            return 'electronics'
        elif any(word in title_lower for word in ['kitchen', 'home', 'house', 'counter']):
            return 'home_kitchen'
        elif any(word in title_lower for word in ['car', 'auto', 'vehicle', 'automotive']):
            return 'automotive'
        elif any(word in title_lower for word in ['sports', 'outdoor', 'fitness', 'exercise']):
            return 'sports_outdoors'
        elif any(word in title_lower for word in ['beauty', 'personal', 'care', 'cosmetic']):
            return 'beauty_personal_care'
        elif any(word in title_lower for word in ['fashion', 'clothing', 'style', 'apparel']):
            return 'fashion'
        
        return None  # Use default category

    async def close(self):
        """Clean up resources"""
        await self.client.aclose()

# Test function
async def test_server():
    """Test the Amazon Affiliate Server"""
    config = {'amazon_associate_id': 'reviewch3kr0d-20'}
    server = AmazonAffiliateMCPServer('reviewch3kr0d-20', config)
    
    # Test search
    print("🧪 Testing Amazon search...")
    result = await server.search_amazon_product("Sony WH-1000XM4 Wireless Headphones")
    print(f"Search result: {json.dumps(result, indent=2)}")
    
    if result:
        affiliate_link = server.build_affiliate_link(result['asin'])
        print(f"Affiliate link: {affiliate_link}")
    
    await server.close()

if __name__ == "__main__":
    asyncio.run(test_server())
