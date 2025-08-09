# mcp_servers/Test_product_category_extractor_server.py
import json
import logging
import asyncio
import re
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestProductCategoryExtractorMCPServer:
    """Test MCP Server with hardcoded category extraction responses"""
    
    def __init__(self, anthropic_api_key: str):
        self.anthropic_api_key = anthropic_api_key
        # No actual client initialization needed for test mode
        print("🧪 TEST MODE: Product Category Extractor using hardcoded responses")
        logger.info("🧪 Test Product Category Extractor initialized")
    
    async def extract_product_category(self, marketing_title: str) -> Dict[str, Any]:
        """
        Return hardcoded category extraction results for testing
        """
        
        logger.info(f"🔍 Test: Extracting product category from: {marketing_title[:50]}...")
        print(f"🧪 TEST: Extracting category from: {marketing_title}")
        
        try:
            # Clean title for pattern matching
            clean_title = marketing_title.lower()
            
            # Hardcoded category mappings for common test cases
            category_mappings = {
                'gaming headset': {
                    'primary_category': 'gaming headsets',
                    'search_terms': ['gaming headsets', 'gaming headphones', 'pc gaming headsets', 'esports headsets', 'gaming audio'],
                    'product_type': 'electronics',
                    'category_confidence': 0.98,
                    'reasoning': 'Clear gaming audio equipment identification'
                },
                'car amp': {
                    'primary_category': 'car amplifiers',
                    'search_terms': ['car amplifiers', 'automotive amplifiers', 'car audio amps', 'vehicle amplifiers', 'car stereo amps'],
                    'product_type': 'automotive',
                    'category_confidence': 0.95,
                    'reasoning': 'Automotive audio amplification equipment'
                },
                'marine sub': {
                    'primary_category': 'marine subwoofers',
                    'search_terms': ['marine subwoofers', 'boat subwoofers', 'marine audio', 'waterproof subwoofers', 'boat speakers'],
                    'product_type': 'marine',
                    'category_confidence': 0.94,
                    'reasoning': 'Marine audio equipment - subwoofers for boats'
                },
                'monitor': {
                    'primary_category': 'computer monitors',
                    'search_terms': ['computer monitors', 'gaming monitors', 'pc monitors', 'display monitors', 'lcd monitors'],
                    'product_type': 'electronics',
                    'category_confidence': 0.92,
                    'reasoning': 'Computer display equipment'
                },
                'power strip': {
                    'primary_category': 'power strips',
                    'search_terms': ['power strips', 'surge protectors', 'electrical outlets', 'power bars', 'extension cords'],
                    'product_type': 'electronics',
                    'category_confidence': 0.96,
                    'reasoning': 'Electrical power distribution equipment'
                },
                'camera stabilizer': {
                    'primary_category': 'camera stabilizers',
                    'search_terms': ['camera stabilizers', 'gimbal stabilizers', 'video stabilizers', 'camera gimbals', 'smartphone gimbals'],
                    'product_type': 'photography',
                    'category_confidence': 0.93,
                    'reasoning': 'Camera stabilization equipment'
                },
                'kitchen knife': {
                    'primary_category': 'kitchen knives',
                    'search_terms': ['kitchen knives', 'chef knives', 'cooking knives', 'cutlery', 'kitchen cutlery'],
                    'product_type': 'kitchen',
                    'category_confidence': 0.97,
                    'reasoning': 'Kitchen cutting tools'
                },
                'bluetooth speaker': {
                    'primary_category': 'bluetooth speakers',
                    'search_terms': ['bluetooth speakers', 'wireless speakers', 'portable speakers', 'mobile speakers', 'audio speakers'],
                    'product_type': 'electronics',
                    'category_confidence': 0.98,
                    'reasoning': 'Wireless audio equipment'
                },
                'phone case': {
                    'primary_category': 'phone cases',
                    'search_terms': ['phone cases', 'smartphone cases', 'mobile cases', 'protective cases', 'cell phone covers'],
                    'product_type': 'mobile accessories',
                    'category_confidence': 0.96,
                    'reasoning': 'Mobile device protection accessories'
                }
            }
            
            # Find best match
            result = None
            for keyword, category_data in category_mappings.items():
                if keyword in clean_title:
                    result = category_data
                    break
            
            # Default fallback for unmatched titles
            if not result:
                # Extract key words from title
                words = re.findall(r'\b[a-z]{3,}\b', clean_title)
                meaningful_words = [w for w in words if w not in ['best', 'top', 'insane', 'need', 'you', 'will', 'that', 'the', 'and', 'for', 'with']][:3]
                
                primary_category = ' '.join(meaningful_words) if meaningful_words else 'general products'
                
                result = {
                    'primary_category': primary_category,
                    'search_terms': [primary_category, ' '.join(meaningful_words[:2])] if meaningful_words else ['products'],
                    'product_type': 'general',
                    'category_confidence': 0.75,
                    'reasoning': 'Fallback extraction from title keywords'
                }
            
            logger.info(f"✅ Test: Extracted category: {result['primary_category']}")
            logger.info(f"🎯 Test: Search terms: {', '.join(result['search_terms'][:3])}")
            logger.info(f"📊 Test: Confidence: {result['category_confidence']}")
            print(f"🧪 TEST: Category extracted - {result['primary_category']}")
            
            return {
                'success': True,
                'original_title': marketing_title,
                'primary_category': result['primary_category'],
                'search_terms': result['search_terms'],
                'product_type': result['product_type'],
                'category_confidence': result['category_confidence'],
                'reasoning': result['reasoning'],
                'test_mode': True,
                'api_usage': 0  # No API tokens used in test mode
            }
                
        except Exception as e:
            logger.error(f"❌ Test category extraction error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'original_title': marketing_title,
                'test_mode': True
            }
    
    async def batch_extract_categories(self, titles: List[str]) -> List[Dict[str, Any]]:
        """Extract categories from multiple titles in batch (test mode)"""
        
        logger.info(f"🔄 Test: Batch extracting categories from {len(titles)} titles")
        print(f"🧪 TEST: Batch processing {len(titles)} titles")
        
        # Process sequentially in test mode to avoid overwhelming logs
        results = []
        for title in titles:
            result = await self.extract_product_category(title)
            results.append(result)
            await asyncio.sleep(0.1)  # Small delay for readability
        
        successful = sum(1 for r in results if r['success'])
        logger.info(f"✅ Test: Batch complete - {successful}/{len(titles)} successful")
        print(f"🧪 TEST: Batch complete - {successful}/{len(titles)} successful")
        
        return results
    
    async def test_extraction(self, test_titles: List[str]) -> None:
        """Test the extraction with sample titles"""
        
        print("🧪 Testing Product Category Extraction")
        print("=" * 60)
        
        for title in test_titles:
            print(f"\n📝 Original: {title}")
            result = await self.extract_product_category(title)
            
            if result['success']:
                print(f"✅ Category: {result['primary_category']}")
                print(f"🎯 Search Terms: {', '.join(result['search_terms'][:3])}")
                print(f"📊 Confidence: {result['category_confidence']}")
                print(f"🧠 Reasoning: {result['reasoning']}")
            else:
                print(f"❌ Error: {result['error']}")

