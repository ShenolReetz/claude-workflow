#!/usr/bin/env python3
"""
Amazon Fallback - Alternative sources for affiliate links
"""
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

# Predefined affiliate links for common product categories
FALLBACK_PRODUCTS = {
    'security camera': [
        {'name': 'Wyze Cam v3', 'asin': 'B08R59YH7W'},
        {'name': 'Blink Mini', 'asin': 'B07X6C9RMF'},
        {'name': 'Ring Indoor Cam', 'asin': 'B07Q9VBYV8'}
    ],
    'monitor cover': [
        {'name': 'Computer Monitor Dust Cover', 'asin': 'B07SC7T2L9'},
        {'name': 'kwmobile Monitor Cover', 'asin': 'B01N6S5Z9Z'}
    ],
    'kvm switch': [
        {'name': 'UGREEN USB Switch', 'asin': 'B01MXXQKGM'},
        {'name': 'Cable Matters KVM Switch', 'asin': 'B0746P6LPP'}
    ],
    'camera lens': [
        {'name': 'Canon EF 50mm f/1.8', 'asin': 'B00X8MRBCW'},
        {'name': 'Sony FE 85mm f/1.8', 'asin': 'B06WLGFWGX'}
    ]
}

def get_fallback_affiliate_link(product_name: str, affiliate_tag: str) -> Dict:
    """Get a fallback affiliate link based on product category"""
    product_lower = product_name.lower()
    
    for category, products in FALLBACK_PRODUCTS.items():
        if category in product_lower:
            # Return first matching product
            product = products[0]
            return {
                'success': True,
                'affiliate_link': f"https://www.amazon.com/dp/{product['asin']}?tag={affiliate_tag}",
                'asin': product['asin'],
                'title': product['name'],
                'is_fallback': True
            }
    
    # Generic fallback
    return {
        'success': True,
        'affiliate_link': f"https://www.amazon.com/s?k={product_name.replace(' ', '+')}&tag={affiliate_tag}",
        'title': product_name,
        'is_fallback': True,
        'is_search': True
    }
    ],
    'vacuum': [
        {'name': 'XPOWER A-2 Airrow Pro', 'asin': 'B00SI67YRU'},
        {'name': 'Metro Vacuum ED500', 'asin': 'B001J4ZOAW'},
        {'name': 'OPOLAR Cordless Air Duster', 'asin': 'B08HLVKB9V'}
    ],
    'computer vacuum': [
        {'name': 'XPOWER A-2 Airrow Pro', 'asin': 'B00SI67YRU'},
        {'name': 'Metro Vacuum DataVac', 'asin': 'B00006IAOR'}
    ]
}

def get_fallback_affiliate_link(product_name: str, affiliate_tag: str) -> Dict:
    """Get a fallback affiliate link based on product category"""
    product_lower = product_name.lower()
    
    # Check multiple keywords
    for category, products in FALLBACK_PRODUCTS.items():
        if any(word in product_lower for word in category.split()):
            # Return random product from category
            import random
            product = random.choice(products)
            return {
                'success': True,
                'affiliate_link': f"https://www.amazon.com/dp/{product['asin']}?tag={affiliate_tag}",
                'asin': product['asin'],
                'title': product['name'],
                'is_fallback': True
            }
    
    # Generic fallback
    return {
        'success': True,
        'affiliate_link': f"https://www.amazon.com/s?k={product_name.replace(' ', '+')}&tag={affiliate_tag}",
        'title': product_name,
        'is_fallback': True,
        'is_search': True
    }
    ],
    'satellite': [
        {'name': 'DISH Wally HD Receiver', 'asin': 'B01MSBQB1P'},
        {'name': 'Winegard SK-SWM3 DIRECTV', 'asin': 'B00WGR8PA4'},
        {'name': 'KING VQ4500 Tailgater', 'asin': 'B00B40XO8K'}
    ],
    'satellite tv': [
        {'name': 'DIRECTV H25 HD Receiver', 'asin': 'B00WGR8PA4'},
        {'name': 'ViewTV AT-263 ATSC', 'asin': 'B00GGVPKKC'}
    ]
}
