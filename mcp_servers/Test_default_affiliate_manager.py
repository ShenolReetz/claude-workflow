#!/usr/bin/env python3
"""
Test Default Affiliate Manager
Manages pre-generated affiliate links for test workflow to avoid Amazon scraping and API costs
All affiliate links include pricing data, ratings, and product information
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestDefaultAffiliateManager:
    """Manages default affiliate links for test workflow efficiency"""
    
    def __init__(self):
        self.config_path = '/home/claude-workflow/config/test_default_affiliate_links.json'
        self.default_affiliates = self._load_default_affiliates()
        
    def _load_default_affiliates(self) -> Dict[str, Any]:
        """Load default affiliate links configuration"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            logger.info("✅ Loaded default affiliate links configuration")
            return config
        except FileNotFoundError:
            logger.error(f"❌ Default affiliate config not found: {self.config_path}")
            return self._create_fallback_config()
        except Exception as e:
            logger.error(f"❌ Error loading default affiliates: {e}")
            return self._create_fallback_config()
    
    def _create_fallback_config(self) -> Dict[str, Any]:
        """Create minimal fallback configuration"""
        return {
            "test_mode_enabled": True,
            "default_affiliate_links": {
                f"product_{i}": {
                    "affiliate_link": f"https://amzn.to/TEST_fallback_{i}",
                    "price": f"${20 + i * 5}.99",
                    "rating": "4.5",
                    "reviews": f"{5000 + i * 1000}",
                    "title": f"Fallback Product {i}",
                    "description": f"Fallback product description {i}"
                } for i in range(1, 6)
            }
        }
    
    def get_affiliate_link(self, product_number: int, category: str = None) -> Dict[str, str]:
        """Get default affiliate link with product data"""
        try:
            # Try category-specific affiliate link first
            if category and category in self.default_affiliates.get('category_specific_links', {}):
                category_links = self.default_affiliates['category_specific_links'][category]
                product_key = f"product_{product_number}"
                if product_key in category_links:
                    category_affiliate = category_links[product_key]
                    logger.info(f"🔗 Using category-specific affiliate for {category}: product {product_number}")
                    return {
                        'affiliate_link': category_affiliate['affiliate_link'],
                        'price': category_affiliate['price'],
                        'rating': category_affiliate['rating'],
                        'reviews': category_affiliate['reviews'],
                        'title': category_affiliate['title'],
                        'description': category_affiliate['description']
                    }
            
            # Default affiliate link
            product_key = f"product_{product_number}"
            affiliate_data = self.default_affiliates['default_affiliate_links'].get(product_key)
            
            if affiliate_data:
                logger.info(f"🔗 Using default affiliate link for product {product_number}")
                return {
                    'affiliate_link': affiliate_data['affiliate_link'],
                    'price': affiliate_data['price'],
                    'rating': affiliate_data['rating'],
                    'reviews': affiliate_data['reviews'],
                    'title': affiliate_data['title'],
                    'description': affiliate_data['description']
                }
            else:
                # Fallback
                logger.warning(f"⚠️ No default affiliate for product {product_number}, using fallback")
                fallback = self.default_affiliates['fallback_links']['generic_product']
                return {
                    'affiliate_link': fallback['affiliate_link'],
                    'price': fallback['price'],
                    'rating': fallback['rating'],
                    'reviews': fallback['reviews'],
                    'title': fallback['title'],
                    'description': fallback['description']
                }
                
        except Exception as e:
            logger.error(f"❌ Error getting affiliate link for product {product_number}: {e}")
            return {
                'affiliate_link': f"https://amzn.to/TEST_error_{product_number}",
                'price': "$25.99",
                'rating': "4.5",
                'reviews': "5,000",
                'title': f"Error Product {product_number}",
                'description': f"Error product description {product_number}"
            }
    
    def populate_airtable_with_default_affiliates(self, record_data: Dict[str, Any], category: str = None) -> Dict[str, str]:
        """Populate Airtable record with default affiliate links and product data"""
        try:
            updates = {}
            
            # Get affiliate links for all 5 products
            for i in range(1, 6):
                affiliate_data = self.get_affiliate_link(i, category)
                
                # Update Airtable fields with affiliate data
                updates[f'ProductNo{i}AffiliateLink'] = affiliate_data['affiliate_link']
                
                # Convert price to number format (remove $ and convert to float)
                price_str = affiliate_data['price'].replace('$', '').replace(',', '')
                try:
                    updates[f'ProductNo{i}Price'] = float(price_str)
                except ValueError:
                    updates[f'ProductNo{i}Price'] = 25.99  # fallback price
                
                # Convert rating to number format  
                try:
                    updates[f'ProductNo{i}Rating'] = float(affiliate_data['rating'])
                except ValueError:
                    updates[f'ProductNo{i}Rating'] = 4.5  # fallback rating
                
                # Convert reviews to number format (remove commas)
                reviews_str = affiliate_data['reviews'].replace(',', '')
                try:
                    updates[f'ProductNo{i}Reviews'] = int(reviews_str)
                except ValueError:
                    updates[f'ProductNo{i}Reviews'] = 5000  # fallback reviews
                
                # Also update title and description if not already set
                if f'ProductNo{i}Title' not in record_data or not record_data[f'ProductNo{i}Title']:
                    updates[f'ProductNo{i}Title'] = affiliate_data['title']
                if f'ProductNo{i}Description' not in record_data or not record_data[f'ProductNo{i}Description']:
                    updates[f'ProductNo{i}Description'] = affiliate_data['description']
            
            logger.info(f"✅ TEST MODE: Using default affiliate links (no scraping needed)")
            logger.info(f"📊 Updated {len(updates)} affiliate fields with default data")
            logger.info(f"💰 All products have pricing, ratings, and affiliate links")
            
            return updates
            
        except Exception as e:
            logger.error(f"❌ Error populating default affiliates: {e}")
            return {}
    
    def get_test_mode_status(self) -> Dict[str, Any]:
        """Get test mode affiliate configuration status"""
        return {
            'test_mode_enabled': self.default_affiliates.get('test_mode_enabled', False),
            'config_loaded': bool(self.default_affiliates),
            'total_affiliate_links': 5,  # 5 products
            'available_categories': list(self.default_affiliates.get('category_specific_links', {}).keys()),
            'cost_savings': 'Eliminates ScrapingDog and Amazon API calls',
            'timestamp': datetime.now().isoformat()
        }
    
    def get_affiliate_summary(self) -> Dict[str, Any]:
        """Get summary of all affiliate links"""
        try:
            links = self.default_affiliates.get('default_affiliate_links', {})
            return {
                'products': [
                    {
                        'product_number': i,
                        'title': links.get(f'product_{i}', {}).get('title', f'Product {i}'),
                        'price': links.get(f'product_{i}', {}).get('price', '$0.00'),
                        'rating': links.get(f'product_{i}', {}).get('rating', '0.0'),
                        'reviews': links.get(f'product_{i}', {}).get('reviews', '0'),
                        'affiliate_link': links.get(f'product_{i}', {}).get('affiliate_link', 'None')[:50] + '...'
                    }
                    for i in range(1, 6)
                ],
                'total_products': 5,
                'categories_available': len(self.default_affiliates.get('category_specific_links', {}))
            }
        except Exception as e:
            logger.error(f"Error getting affiliate summary: {e}")
            return {
                'products': [{'product_number': i, 'title': f'Product {i}', 'price': '$25.99', 'rating': '4.5', 'reviews': '5000', 'affiliate_link': 'Error'} for i in range(1, 6)],
                'total_products': 5,
                'categories_available': 0
            }