# Test function
if __name__ == "__main__":
    import os
    
    # Test titles from the Airtable
    test_titles = [
        "🔥 5 INSANE Car Amps You Need in 2025! *Loudest Ever* 🚗",
        "🔥 5 INSANE Marine Subs That Will Shock You (2025 DEALS)",
        "INSANE Monitors You NEED in 2025! 🔥 (Gone Too Far?)",
        "BEST Power Strips in 2025! 🔌 (Shocking Test Results) ⚡️",
        "🔥 5 INSANE Camera Stabilizers You Need in 2025! 📱",
        "Top 5 New Car Mono Amplifiers Releases 2025",
        "🔥 TOP 5 Gaming Headsets That Will Blow Your Mind! 🎮",
        "BEST Kitchen Knives Every Chef Needs 🔪 (Professional Grade)",
        "🔥 5 INSANE Bluetooth Speakers You Need! 🔊 (Bass Test)",
        "TOP 5 Phone Cases That Actually Work! 📱 (Drop Test)"
    ]
    
    async def run_test():
        print("🧪 TEST MODE: No API keys needed - using hardcoded responses")
        
        # Initialize test server
        server = TestProductCategoryExtractorMCPServer('test-api-key')
        
        # Test extraction
        await server.test_extraction(test_titles)
        
        print("\n" + "=" * 60)
        print("✅ Test Product Category Extraction complete!")
    
    asyncio.run(run_test())