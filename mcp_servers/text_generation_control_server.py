#!/usr/bin/env python3
"""
Text Generation Control MCP Server
Quality control for text outputs - validates timing, keywords, and sends back for regeneration if needed
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextGenerationControlMCPServer:
    """Quality control for all text generation - validates and sends back if needed"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # TTS timing constraints
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
    
    async def check_countdown_products(self, 
                                     products: List[Dict], 
                                     keywords: List[str],
                                     category: str) -> Dict[str, Any]:
        """
        Check if generated products meet all criteria
        """
        logger.info(f"🔍 Checking {len(products)} products for quality control")
        
        validation_results = []
        products_needing_regeneration = []
        all_valid = True
        
        for i, product in enumerate(products):
            product_num = i + 1
            
            # Validate this product
            validation = await self._validate_single_product(
                product_num=product_num,
                title=product.get('title', ''),
                description=product.get('description', ''),
                keywords=keywords,
                category=category
            )
            
            validation_results.append(validation)
            
            if not validation['is_valid']:
                all_valid = False
                products_needing_regeneration.append({
                    'product_number': product_num,
                    'issues': validation['issues'],
                    'regeneration_instructions': validation['regeneration_instructions']
                })
        
        # Calculate timing summary
        timing_summary = self._calculate_timing_summary(validation_results)
        
        return {
            'all_valid': all_valid,
            'validation_results': validation_results,
            'products_needing_regeneration': products_needing_regeneration,
            'timing_summary': timing_summary,
            'requires_regeneration': len(products_needing_regeneration) > 0
        }
    
    async def _validate_single_product(self,
                                     product_num: int,
                                     title: str,
                                     description: str,
                                     keywords: List[str],
                                     category: str) -> Dict[str, Any]:
        """
        Validate a single product against all criteria
        """
        issues = []
        regeneration_instructions = []
        
        # 1. Check title length
        title_words = len(title.split())
        if title_words < self.min_title_words:
            issues.append(f"Title too short ({title_words} words, need {self.min_title_words}+)")
            regeneration_instructions.append(f"Expand title to {self.min_title_words}-{self.max_title_words} words")
        elif title_words > self.max_title_words:
            issues.append(f"Title too long ({title_words} words, max {self.max_title_words})")
            regeneration_instructions.append(f"Shorten title to {self.max_title_words} words")
        
        # 2. Check description length
        desc_words = len(description.split())
        if desc_words < self.min_description_words:
            issues.append(f"Description too short ({desc_words} words, need {self.min_description_words}+)")
            regeneration_instructions.append(f"Expand description to {self.min_description_words}-{self.max_description_words} words")
        elif desc_words > self.max_description_words:
            issues.append(f"Description too long ({desc_words} words, max {self.max_description_words})")
            regeneration_instructions.append(f"Shorten description to {self.max_description_words} words")
        
        # 3. Check total timing
        total_words = title_words + desc_words
        estimated_seconds = total_words / self.words_per_second
        
        if estimated_seconds < self.min_seconds_per_product:
            issues.append(f"Too short for TTS ({estimated_seconds:.1f}s, need {self.min_seconds_per_product}s+)")
            regeneration_instructions.append(f"Add {int((self.min_seconds_per_product - estimated_seconds) * self.words_per_second)} more words")
        elif estimated_seconds > self.max_seconds_per_product:
            issues.append(f"Too long for TTS ({estimated_seconds:.1f}s, max {self.max_seconds_per_product}s)")
            regeneration_instructions.append(f"Remove {int((estimated_seconds - self.max_seconds_per_product) * self.words_per_second)} words")
        
        # 4. Check keyword usage
        keywords_found = self._check_keyword_usage(title + " " + description, keywords)
        if keywords_found < 2:
            issues.append(f"Insufficient keyword usage (found {keywords_found}, need 2+)")
            regeneration_instructions.append(f"Include at least 2 of these keywords: {', '.join(keywords[:5])}")
        
        # 5. Check category relevance
        if not self._check_category_relevance(title, category):
            issues.append(f"Title doesn't seem relevant to {category} category")
            regeneration_instructions.append(f"Ensure product is clearly a {category} item")
        
        # 6. Check for real product (not generic)
        if self._is_generic_title(title):
            issues.append("Title seems generic, not a real product")
            regeneration_instructions.append("Use specific brand and model names")
        
        is_valid = len(issues) == 0
        
        return {
            'product_number': product_num,
            'is_valid': is_valid,
            'title': title,
            'description': description,
            'title_words': title_words,
            'description_words': desc_words,
            'total_words': total_words,
            'estimated_seconds': round(estimated_seconds, 1),
            'keywords_found': keywords_found,
            'issues': issues,
            'regeneration_instructions': regeneration_instructions
        }
    
    def _check_keyword_usage(self, text: str, keywords: List[str]) -> int:
        """Count how many keywords are used in the text"""
        text_lower = text.lower()
        count = 0
        
        for keyword in keywords:
            if keyword.lower() in text_lower:
                count += 1
        
        return count
    
    def _check_category_relevance(self, title: str, category: str) -> bool:
        """Check if title is relevant to category"""
        title_lower = title.lower()
        category_lower = category.lower()
        
        # Category-specific indicators
        category_indicators = {
            'electronics': ['phone', 'laptop', 'tablet', 'computer', 'camera', 'tv', 'speaker', 'headphone', 'monitor', 'console'],
            'gaming': ['gaming', 'gamer', 'xbox', 'playstation', 'nintendo', 'gpu', 'graphics'],
            'home': ['home', 'kitchen', 'furniture', 'appliance', 'decor'],
            'fashion': ['shirt', 'dress', 'shoes', 'jacket', 'pants', 'clothing'],
            'sports': ['fitness', 'gym', 'running', 'workout', 'sport', 'athletic'],
        }
        
        # Check if category indicators are present
        indicators = category_indicators.get(category_lower, [])
        
        return any(indicator in title_lower for indicator in indicators)
    
    def _is_generic_title(self, title: str) -> bool:
        """Check if title is too generic (not a real product)"""
        generic_patterns = [
            r'^(the\s+)?best\s+',
            r'^(amazing|great|awesome|fantastic)\s+',
            r'^(top|premium|quality)\s+\w+$',
            r'product\s+\d+',
            r'item\s+\#\d+'
        ]
        
        title_lower = title.lower()
        
        # Check for generic patterns
        for pattern in generic_patterns:
            if re.search(pattern, title_lower):
                return True
        
        # Check if it has a brand name (usually capitalized)
        words = title.split()
        capitalized_words = [w for w in words if w[0].isupper()]
        
        # If no capitalized words (potential brand names), might be generic
        if len(capitalized_words) == 0:
            return True
        
        return False
    
    def _calculate_timing_summary(self, validation_results: List[Dict]) -> Dict:
        """Calculate overall timing summary"""
        total_seconds = sum(v['estimated_seconds'] for v in validation_results)
        valid_products = sum(1 for v in validation_results if v['is_valid'])
        
        return {
            'total_products_duration': round(total_seconds, 1),
            'average_product_duration': round(total_seconds / len(validation_results), 1) if validation_results else 0,
            'intro_duration': 5,
            'outro_duration': 5,
            'total_video_duration': round(total_seconds + 10, 1),
            'valid_products': valid_products,
            'invalid_products': len(validation_results) - valid_products,
            'timing_acceptable': 40 <= total_seconds <= 50  # 40-50 seconds for 5 products is good
        }
    
    async def check_intro_outro(self, intro: str, outro: str) -> Dict[str, Any]:
        """Check if intro and outro meet timing requirements"""
        
        intro_words = len(intro.split())
        outro_words = len(outro.split())
        
        intro_seconds = intro_words / self.words_per_second
        outro_seconds = outro_words / self.words_per_second
        
        intro_valid = 4 <= intro_seconds <= 6
        outro_valid = 4 <= outro_seconds <= 6
        
        return {
            'intro': {
                'text': intro,
                'words': intro_words,
                'estimated_seconds': round(intro_seconds, 1),
                'is_valid': intro_valid,
                'issue': None if intro_valid else f"Should be 5 seconds (currently {intro_seconds:.1f}s)"
            },
            'outro': {
                'text': outro,
                'words': outro_words,
                'estimated_seconds': round(outro_seconds, 1),
                'is_valid': outro_valid,
                'issue': None if outro_valid else f"Should be 5 seconds (currently {outro_seconds:.1f}s)"
            },
            'both_valid': intro_valid and outro_valid
        }


