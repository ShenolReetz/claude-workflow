#!/usr/bin/env python3
"""
Test Amazon Category Scraper - Hardcoded responses for testing
"""
import asyncio
import json
import logging
import time
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class TestAmazonCategoryScraper:
    """Test version with hardcoded Amazon product data"""
    
    def __init__(self, scrapingdog_api_key: str = None, config: Dict = None):
        self.config = config
        self.affiliate_tag = 'reviewch3kr0d-20'
        self.last_request_time = 0
        self.min_delay = 0.1  # Minimal delay for testing
        
        print("🧪 TEST MODE: Amazon Category Scraper using hardcoded responses")
        logger.info("🧪 Test Amazon Category Scraper initialized")
    
    def extract_category_from_title(self, title: str) -> str:
        """Extract category keywords from Airtable title"""
        # Simplified extraction for testing
        title_lower = title.lower()
        prefixes = ['top 5', 'best 5', 'top', 'best']
        
        for prefix in prefixes:
            if title_lower.startswith(prefix):
                title_lower = title_lower[len(prefix):].strip()
        
        # Remove common suffixes
        suffixes = ['category', '2025', '2024']
        for suffix in suffixes:
            if title_lower.endswith(suffix):
                title_lower = title_lower[:-len(suffix)].strip()
        
        return title_lower.strip()
    
    async def rate_limit(self):
        """Minimal rate limiting for test mode"""
        await asyncio.sleep(self.min_delay)
        self.last_request_time = time.time()
    
    async def search_category_products(self, category_title: str, max_products: int = 20) -> List[Dict]:
        """Return hardcoded product data for testing"""
        try:
            await self.rate_limit()
            
            category = self.extract_category_from_title(category_title)
            print(f"🧪 TEST: Searching Amazon category: {category}")
            logger.info(f"🔍 Test searching Amazon category: {category}")
            
            # Hardcoded product data based on category
            test_products = [
                {
                    'asin': 'B08TEST123',
                    'title': f'Top Rated {category.title()} Product #1 with Premium Features',
                    'price': '$49.99',
                    'rating': 4.8,
                    'review_count': 2150,
                    'review_score': 10320.0,
                    'image_url': 'https://test-images.amazonaws.com/product1.jpg',
                    'affiliate_link': f'https://www.amazon.com/dp/B08TEST123?tag={self.affiliate_tag}'
                },
                {
                    'asin': 'B08TEST456',
                    'title': f'Best Selling {category.title()} with 5-Star Reviews',
                    'price': '$79.99',
                    'rating': 4.7,
                    'review_count': 1850,
                    'review_score': 8695.0,
                    'image_url': 'https://test-images.amazonaws.com/product2.jpg',
                    'affiliate_link': f'https://www.amazon.com/dp/B08TEST456?tag={self.affiliate_tag}'
                },
                {
                    'asin': 'B08TEST789',
                    'title': f'Professional Grade {category.title()} for Advanced Users',
                    'price': '$129.99',
                    'rating': 4.6,
                    'review_count': 1420,
                    'review_score': 6532.0,
                    'image_url': 'https://test-images.amazonaws.com/product3.jpg',
                    'affiliate_link': f'https://www.amazon.com/dp/B08TEST789?tag={self.affiliate_tag}'
                },
                {
                    'asin': 'B08TEST101',
                    'title': f'Premium {category.title()} with Latest Technology',
                    'price': '$89.99',
                    'rating': 4.5,
                    'review_count': 980,
                    'review_score': 4410.0,
                    'image_url': 'https://test-images.amazonaws.com/product4.jpg',
                    'affiliate_link': f'https://www.amazon.com/dp/B08TEST101?tag={self.affiliate_tag}'
                },
                {
                    'asin': 'B08TEST202',
                    'title': f'Budget-Friendly {category.title()} with Great Value',
                    'price': '$29.99',
                    'rating': 4.4,
                    'review_count': 750,
                    'review_score': 3300.0,
                    'image_url': 'https://test-images.amazonaws.com/product5.jpg',
                    'affiliate_link': f'https://www.amazon.com/dp/B08TEST202?tag={self.affiliate_tag}'
                }
            ]
            
            # Sort by review score (already pre-sorted in hardcoded data)
            logger.info(f"✅ Test: Successfully generated {len(test_products)} hardcoded products")
            print(f"🧪 TEST: Generated {len(test_products)} hardcoded products for {category}")
            
            return test_products[:5]  # Return top 5 products
                
        except Exception as e:
            logger.error(f"Test error searching category {category_title}: {str(e)}")
            return []
    
    async def get_top_5_products(self, category_title: str) -> Dict:
        """Get hardcoded top 5 products for testing"""
        try:
            print(f"🧪 TEST: Getting top 5 products for: {category_title}")
            
            # Get hardcoded products
            products = await self.search_category_products(category_title)
            
            if not products:
                return {
                    'success': False,
                    'error': 'No test products generated',
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
                    price_clean = price_str.replace('$', '').replace(',', '').replace(' ', '')
                    try:
                        price_num = float(price_clean)
                        airtable_data[f'ProductNo{i}Price'] = price_num
                        logger.info(f"✅ Test price for product {i}: ${price_num}")
                    except ValueError:
                        airtable_data[f'ProductNo{i}Price'] = 0.0
                        logger.warning(f"⚠️ Test: Could not convert price '{price_str}', using 0.0")
                else:
                    airtable_data[f'ProductNo{i}Price'] = 0.0
                
                airtable_data[f'ProductNo{i}Rating'] = str(product['rating'])
                airtable_data[f'ProductNo{i}Reviews'] = str(product['review_count'])
                airtable_data[f'ProductNo{i}Score'] = str(product['review_score'])
                
                # Add to product results for other uses
                product_results[f'product_{i}'] = product
            
            logger.info(f"✅ Test: Selected top 5 products based on review score")
            print(f"🧪 TEST: Top 5 products generated successfully")
            for i, product in enumerate(products[:5], 1):
                logger.info(f"  {i}. {product['title'][:50]}... (Score: {product['review_score']:.0f})")
            
            return {
                'success': True,
                'products': products[:5],
                'airtable_data': airtable_data,
                'product_results': product_results,
                'total_found': len(products),
                'test_mode': True,
                'api_usage': 0  # No API tokens used in test mode
            }
            
        except Exception as e:
            logger.error(f"Test error getting top 5 products: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'products': [],
                'test_mode': True
            }

# Test function
if __name__ == "__main__":
    async def test_scraper():
        config = {
            'scrapingdog_api_key': 'test-key',
            'amazon_associate_id': 'reviewch3kr0d-20'
        }
        
        scraper = TestAmazonCategoryScraper(config)
        
        test_titles = [
            "Top 5 Gaming Headsets",
            "Best Car Amplifiers 2025",
            "Top Marine Subwoofers"
        ]
        
        for title in test_titles:
            print(f"\n🧪 Testing: {title}")
            result = await scraper.get_top_5_products(title)
            print(f"Result: {'✅ Success' if result['success'] else '❌ Failed'}")
            if result['success']:
                print(f"Products: {len(result['products'])}")
    
    asyncio.run(test_scraper())