# Test function
if __name__ == "__main__":
    def test_default_affiliate_manager():
        manager = TestDefaultAffiliateManager()
        
        print("🧪 Testing Default Affiliate Manager")
        print("=" * 50)
        
        # Test status
        status = manager.get_test_mode_status()
        print(f"📊 Test Mode Status: {status}")
        
        # Test affiliate summary
        summary = manager.get_affiliate_summary()
        print(f"\n📝 Affiliate Summary:")
        for product in summary['products']:
            print(f"   Product {product['product_number']}: {product['title']} - {product['price']} ({product['rating']}⭐, {product['reviews']} reviews)")
            print(f"      Link: {product['affiliate_link']}")
        
        # Test category-specific affiliates
        test_categories = ['electronics', 'home_kitchen', 'automotive']
        for category in test_categories:
            affiliate = manager.get_affiliate_link(1, category)
            print(f"\n🎯 Category '{category}' Product 1:")
            print(f"   Title: {affiliate['title']}")
            print(f"   Price: {affiliate['price']} | Rating: {affiliate['rating']}⭐ | Reviews: {affiliate['reviews']}")
            print(f"   Link: {affiliate['affiliate_link']}")
        
        # Test Airtable population
        test_record = {'Title': 'Test Power Strip Products'}
        updates = manager.populate_airtable_with_default_affiliates(test_record, 'electronics')
        print(f"\n📋 Airtable Updates: {len(updates)} fields")
        affiliate_fields = [field for field in updates.keys() if 'AffiliateLink' in field]
        price_fields = [field for field in updates.keys() if 'Price' in field]
        print(f"   Affiliate Links: {len(affiliate_fields)}")
        print(f"   Price Fields: {len(price_fields)}")
        for field in affiliate_fields[:3]:  # Show first 3
            print(f"   {field}: {updates[field]}")
    
    test_default_affiliate_manager()