# Test function
async def test_server():
    """Test the text generation control server"""
    
    config = {}
    server = TextGenerationControlMCPServer(config)
    
    # Test products (some good, some bad)
    test_products = [
        {
            'title': 'ASUS ROG Strix G15',  # Good: 5 words
            'description': 'Powerful gaming laptop featuring RTX 4070 graphics and AMD Ryzen processor for ultimate performance.'  # Good: 15 words
        },
        {
            'title': 'Gaming Laptop',  # Bad: Too short, too generic
            'description': 'Great for gaming.'  # Bad: Too short
        },
        {
            'title': 'Apple MacBook Pro 16-inch M3 Max with 64GB RAM',  # Bad: Too long
            'description': 'Professional laptop.'  # Bad: Too short
        }
    ]
    
    keywords = ['gaming', 'laptop', 'performance', 'graphics', 'portable']
    category = 'Electronics'
    
    result = await server.check_countdown_products(test_products, keywords, category)
    
    print(f"\n✅ Valid products: {result['timing_summary']['valid_products']}")
    print(f"❌ Invalid products: {result['timing_summary']['invalid_products']}")
    
    if result['products_needing_regeneration']:
        print("\n🔄 Products needing regeneration:")
        for product in result['products_needing_regeneration']:
            print(f"\nProduct #{product['product_number']}:")
            print(f"Issues: {', '.join(product['issues'])}")
            print(f"Instructions: {', '.join(product['regeneration_instructions'])}")

if __name__ == "__main__":
    asyncio.run(test_server())
