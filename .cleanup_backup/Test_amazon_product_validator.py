#!/usr/bin/env python3
"""
Test Amazon Product Validator - Hardcoded responses for testing
Purpose: Test product validation without consuming API tokens
"""

from typing import Dict, Any

class TestAmazonProductValidator:
    """Test Amazon Product Validator with hardcoded responses"""
    
    def __init__(self, scrapingdog_api_key: str):
        self.scrapingdog_api_key = scrapingdog_api_key  # Not used in test mode
        
        print("🧪 Test Amazon Product Validator initialized")
    
    async def validate_amazon_products(self, title: str, min_products: int = 5) -> Dict[str, Any]:
        """Return hardcoded validation result for testing"""
        print(f"✅ Test validation for: {title[:50]}... (no API call)")
        print(f"📦 Checking for minimum {min_products} products")
        
        # Always return successful validation with hardcoded data
        return {
            'valid': True,
            'product_count': 15,  # Hardcoded product count
            'reason': 'Test validation passed',
            'categories': ['Camera & Photo', 'Electronics', 'Accessories'],
            'price_range': '$9.99 - $89.99',
            'avg_rating': 4.5,
            'total_reviews': 12847,
            'search_query': title,
            'validation_time': '0.1s',  # Instant in test mode
            'api_calls_used': 0  # No real API calls
        }
    
    async def get_product_details(self, product_url: str) -> Dict[str, Any]:
        """Return hardcoded product details"""
        print(f"🔍 Getting test product details (no API call)")
        
        return {
            'success': True,
            'title': 'Test Camera Cleaning Brush Professional Kit',
            'price': '$24.99',
            'rating': 4.7,
            'reviews': 2341,
            'image_url': 'https://images.unsplash.com/photo-1606983340126-99ab4feaa64a?w=500&h=500',
            'description': 'Professional camera cleaning kit with anti-static brushes',
            'features': [
                'Anti-static brush design',
                'Safe for all camera types',
                'Professional grade quality',
                'Includes microfiber cloths'
            ]
        }
    
    async def search_products(self, query: str, max_results: int = 20) -> Dict[str, Any]:
        """Return hardcoded search results"""
        print(f"🔍 Test search for: {query[:30]}... (no API call)")
        
        # Hardcoded test products
        test_products = []
        for i in range(min(max_results, 15)):
            test_products.append({
                'title': f'Camera Cleaning Brush Pro {i+1}',
                'price': f'${19.99 + i * 5}',
                'rating': round(4.0 + (i * 0.1), 1),
                'reviews': 1000 + i * 200,
                'image_url': f'https://images.unsplash.com/photo-1606983340126-99ab4feaa64a?w=500&h=500&crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w0NTYwMDhfMHwxfHNlYXJjaHwxfHxjYW1lcmElMjBjbGVhbmluZyUyMGJydXNofGVufDB8fHx8MTY5ODc2MDAwMHww&ixlib=rb-4.0.3&q=80',
                'url': f'https://amazon.com/test-product-{i+1}',
                'availability': 'In Stock',
                'prime': True,
                'category': 'Camera & Photo'
            })
        
        return {
            'success': True,
            'products': test_products,
            'total_found': len(test_products),
            'search_query': query,
            'api_calls_used': 0
        }
    
    async def close(self):
        """Close test validator (no cleanup needed)"""
        print("🧪 Test Amazon Product Validator closed")
        pass