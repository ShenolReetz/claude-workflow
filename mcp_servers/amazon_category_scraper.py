#!/usr/bin/env python3
"""
Amazon Category Scraper - Searches products by category and ranks by Reviews × Rating
"""
import asyncio
import json
import logging
import re
import time
from typing import Dict, List, Optional
from urllib.parse import quote
import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class AmazonCategoryScraper:
    """Scrapes Amazon products by category and ranks them by review score"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.api_key = config.get('scrapingdog_api_key', '')
        self.affiliate_tag = config.get('amazon_associate_id', 'reviewch3kr0d-20')
        self.base_url = 'https://api.scrapingdog.com/scrape'
        self.last_request_time = 0
        self.min_delay = 6  # ScrapingDog requires 6 second delays
        
        if not self.api_key:
            logger.warning("ScrapingDog API key not found in config!")
    
    def extract_category_from_title(self, title: str) -> str:
        """Extract category keywords from Airtable title"""
        # Remove common prefixes
        title_lower = title.lower()
        prefixes = [
            'top 5 products based on amazon', 
            'top 5 products based on', 
            'top 5', 'best 5', 'top', 'best',
            'editor\'s picks', 'picks'
        ]
        
        for prefix in prefixes:
            if title_lower.startswith(prefix):
                title_lower = title_lower[len(prefix):].strip()
        
        # Remove common suffixes
        suffixes = ['category', 'editor\'s picks', 'picks', '2025', '2024']
        for suffix in suffixes:
            if title_lower.endswith(suffix):
                title_lower = title_lower[:-len(suffix)].strip()
        
        # Clean up common words that don't help search
        cleanup_words = ['&', 'accessories']
        for word in cleanup_words:
            if word in title_lower:
                title_lower = title_lower.replace(word, ' ').strip()
        
        # Clean up multiple spaces
        title_lower = ' '.join(title_lower.split())
        
        return title_lower.strip()
    
    async def rate_limit(self):
        """Implement rate limiting for ScrapingDog"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_delay:
            delay = self.min_delay - time_since_last
            logger.info(f"Rate limiting: waiting {delay:.2f} seconds")
            await asyncio.sleep(delay)
        
        self.last_request_time = time.time()
    
    async def search_category_products(self, category_title: str, max_products: int = 20) -> List[Dict]:
        """Search Amazon for products in a category and return top products by review score"""
        try:
            await self.rate_limit()
            
            # Extract category from title
            category = self.extract_category_from_title(category_title)
            logger.info(f"🔍 Searching Amazon category: {category}")
            
            # Amazon search URL
            target_url = f"https://www.amazon.com/s?k={quote(category)}&s=review-rank"
            
            # ScrapingDog parameters
            params = {
                'api_key': self.api_key,
                'url': target_url,
                'dynamic': 'false',
                'country': 'us'
            }
            
            async with httpx.AsyncClient(timeout=86400) as client:
                response = await client.get(self.base_url, params=params)
                
                if response.status_code == 429:
                    logger.error("ScrapingDog rate limit hit. Waiting 10 seconds...")
                    await asyncio.sleep(10)
                    return []
                
                if response.status_code != 200:
                    logger.error(f"ScrapingDog API error: {response.status_code}")
                    return []
                
                # Parse the HTML response
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find all products
                products = soup.select('[data-component-type="s-search-result"]')
                
                if not products:
                    logger.warning(f"No products found for category: {category}")
                    return []
                
                logger.info(f"Found {len(products)} products in search results")
                
                # Extract product details
                product_list = []
                for product in products[:max_products]:
                    try:
                        asin = product.get('data-asin', '')
                        if not asin:
                            continue
                        
                        # Title - try multiple selectors for robustness
                        title = ''
                        title_selectors = ['h2 span', '.a-link-normal span', 'h2 a span', 'h2']
                        for selector in title_selectors:
                            title_elem = product.select_one(selector)
                            if title_elem:
                                title = title_elem.text.strip()
                                if title:  # Only use if we got actual text
                                    break
                        
                        # Price - try multiple selectors for better accuracy
                        price = 'N/A'
                        
                        # Try different price selectors in order of preference
                        price_selectors = [
                            '.a-price-whole',  # Whole price part
                            '.a-price .a-offscreen',  # Full price with cents
                            '.a-price-symbol + .a-price-whole',  # Price with symbol
                            '.a-price .a-price-range .a-price-whole',  # Price range
                            '.a-price',  # General price container
                            '.a-price-value',  # Price value
                            '.a-price-display'  # Price display
                        ]
                        
                        for selector in price_selectors:
                            price_elem = product.select_one(selector)
                            if price_elem:
                                price_text = price_elem.text.strip()
                                if price_text and price_text != 'N/A':
                                    price = price_text
                                    break
                        
                        # Clean up price text and add $ if missing
                        if price != 'N/A':
                            # Remove extra whitespace and clean up
                            price = price.replace('\n', '').replace('\t', '').strip()
                            # Add $ symbol if not present
                            if not price.startswith('$') and price != 'N/A':
                                price = f'${price}'
                        
                        # Rating
                        rating_elem = product.select_one('span.a-icon-alt')
                        rating_text = rating_elem.text if rating_elem else '0 out of 5 stars'
                        rating = float(rating_text.split()[0]) if rating_text else 0.0
                        
                        # Review count
                        review_elem = product.select_one('span.a-size-base.s-underline-text')
                        review_text = review_elem.text.strip() if review_elem else '0'
                        # Extract number from text like "1,234" or "1234"
                        review_count = int(review_text.replace(',', '')) if review_text.replace(',', '').isdigit() else 0
                        
                        # Image
                        img_elem = product.select_one('img.s-image')
                        image_url = img_elem.get('src', '') if img_elem else ''
                        
                        # Calculate review score (reviews × rating)
                        review_score = review_count * rating
                        
                        product_data = {
                            'asin': asin,
                            'title': title,
                            'price': price,
                            'rating': rating,
                            'review_count': review_count,
                            'review_score': review_score,
                            'image_url': image_url,
                            'affiliate_link': f"https://www.amazon.com/dp/{asin}?tag={self.affiliate_tag}"
                        }
                        
                        product_list.append(product_data)
                        
                    except Exception as e:
                        logger.warning(f"Error parsing product: {e}")
                        continue
                
                # Sort by review score (reviews × rating)
                product_list.sort(key=lambda x: x['review_score'], reverse=True)
                
                logger.info(f"✅ Successfully scraped {len(product_list)} products")
                return product_list[:5]  # Return top 5 products
                
        except Exception as e:
            logger.error(f"Error searching category {category_title}: {str(e)}")
            return []
    
    async def get_top_5_products(self, category_title: str) -> Dict:
        """Get top 5 products for a category based on review score"""
        try:
            # Search for products
            products = await self.search_category_products(category_title)
            
            if not products:
                return {
                    'success': False,
                    'error': 'No products found',
                    'products': []
                }
            
            # Format results for Airtable
            airtable_data = {}
            product_results = {}
            
            for i, product in enumerate(products[:5], 1):
                # Add to Airtable fields
                airtable_data[f'ProductNo{i}Title'] = product['title']
                airtable_data[f'ProductNo{i}AffiliateLink'] = product['affiliate_link']
                airtable_data[f'ProductNo{i}Photo'] = product['image_url']
                # Convert price to number format for Airtable
                price_str = product['price']
                if isinstance(price_str, str) and price_str != 'N/A':
                    # Remove $ symbol, commas, and other non-numeric characters
                    price_clean = price_str.replace('$', '').replace(',', '').replace(' ', '')
                    
                    # Handle price ranges (e.g., "49.99-59.99" -> take the lower price)
                    if '-' in price_clean:
                        price_clean = price_clean.split('-')[0]
                    
                    # Handle fractional prices like "49.99"
                    try:
                        price_num = float(price_clean)
                        airtable_data[f'ProductNo{i}Price'] = price_num
                        logger.info(f"✅ Price for product {i}: ${price_num}")
                    except ValueError:
                        # If conversion fails, store as 0
                        airtable_data[f'ProductNo{i}Price'] = 0.0
                        logger.warning(f"⚠️ Could not convert price '{price_str}' to number, using 0.0")
                else:
                    # If price is N/A or not a string, store as 0
                    airtable_data[f'ProductNo{i}Price'] = 0.0
                    logger.warning(f"⚠️ No valid price found for product {i}, using 0.0")
                airtable_data[f'ProductNo{i}Rating'] = product['rating']  # Keep as number
                airtable_data[f'ProductNo{i}Reviews'] = product['review_count']  # Keep as number
                # airtable_data[f'ProductNo{i}Score'] = product['review_score']  # Field doesn't exist in Airtable
                
                # Add to product results for other uses
                product_results[f'product_{i}'] = product
            
            logger.info(f"✅ Selected top 5 products based on review score")
            for i, product in enumerate(products[:5], 1):
                logger.info(f"  {i}. {product['title'][:50]}... (Score: {product['review_score']:.0f})")
            
            return {
                'success': True,
                'products': products[:5],
                'airtable_data': airtable_data,
                'product_results': product_results,
                'total_found': len(products)
            }
            
        except Exception as e:
            logger.error(f"Error getting top 5 products: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'products': []
            }