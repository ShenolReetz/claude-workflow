#!/usr/bin/env python3
"""
Test Enhanced Amazon Scraper MCP Server - Hardcoded responses for testing
Purpose: Test enhanced Amazon scraping without consuming API tokens
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestEnhancedAmazonScraperMCPServer:
    """Test Enhanced Amazon Scraper MCP Server with hardcoded responses"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key  # Not used in test mode
        logger.info("🧪 Test Enhanced Amazon Scraper Server initialized")
    
    async def scrape_amazon_products_advanced(self, search_query: str) -> Dict[str, Any]:
        """Return hardcoded advanced product data for testing"""
        
        logger.info(f"🧪 Test: Advanced scraping for '{search_query}' (hardcoded data)")
        
        # Hardcoded advanced product data
        hardcoded_products = [
            {
                'title': 'Professional Camera Lens Cleaning Kit - Advanced Edition',
                'image_url': 'https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=1080&h=1920&fit=crop&crop=center',
                'rating': 4.9,
                'review_count': 3421,
                'price': '$39.99',
                'asin': 'B10ADVANCED1',
                'url': 'https://amazon.com/dp/B10ADVANCED1',
                'features': ['Anti-static', 'Microfiber cloth', '7-in-1 tools']
            },
            {
                'title': 'Ultra Precision Lens Pen - Pro Series',
                'image_url': 'https://images.unsplash.com/photo-1593784991095-a205069470b6?w=1080&h=1920&fit=crop&crop=center',
                'rating': 4.8,
                'review_count': 2156,
                'price': '$27.99',
                'asin': 'B11ADVANCED2',
                'url': 'https://amazon.com/dp/B11ADVANCED2',
                'features': ['Retractable brush', 'Cleaning compound', 'Protective cap']
            }
        ]
        
        logger.info(f"✅ Test: Returning {len(hardcoded_products)} advanced hardcoded products")
        
        return {
            'success': True,
            'products': hardcoded_products,
            'total_found': len(hardcoded_products),
            'search_query': search_query,
            'test_mode': True,
            'api_calls_used': 0,
            'advanced_features': True
        }