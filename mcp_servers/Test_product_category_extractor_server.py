# mcp_servers/Test_product_category_extractor_server.py
import json
import logging
import asyncio
import re
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductCategoryExtractorMCPServer:
    """TEST MODE: MCP Server with hardcoded product category extraction"""
    
    def __init__(self, anthropic_api_key: str):
        self.anthropic_api_key = anthropic_api_key
        # TEST MODE: No actual API client needed
        
        # Hardcoded category mappings
        self.category_patterns = {
            # Audio/Electronics
            'speaker': {'category': 'speakers', 'type': 'electronics', 'terms': ['speakers', 'bluetooth speakers', 'wireless speakers']},
            'cable': {'category': 'audio cables', 'type': 'electronics', 'terms': ['audio cables', 'speaker cables', 'rca cables']},
            'headphone': {'category': 'headphones', 'type': 'electronics', 'terms': ['headphones', 'wireless headphones', 'bluetooth headphones']},
            'headset': {'category': 'gaming headsets', 'type': 'electronics', 'terms': ['gaming headsets', 'headsets', 'gaming headphones']},
            'amplifier': {'category': 'car amplifiers', 'type': 'automotive', 'terms': ['car amplifiers', 'automotive amplifiers', 'car audio amps']},
            'amp': {'category': 'car amplifiers', 'type': 'automotive', 'terms': ['car amplifiers', 'automotive amplifiers', 'car audio amps']},
            'subwoofer': {'category': 'car subwoofers', 'type': 'automotive', 'terms': ['car subwoofers', 'automotive subwoofers', 'car audio subs']},
            'marine': {'category': 'marine speakers', 'type': 'automotive', 'terms': ['marine speakers', 'boat speakers', 'waterproof speakers']},
            
            # Cameras/Security
            'camera': {'category': 'security cameras', 'type': 'electronics', 'terms': ['security cameras', 'surveillance cameras', 'home security cameras']},
            'security': {'category': 'security cameras', 'type': 'electronics', 'terms': ['security cameras', 'surveillance cameras', 'home security cameras']},
            'surveillance': {'category': 'security cameras', 'type': 'electronics', 'terms': ['surveillance cameras', 'security cameras', 'home cameras']},
            
            # Tech/Computing
            'monitor': {'category': 'computer monitors', 'type': 'electronics', 'terms': ['computer monitors', 'gaming monitors', 'desktop monitors']},
            'keyboard': {'category': 'gaming keyboards', 'type': 'electronics', 'terms': ['gaming keyboards', 'mechanical keyboards', 'computer keyboards']},
            'mouse': {'category': 'gaming mice', 'type': 'electronics', 'terms': ['gaming mice', 'computer mice', 'wireless mice']},
            
            # Home/Kitchen
            'knife': {'category': 'kitchen knives', 'type': 'home', 'terms': ['kitchen knives', 'chef knives', 'cooking knives']},
            'cookware': {'category': 'cookware sets', 'type': 'home', 'terms': ['cookware sets', 'pots and pans', 'kitchen cookware']},
            'power strip': {'category': 'power strips', 'type': 'electronics', 'terms': ['power strips', 'surge protectors', 'outlet strips']},
            
            # Fashion/Accessories
            'watch': {'category': 'smartwatches', 'type': 'electronics', 'terms': ['smartwatches', 'fitness trackers', 'wearable devices']},
            'band': {'category': 'watch bands', 'type': 'fashion', 'terms': ['watch bands', 'smartwatch bands', 'watch straps']},
            
            # Default fallback
            'default': {'category': 'electronics', 'type': 'electronics', 'terms': ['electronics', 'gadgets', 'tech accessories']}
        }
    
    async def extract_product_category(self, marketing_title: str) -> Dict[str, Any]:
        """
        TEST MODE: Extract product category using hardcoded patterns
        
        Args:
            marketing_title: Title like "🔥 5 INSANE Car Amps You Need in 2025! *Loudest Ever* 🚗"
            
        Returns:
            {
                'primary_category': 'car amplifiers',
                'search_terms': ['car amplifiers', 'automotive amplifiers', 'car audio amps'],
                'product_type': 'electronics',
                'category_confidence': 0.95
            }
        """
        
        logger.info(f"🔍 Extracting product category from: {marketing_title[:50]}...")
        
        try:
            # Clean title for pattern matching
            clean_title = self._clean_title(marketing_title)
            
            # Find matching pattern
            matched_pattern = None
            for pattern, category_info in self.category_patterns.items():
                if pattern == 'default':
                    continue
                if pattern.lower() in clean_title.lower():
                    matched_pattern = category_info
                    break
            
            # Use default if no match found
            if not matched_pattern:
                matched_pattern = self.category_patterns['default']
            
            result = {
                'success': True,
                'primary_category': matched_pattern['category'],
                'search_terms': matched_pattern['terms'][:5],
                'product_type': matched_pattern['type'],
                'category_confidence': 0.95,
                'reasoning': f"Matched pattern based on keywords in title"
            }
            
            logger.info(f"✅ Extracted category: {result['primary_category']}")
            logger.info(f"🎯 Search terms: {', '.join(result['search_terms'][:3])}")
            logger.info(f"📊 Confidence: {result['category_confidence']}")
            
            return result
                
        except Exception as e:
            logger.error(f"❌ Error extracting category: {e}")
            return {
                'success': False,
                'error': str(e),
                'primary_category': 'electronics',
                'search_terms': ['electronics', 'gadgets'],
                'product_type': 'electronics',
                'category_confidence': 0.5
            }
    
    def _clean_title(self, title: str) -> str:
        """Clean marketing title for pattern matching"""
        # Remove emojis and special characters
        clean = re.sub(r'[🔥⚡💸🚗🔪📱💻🎵🎮🏠⭐👍💯✨]', '', title)
        # Remove hype words
        hype_words = ['INSANE', 'BEST', 'TOP', '2025', 'NEW', 'SHOCKING', 'AMAZING', 'INCREDIBLE']
        for word in hype_words:
            clean = clean.replace(word, '')
        # Remove extra whitespace
        clean = ' '.join(clean.split())
        return clean
    
    def _fallback_extraction(self, marketing_title: str) -> Dict[str, Any]:
        """
        TEST MODE: Enhanced fallback using pattern matching
        """
        logger.warning("🔄 Using fallback extraction method")
        
        # Use the same logic as main extraction but with lower confidence
        clean_title = self._clean_title(marketing_title)
        
        # Find matching pattern
        for pattern, category_info in self.category_patterns.items():
            if pattern == 'default':
                continue
            if pattern.lower() in clean_title.lower():
                return {
                    'success': True,
                    'primary_category': category_info['category'],
                    'search_terms': category_info['terms'][:5],
                    'product_type': category_info['type'],
                    'category_confidence': 0.75,  # Lower confidence for fallback
                    'reasoning': f'Fallback: detected {pattern} keywords'
                }
        
        # Ultimate fallback
        return {
            'success': True,
            'primary_category': 'electronics',
            'search_terms': ['electronics', 'gadgets', 'tech accessories'],
            'product_type': 'electronics',
            'category_confidence': 0.5,
            'reasoning': 'Fallback: generic electronics category'
        }

# Test the server
async def test_category_extractor():
    server = ProductCategoryExtractorMCPServer('test_key')
    
    test_titles = [
        "🔥 5 INSANE Car Amps You Need in 2025!",
        "BEST Gaming Headsets That Will Blow Your Mind!",
        "TOP 5 Kitchen Knives Every Chef Needs 🔪",
        "Marine Subs That Will Shock You",
        "Bluetooth Speakers You Need",
        "Top 5 Surveillance & Security Cameras Editor's Picks 2025"
    ]
    
    for title in test_titles:
        result = await server.extract_product_category(title)
        print(f"Title: {title}")
        print(f"Category: {result['primary_category']}")
        print(f"Terms: {result['search_terms'][:3]}")
        print(f"Confidence: {result['category_confidence']}")
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(test_category_extractor())