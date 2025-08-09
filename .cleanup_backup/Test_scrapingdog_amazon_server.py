#!/usr/bin/env python3
"""
Test ScrapingDog Amazon MCP Server - Hardcoded responses for testing
Purpose: Test Amazon scraping without consuming API tokens
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestScrapingDogAmazonMCPServer:
    """Test ScrapingDog Amazon MCP Server with hardcoded responses"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key  # Not used in test mode
        logger.info("🧪 Test ScrapingDog Amazon Server initialized")
    
    async def scrape_products_with_reviews(self, search_query: str, max_products: int = 20) -> Dict[str, Any]:
        """Return hardcoded product data for testing"""
        
        logger.info(f"🧪 Test: Scraping products for '{search_query}' (hardcoded data)")
        
        # Hardcoded product data based on camera cleaning brushes
        hardcoded_products = [
            {
                'title': 'ZEISS Lens Cleaning Kit - Professional Camera Lens Cleaner',
                'image_url': 'https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=1080&h=1920&fit=crop&crop=center',
                'rating': 4.8,
                'review_count': 2847,
                'price': '$29.99',
                'asin': 'B08HJKL901',
                'url': 'https://amazon.com/dp/B08HJKL901'
            },
            {
                'title': 'Camera Cleaning Kit - Professional Grade 7-in-1',
                'image_url': 'https://images.unsplash.com/photo-1593784991095-a205069470b6?w=1080&h=1920&fit=crop&crop=center',
                'rating': 4.7,
                'review_count': 1923,
                'price': '$24.99',
                'asin': 'B09MNOP234',
                'url': 'https://amazon.com/dp/B09MNOP234'
            },
            {
                'title': 'Lens Pen Pro - Precision Camera Lens Cleaner',
                'image_url': 'https://images.unsplash.com/photo-1585792180666-f7347c490ee2?w=1080&h=1920&fit=crop&crop=center',
                'rating': 4.6,
                'review_count': 1456,
                'price': '$19.99',
                'asin': 'B07QRST567',
                'url': 'https://amazon.com/dp/B07QRST567'
            },
            {
                'title': 'Altura Photo Cleaning Kit - Complete Camera Care',
                'image_url': 'https://images.unsplash.com/photo-1583394838336-acd977736f90?w=1080&h=1920&fit=crop&crop=center',
                'rating': 4.5,
                'review_count': 987,
                'price': '$16.99',
                'asin': 'B06UVWX890',
                'url': 'https://amazon.com/dp/B06UVWX890'
            },
            {
                'title': 'K&F Concept Camera Cleaning Brush Set',
                'image_url': 'https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=1080&h=1920&fit=crop&crop=center',
                'rating': 4.4,
                'review_count': 654,
                'price': '$12.99',
                'asin': 'B05YZ123AB',
                'url': 'https://amazon.com/dp/B05YZ123AB'
            }
        ]
        
        logger.info(f"✅ Test: Returning {len(hardcoded_products)} hardcoded products")
        
        return {
            'success': True,
            'products': hardcoded_products,
            'total_found': len(hardcoded_products),
            'search_query': search_query,
            'test_mode': True,
            'api_calls_used': 0
        }