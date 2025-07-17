# mcp_servers/product_category_extractor_server.py
import json
import logging
import asyncio
from typing import Dict, List, Optional, Any
from anthropic import AsyncAnthropic

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductCategoryExtractorMCPServer:
    """MCP Server that converts marketing titles to clean product search terms"""
    
    def __init__(self, anthropic_api_key: str):
        self.anthropic_api_key = anthropic_api_key
        self.client = AsyncAnthropic(api_key=anthropic_api_key)
    
    async def extract_product_category(self, marketing_title: str) -> Dict[str, Any]:
        """
        Extract clean product category from marketing title
        
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
            prompt = f"""
You are a product category extraction specialist. Your job is to convert marketing titles into clean, searchable product categories that Amazon can understand.

Input title: "{marketing_title}"

Please extract:
1. PRIMARY_CATEGORY: The main product category (2-3 words max, simple and clear)
2. SEARCH_TERMS: 3-5 alternative search terms that would work on Amazon
3. PRODUCT_TYPE: General category (electronics, automotive, home, sports, etc.)
4. CONFIDENCE: How confident you are (0.0-1.0)

Rules:
- Remove ALL emojis, exclamation marks, and hype language
- Remove words like "INSANE", "BEST", "TOP", "2025", "NEW", "SHOCKING"
- Focus on the actual product being discussed
- Use terms that real shoppers would search for
- Keep it simple and clear

Format your response as JSON:
{{
    "primary_category": "clean product name",
    "search_terms": ["term1", "term2", "term3", "term4", "term5"],
    "product_type": "category",
    "category_confidence": 0.95,
    "reasoning": "why you chose this category"
}}

Examples:
- "🔥 5 INSANE Car Amps You Need in 2025!" → "car amplifiers"
- "BEST Gaming Headsets That Will Blow Your Mind!" → "gaming headsets"
- "TOP 5 Kitchen Knives Every Chef Needs 🔪" → "kitchen knives"
- "Marine Subs That Will Shock You" → "marine subwoofers" (NOT submarines)
- "Bluetooth Speakers You Need" → "bluetooth speakers"

Important context:
- "Marine Subs" refers to marine subwoofers (audio equipment for boats), NOT submarines
- "Amps" refers to amplifiers (audio equipment), NOT electrical amperage
- "Monitors" refers to computer monitors, NOT surveillance monitors
"""

            response = await self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=500,
                temperature=0.1,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            response_text = response.content[0].text.strip()
            
            # Parse JSON response
            try:
                result = json.loads(response_text)
                
                # Validate required fields
                required_fields = ['primary_category', 'search_terms', 'product_type', 'category_confidence']
                if not all(field in result for field in required_fields):
                    raise ValueError(f"Missing required fields in response: {result}")
                
                logger.info(f"✅ Extracted category: {result['primary_category']}")
                logger.info(f"🎯 Search terms: {', '.join(result['search_terms'][:3])}")
                logger.info(f"📊 Confidence: {result['category_confidence']}")
                
                return {
                    'success': True,
                    'original_title': marketing_title,
                    'primary_category': result['primary_category'],
                    'search_terms': result['search_terms'],
                    'product_type': result['product_type'],
                    'category_confidence': result['category_confidence'],
                    'reasoning': result.get('reasoning', '')
                }
                
            except json.JSONDecodeError as e:
                logger.error(f"❌ JSON parsing error: {e}")
                logger.error(f"Response: {response_text}")
                
                # Fallback: try to extract category manually
                fallback_result = self._fallback_extraction(marketing_title)
                return fallback_result
                
        except Exception as e:
            logger.error(f"❌ Category extraction failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'original_title': marketing_title
            }
    
    def _fallback_extraction(self, title: str) -> Dict[str, Any]:
        """Fallback extraction using simple keyword matching"""
        
        logger.info("🔄 Using fallback extraction method")
        
        # Clean the title
        import re
        clean_title = re.sub(r'[🔥🚗🎮🔌⚡️📱🏆💯✨🎯💎🔊🎧🎪🎨🔥]', '', title)
        clean_title = re.sub(r'[!*]', '', clean_title)
        clean_title = re.sub(r'\b(TOP|BEST|INSANE|NEW|2025|SHOCKING|GONE|FAR|EVER|NEED|YOU|WILL|THAT|THE|OF|IN|FOR|WITH|AND|OR)\b', '', clean_title, flags=re.IGNORECASE)
        clean_title = re.sub(r'\s+', ' ', clean_title).strip()
        
        # Common product mappings
        product_mappings = {
            'car amp': 'car amplifiers',
            'car amplifier': 'car amplifiers', 
            'marine sub': 'marine subwoofers',
            'gaming headset': 'gaming headsets',
            'monitor': 'computer monitors',
            'power strip': 'power strips',
            'camera stabilizer': 'camera stabilizers',
            'kitchen knife': 'kitchen knives',
            'bluetooth speaker': 'bluetooth speakers',
            'phone case': 'phone cases',
            'laptop stand': 'laptop stands',
            'wireless charger': 'wireless chargers'
        }
        
        # Find best match
        clean_lower = clean_title.lower()
        primary_category = None
        
        for keyword, category in product_mappings.items():
            if keyword in clean_lower:
                primary_category = category
                break
        
        if not primary_category:
            # Extract first few meaningful words
            words = clean_title.split()[:3]
            primary_category = ' '.join(words).lower()
        
        return {
            'success': True,
            'original_title': title,
            'primary_category': primary_category,
            'search_terms': [primary_category, clean_title.lower()],
            'product_type': 'electronics',
            'category_confidence': 0.6,
            'reasoning': 'Fallback extraction used'
        }
    
    async def batch_extract_categories(self, titles: List[str]) -> List[Dict[str, Any]]:
        """Extract categories from multiple titles in batch"""
        
        logger.info(f"🔄 Batch extracting categories from {len(titles)} titles")
        
        tasks = [self.extract_product_category(title) for title in titles]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"❌ Error processing title {i+1}: {result}")
                processed_results.append({
                    'success': False,
                    'error': str(result),
                    'original_title': titles[i]
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
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
        # Load config
        with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
            config = json.load(f)
        
        # Initialize server
        server = ProductCategoryExtractorMCPServer(config['anthropic_api_key'])
        
        # Test extraction
        await server.test_extraction(test_titles)
        
        print("\n" + "=" * 60)
        print("✅ Product Category Extraction test complete!")
    
    asyncio.run(run_test())