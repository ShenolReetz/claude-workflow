#!/usr/bin/env python3
"""
Production Amazon Product Validator - Real Product Validation
"""

from typing import Dict, List, Optional

class ProductionAmazonProductValidator:
    def __init__(self, scrapingdog_api_key: str):
        self.api_key = scrapingdog_api_key
        
    async def validate_amazon_products(self, products: List[Dict], min_products: int = 5) -> Dict:
        """Validate Amazon products meet quality criteria"""
        try:
            if not products:
                return {
                    'valid': False,
                    'reason': 'No products provided',
                    'product_count': 0
                }
            
            if len(products) < min_products:
                return {
                    'valid': False,
                    'reason': f'Insufficient products: {len(products)} < {min_products}',
                    'product_count': len(products)
                }
            
            # Validate each product
            valid_products = []
            for product in products:
                if self._validate_single_product(product):
                    valid_products.append(product)
            
            if len(valid_products) < min_products:
                return {
                    'valid': False,
                    'reason': f'Only {len(valid_products)} valid products out of {len(products)}',
                    'product_count': len(valid_products)
                }
            
            return {
                'valid': True,
                'product_count': len(valid_products),
                'products': valid_products[:min_products]
            }
            
        except Exception as e:
            print(f"❌ Error validating products: {e}")
            return {
                'valid': False,
                'reason': f'Validation error: {str(e)}',
                'product_count': 0
            }
    
    def _validate_single_product(self, product: Dict) -> bool:
        """Validate a single product meets criteria"""
        # Check required fields
        if not product.get('name'):
            return False
        
        # Check rating (minimum 3.5)
        rating = product.get('rating', '0')
        try:
            rating_float = float(rating)
            if rating_float < 3.5:
                return False
        except (ValueError, TypeError):
            return False
        
        # Check reviews (minimum 10)
        reviews = product.get('reviews', '0')
        try:
            # Handle review formats like "3,563" or "381"
            reviews_clean = str(reviews).replace(',', '').replace('+', '')
            reviews_int = int(reviews_clean)
            if reviews_int < 10:
                return False
        except (ValueError, TypeError):
            return False
        
        # Check price (must be positive)
        price = product.get('price', '$0')
        try:
            # Handle price formats like "$117.99"
            price_clean = str(price).replace('$', '').replace(',', '')
            price_float = float(price_clean)
            if price_float <= 0:
                return False
        except (ValueError, TypeError):
            return False
        
        # Check ASIN exists
        if not product.get('asin'):
            return False
        
        return True