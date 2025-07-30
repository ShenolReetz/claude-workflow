#!/usr/bin/env python3
"""
Test Text Generation Control MCP Server
Hardcoded responses for testing - no API calls
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestTextGenerationControlMCPServer:
    """Test version - Quality control for text outputs with hardcoded responses"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # TTS timing constraints (same as production)
        self.words_per_second = 2.5  # Average TTS speed
        self.target_seconds_per_product = 9
        self.max_seconds_per_product = 10
        self.min_seconds_per_product = 8
        
        # Calculate word limits
        self.min_words_per_product = int(self.min_seconds_per_product * self.words_per_second)  # ~20 words
        self.max_words_per_product = int(self.max_seconds_per_product * self.words_per_second)  # ~25 words
        
        # Title constraints
        self.min_title_words = 4
        self.max_title_words = 8
        
        # Description constraints (total - title words)
        self.min_description_words = 12
        self.max_description_words = 18
        
        logger.info("🧪 TEST Text Generation Control Server initialized (hardcoded responses)")
    
    async def check_countdown_products(self, 
                                     products: List[Dict], 
                                     keywords: List[str],
                                     category: str) -> Dict[str, Any]:
        """
        TEST VERSION: Check if generated products meet all criteria (hardcoded success)
        """
        logger.info(f"🧪 TEST: Checking {len(products)} products for quality control (always passes)")
        
        # Hardcoded test validation results - all products pass
        validation_results = []
        products_needing_regeneration = []
        
        for i, product in enumerate(products):
            product_num = i + 1
            
            # Hardcoded validation for each product (always valid)
            validation = {
                'product_number': product_num,
                'is_valid': True,  # Always valid in test mode
                'title': product.get('title', f'Test Product {i+1}'),
                'description': product.get('description', f'Test description for product {i+1}'),
                'title_words': 6,  # Optimal word count
                'description_words': 15,  # Optimal word count
                'total_words': 21,  # Optimal total
                'estimated_seconds': 8.4,  # Perfect timing
                'keywords_found': 3,  # Good keyword usage
                'issues': [],  # No issues in test mode
                'regeneration_instructions': []  # No regeneration needed
            }
            
            validation_results.append(validation)
        
        # Calculate timing summary (hardcoded optimal values)
        timing_summary = {
            'total_products_duration': 42.0,  # 5 products × 8.4s each
            'average_product_duration': 8.4,
            'intro_duration': 5,
            'outro_duration': 5,
            'total_video_duration': 52.0,  # Perfect video length
            'valid_products': len(products),
            'invalid_products': 0,
            'timing_acceptable': True
        }
        
        logger.info("✅ TEST: All products passed validation (hardcoded success)")
        
        return {
            'all_valid': True,  # Always true in test mode
            'validation_results': validation_results,
            'products_needing_regeneration': products_needing_regeneration,
            'timing_summary': timing_summary,
            'requires_regeneration': False  # Never needs regeneration in test mode
        }
    
    async def check_intro_outro(self, intro: str, outro: str) -> Dict[str, Any]:
        """TEST VERSION: Check if intro and outro meet timing requirements (hardcoded success)"""
        
        logger.info("🧪 TEST: Validating intro/outro timing (hardcoded success)")
        
        # Hardcoded optimal results
        return {
            'intro': {
                'text': intro or "Test intro content for video",
                'words': 12,  # Perfect word count
                'estimated_seconds': 4.8,  # Perfect timing
                'is_valid': True,
                'issue': None
            },
            'outro': {
                'text': outro or "Test outro content for video",
                'words': 13,  # Perfect word count
                'estimated_seconds': 5.2,  # Perfect timing
                'is_valid': True,
                'issue': None
            },
            'both_valid': True
        }
    
    async def validate_text_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """TEST VERSION: Validate any text content (hardcoded success)"""
        
        logger.info("🧪 TEST: Validating text content (hardcoded success)")
        
        return {
            'success': True,
            'all_valid': True,
            'validation_passed': True,
            'timing_acceptable': True,
            'keyword_usage_good': True,
            'content_quality_high': True,
            'recommendations': [],
            'issues_found': 0,
            'total_estimated_duration': 52.0
        }
    
    async def regenerate_failed_content(self, failed_items: List[Dict]) -> Dict[str, Any]:
        """TEST VERSION: Regenerate failed content (not needed in test mode)"""
        
        logger.info("🧪 TEST: Content regeneration not needed (all content passes)")
        
        return {
            'success': True,
            'regenerated_count': 0,
            'all_content_valid': True,
            'message': 'No regeneration needed in test mode - all content is optimal'
        }


# Test function
async def test_server():
    """Test the text generation control server"""
    
    config = {'test_mode': True}
    server = TestTextGenerationControlMCPServer(config)
    
    # Test products (will all pass in test mode)
    test_products = [
        {
            'title': 'ASUS ROG Strix G15 Gaming Laptop',
            'description': 'Powerful gaming laptop featuring RTX 4070 graphics and AMD Ryzen processor for ultimate gaming performance and productivity.'
        },
        {
            'title': 'Razer DeathAdder V3 Gaming Mouse',
            'description': 'Ergonomic gaming mouse with precise sensor technology and customizable RGB lighting for competitive gaming excellence.'
        },
        {
            'title': 'SteelSeries Arctis 7 Wireless Headset',
            'description': 'Premium wireless gaming headset with DTS Headphone audio and ClearCast microphone for immersive gaming experience.'
        },
        {
            'title': 'Corsair K95 RGB Platinum Keyboard',
            'description': 'Mechanical gaming keyboard with Cherry MX switches and per-key RGB backlighting for professional gaming setups.'
        },
        {
            'title': 'NVIDIA GeForce RTX 4080 Graphics Card',
            'description': 'High-performance graphics card with ray tracing technology and DLSS support for ultra-high resolution gaming.'
        }
    ]
    
    keywords = ['gaming', 'performance', 'RGB', 'wireless', 'professional']
    category = 'Gaming Electronics'
    
    result = await server.check_countdown_products(test_products, keywords, category)
    
    print(f"\n✅ Valid products: {result['timing_summary']['valid_products']}")
    print(f"❌ Invalid products: {result['timing_summary']['invalid_products']}")
    print(f"🎯 Total video duration: {result['timing_summary']['total_video_duration']}s")
    print(f"📊 All valid: {result['all_valid']}")
    
    # Test intro/outro
    intro_outro_result = await server.check_intro_outro(
        "Welcome to our top gaming products review for 2025",
        "Subscribe for more amazing tech reviews and gaming content"
    )
    
    print(f"\n🎬 Intro valid: {intro_outro_result['intro']['is_valid']}")
    print(f"🎬 Outro valid: {intro_outro_result['outro']['is_valid']}")
    print(f"✅ Both valid: {intro_outro_result['both_valid']}")

if __name__ == "__main__":
    asyncio.run(test_server())