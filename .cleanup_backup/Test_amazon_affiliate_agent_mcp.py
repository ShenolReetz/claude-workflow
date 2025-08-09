#!/usr/bin/env python3
"""
Test Amazon Affiliate Agent - Hardcoded responses for testing
Purpose: Test affiliate generation without consuming API tokens
"""

from typing import Dict, Any, List

async def test_run_amazon_affiliate_generation(title_record: Dict[str, Any], config: Dict[str, str], category_info: Dict[str, Any] = None) -> Dict[str, Any]:
    """Generate hardcoded Amazon affiliate content for testing"""
    print("🛍️ Running test Amazon affiliate generation (no API calls)")
    
    # Hardcoded test products with affiliate links
    test_products = [
        {
            'title': 'VSGO Camera Cleaning Kit Professional DSLR Sensor Cleaning Swabs',
            'description': 'Professional camera cleaning kit with sensor swabs, cleaning solution, and anti-static brush. Perfect for DSLR and mirrorless cameras.',
            'price': '$24.99',
            'rating': '4.6',
            'reviews': '2,847',
            'image_url': 'https://images.unsplash.com/photo-1606983340126-99ab4feaa64a?w=500&h=500',
            'affiliate_link': 'https://amazon.com/test-affiliate-link-1?tag=testaffiliate-20',
            'features': [
                'Professional sensor cleaning swabs',
                'Anti-static cleaning solution',
                'Safe for all camera sensors',
                'Includes precision brushes'
            ]
        },
        {
            'title': 'LensPen Camera Lens Cleaning Pen with Retractable Brush',
            'description': 'Compact lens cleaning pen with retractable brush and cleaning tip. Essential tool for photographers on the go.',
            'price': '$12.95',
            'rating': '4.7',
            'reviews': '5,234',
            'image_url': 'https://images.unsplash.com/photo-1508423134147-addf71308178?w=500&h=500',
            'affiliate_link': 'https://amazon.com/test-affiliate-link-2?tag=testaffiliate-20',
            'features': [
                'Retractable cleaning brush',
                'Carbon cleaning tip',
                'Compact portable design',
                'Works on all lens types'
            ]
        },
        {
            'title': 'Altura Photo Camera Cleaning Kit with Microfiber Cloths',
            'description': 'Complete camera cleaning solution with multiple brush sizes, microfiber cloths, and cleaning solution.',
            'price': '$19.99',
            'rating': '4.5',
            'reviews': '1,923',
            'image_url': 'https://images.unsplash.com/photo-1520637836862-4d197d17c79a?w=500&h=500',
            'affiliate_link': 'https://amazon.com/test-affiliate-link-3?tag=testaffiliate-20',
            'features': [
                'Multiple brush sizes',
                'Premium microfiber cloths',
                'Alcohol-free cleaning solution',
                'Protective storage case'
            ]
        },
        {
            'title': 'Rocket Blower Anti-Static Dust Removal Tool',
            'description': 'Professional dust blower with anti-static design. Safe and effective for removing dust from camera sensors and lenses.',
            'price': '$16.99',
            'rating': '4.8',
            'reviews': '3,567',
            'image_url': 'https://images.unsplash.com/photo-1615529328331-f8917597711f?w=500&h=500',
            'affiliate_link': 'https://amazon.com/test-affiliate-link-4?tag=testaffiliate-20',
            'features': [
                'Anti-static design',
                'Safe for all sensors',
                'Powerful air blast',
                'Ergonomic grip'
            ]
        },
        {
            'title': 'Zeiss Lens Cleaning Wipes and Microfiber Cloth Set',
            'description': 'Premium Zeiss lens cleaning wipes with microfiber cloth. Safely removes fingerprints, dust, and smudges.',
            'price': '$14.95',
            'rating': '4.9',
            'reviews': '4,128',
            'image_url': 'https://images.unsplash.com/photo-1606918801925-e2c914c4b2c3?w=500&h=500',
            'affiliate_link': 'https://amazon.com/test-affiliate-link-5?tag=testaffiliate-20',
            'features': [
                'Zeiss premium quality',
                'Individually wrapped wipes',
                'Ultra-soft microfiber cloth',
                'Safe for all lens coatings'
            ]
        }
    ]
    
    # Update the record with hardcoded product data
    updated_record = title_record.copy()
    
    for i, product in enumerate(test_products, 1):
        updated_record[f'ProductNo{i}Title'] = product['title']
        updated_record[f'ProductNo{i}Description'] = product['description']
        updated_record[f'ProductNo{i}Price'] = product['price']
        updated_record[f'ProductNo{i}Rating'] = product['rating']
        updated_record[f'ProductNo{i}Reviews'] = product['reviews']
        updated_record[f'ProductNo{i}Photo'] = product['image_url']
        updated_record[f'ProductNo{i}AffiliateLink'] = product['affiliate_link']
        
        print(f"   📦 Product {i}: {product['title'][:40]}...")
    
    return {
        'success': True,
        'updated_record': updated_record,
        'products': test_products,
        'products_found': len(test_products),
        'category': category_info.get('category', 'Test Category') if category_info else 'Test Category',
        'affiliate_links_generated': len(test_products),
        'api_calls_used': 0,
        'processing_time': '0.1s'
    }