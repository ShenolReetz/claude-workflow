#!/usr/bin/env python3
"""
TEST Amazon Category Scraper - Hardcoded data for faster testing
"""
import asyncio
import json
import logging
import re
import time
from typing import Dict, List, Optional
from urllib.parse import quote
import httpx

logger = logging.getLogger(__name__)

class AmazonCategoryScraper:
    """TEST MODE: Hardcoded Amazon products for faster testing without API calls"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.api_key = config.get('scrapingdog_api_key', '')
        self.affiliate_tag = config.get('amazon_associate_id', 'reviewch3kr0d-20')
        
        # TEST MODE: Hardcoded product data for different categories
        self.hardcoded_products = {
            'electronics': [
                {
                    'title': 'Digital Camera for Kids, WITYEAH 48MP FHD 1080P',
                    'url': 'https://amazon.com/dp/B01234567',
                    'price': '$29.00',
                    'rating': 3.8,
                    'review_count': 1436,
                    'score': 5457  # rating * review_count
                },
                {
                    'title': 'Digital Camera, 4K 64MP, 18X Zoom',
                    'url': 'https://amazon.com/dp/B01234568',
                    'price': '$44.00',
                    'rating': 4.3,
                    'review_count': 262,
                    'score': 1127
                },
                {
                    'title': '4K Digital Camera, 64MP Dual-Lens Vlogging Camera',
                    'url': 'https://amazon.com/dp/B01234569',
                    'price': '$69.00',
                    'rating': 4.6,
                    'review_count': 219,
                    'score': 1007
                },
                {
                    'title': 'Security Cameras Wireless Outdoor - HD 2K Battery',
                    'url': 'https://amazon.com/dp/B01234570',
                    'price': '$28.00',
                    'rating': 3.5,
                    'review_count': 208,
                    'score': 728
                },
                {
                    'title': 'True 5K Digital Camera for Photography, Autofocus',
                    'url': 'https://amazon.com/dp/B01234571',
                    'price': '$99.00',
                    'rating': 4.7,
                    'review_count': 190,
                    'score': 893
                }
            ],
            'fashion': [
                {
                    'title': 'Bands Compatible with ID205L Smart Watch, 19mm',
                    'url': 'https://amazon.com/dp/B01234572',
                    'price': '$5.00',
                    'rating': 4.8,
                    'review_count': 2234,
                    'score': 10723
                },
                {
                    'title': 'ZURURU Soft Silicone Smart Watch Replacement Bands',
                    'url': 'https://amazon.com/dp/B01234573',
                    'price': '$7.00',
                    'rating': 4.6,
                    'review_count': 1598,
                    'score': 7351
                },
                {
                    'title': 'Runostrich Quick Release Nylon Watch Band',
                    'url': 'https://amazon.com/dp/B01234574',
                    'price': '$9.00',
                    'rating': 4.3,
                    'review_count': 1259,
                    'score': 5414
                },
                {
                    'title': 'RuenTech Bands Compatible with Veryfitpro Smart Watch',
                    'url': 'https://amazon.com/dp/B01234575',
                    'price': '$14.00',
                    'rating': 4.2,
                    'review_count': 913,
                    'score': 3835
                },
                {
                    'title': 'Sport Bands for Apple Watch SE Series 6 5 4',
                    'url': 'https://amazon.com/dp/B01234576',
                    'price': '$12.00',
                    'rating': 4.1,
                    'review_count': 845,
                    'score': 3465
                }
            ],
            'home': [
                {
                    'title': 'Power Strip with USB Ports, SUPERDANNY 12 Outlets',
                    'url': 'https://amazon.com/dp/B01234577',
                    'price': '$15.00',
                    'rating': 4.7,
                    'review_count': 3456,
                    'score': 16243
                },
                {
                    'title': 'Power Strip Tower with 8 AC Outlets',
                    'url': 'https://amazon.com/dp/B01234578',
                    'price': '$22.00',
                    'rating': 4.5,
                    'review_count': 2789,
                    'score': 12551
                },
                {
                    'title': 'Surge Protector Power Strip with USB C',
                    'url': 'https://amazon.com/dp/B01234579',
                    'price': '$18.00',
                    'rating': 4.4,
                    'review_count': 2156,
                    'score': 9486
                },
                {
                    'title': 'Smart Power Strip with Voice Control',
                    'url': 'https://amazon.com/dp/B01234580',
                    'price': '$35.00',
                    'rating': 4.3,
                    'review_count': 1876,
                    'score': 8067
                },
                {
                    'title': 'Outdoor Power Strip Weatherproof with Timer',
                    'url': 'https://amazon.com/dp/B01234581',
                    'price': '$28.00',
                    'rating': 4.2,
                    'review_count': 1634,
                    'score': 6863
                }
            ],
            'marine_speakers': [
                {
                    'title': 'Pyle Dual Waterproof Marine Speakers - 6.5" 200W',
                    'url': 'https://amazon.com/dp/B001RNNX8K',
                    'price': '$49.99',
                    'rating': 4.5,
                    'review_count': 2847,
                    'score': 12811
                },
                {
                    'title': 'BOSS Audio Systems MCK632WB.64 Marine Speaker Package',
                    'url': 'https://amazon.com/dp/B07QT3QXFN',
                    'price': '$139.99',
                    'rating': 4.4,
                    'review_count': 1823,
                    'score': 8021
                },
                {
                    'title': 'Kenwood KFC-1633MRW 6.5" Marine Speakers (Pair)',
                    'url': 'https://amazon.com/dp/B07V6M8BNT',
                    'price': '$79.95',
                    'rating': 4.3,
                    'review_count': 1456,
                    'score': 6261
                },
                {
                    'title': 'Rockford Fosgate M0-65B Marine Certified 6.5" Speakers',
                    'url': 'https://amazon.com/dp/B07MCNBNK9',
                    'price': '$149.99',
                    'rating': 4.6,
                    'review_count': 982,
                    'score': 4517
                },
                {
                    'title': 'JBL MS6520 180W, 6.5" Coaxial Marine Speakers',
                    'url': 'https://amazon.com/dp/B00AM4OZH6',
                    'price': '$89.95',
                    'rating': 4.2,
                    'review_count': 756,
                    'score': 3175
                }
            ],
            'default': [
                {
                    'title': 'Universal Product #1 - High Quality Item',
                    'url': 'https://amazon.com/dp/B01234582',
                    'price': '$25.00',
                    'rating': 4.6,
                    'review_count': 1500,
                    'score': 6900
                },
                {
                    'title': 'Universal Product #2 - Premium Choice',
                    'url': 'https://amazon.com/dp/B01234583',
                    'price': '$35.00',
                    'rating': 4.4,
                    'review_count': 1200,
                    'score': 5280
                },
                {
                    'title': 'Universal Product #3 - Best Value',
                    'url': 'https://amazon.com/dp/B01234584',
                    'price': '$20.00',
                    'rating': 4.2,
                    'review_count': 1000,
                    'score': 4200
                },
                {
                    'title': 'Universal Product #4 - Popular Pick',
                    'url': 'https://amazon.com/dp/B01234585',
                    'price': '$30.00',
                    'rating': 4.0,
                    'review_count': 800,
                    'score': 3200
                },
                {
                    'title': 'Universal Product #5 - Budget Option',
                    'url': 'https://amazon.com/dp/B01234586',
                    'price': '$15.00',
                    'rating': 3.8,
                    'review_count': 600,
                    'score': 2280
                }
            ]
        }
        
        logger.info("✅ TEST MODE: Amazon Category Scraper initialized with hardcoded data")

    def detect_category_from_title(self, title: str) -> str:
        """Detect category from title for hardcoded data selection"""
        title_lower = title.lower()
        
        # Category keywords mapping
        if any(word in title_lower for word in ['camera', 'photo', 'digital', 'security']):
            return 'electronics'
        elif any(word in title_lower for word in ['watch', 'band', 'strap', 'wrist', 'smart']):
            return 'fashion'  
        elif any(word in title_lower for word in ['power', 'strip', 'outlet', 'surge', 'home']):
            return 'home'
        elif any(word in title_lower for word in ['marine', 'speaker', 'boat', 'waterproof', 'nautical']):
            return 'marine_speakers'
        else:
            return 'default'

    async def search_category_products(self, category_title: str, max_products: int = 20) -> List[Dict]:
        """TEST MODE: Return hardcoded products based on category detection"""
        try:
            # Detect category from title
            category = self.detect_category_from_title(category_title)
            logger.info(f"🔍 TEST MODE: Using hardcoded products for category: {category}")
            
            # Get hardcoded products for this category
            products = self.hardcoded_products.get(category, self.hardcoded_products['default']).copy()
            
            # Convert to expected format
            formatted_products = []
            for product in products[:5]:  # Top 5 only
                formatted_product = {
                    'asin': product['url'].split('/')[-1],  # Extract ASIN from URL
                    'title': product['title'],
                    'price': product['price'],
                    'rating': product['rating'],
                    'review_count': product['review_count'],
                    'review_score': product['score'],
                    'image_url': '',  # Will be handled by photo managers
                    'affiliate_link': f"{product['url']}?tag={self.affiliate_tag}"
                }
                formatted_products.append(formatted_product)
            
            logger.info(f"✅ Successfully scraped {len(formatted_products)} products")
            
            # Log product details
            for i, product in enumerate(formatted_products, 1):
                price_str = product['price'].replace('$', '')
                logger.info(f"✅ Price for product {i}: ${price_str}")
            
            logger.info(f"✅ Selected top 5 products based on review score")
            for i, product in enumerate(formatted_products, 1):
                logger.info(f"  {i}. {product['title'][:50]}... (Score: {product['review_score']})")
            
            return formatted_products
            
        except Exception as e:
            logger.error(f"Error in hardcoded product generation: {e}")
            return []

    async def get_top_5_products(self, category_title: str) -> Dict:
        """Get top 5 products for a category based on hardcoded data"""
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
                
                airtable_data[f'ProductNo{i}Rating'] = str(product['rating'])
                airtable_data[f'ProductNo{i}Reviews'] = str(product['review_count'])
                airtable_data[f'ProductNo{i}Score'] = str(product['review_score'])
                
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