#!/usr/bin/env python3
"""
Amazon Product Validator - Pre-validates if enough products exist before starting workflow
"""
import asyncio
import json
import logging
import re
import time
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote
import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class AmazonProductValidator:
    """Validates that Amazon has sufficient products before starting workflow"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.api_key = config.get('scrapingdog_api_key', '')
        self.base_url = 'https://api.scrapingdog.com/scrape'
        self.last_request_time = 0
        self.min_delay = 6  # ScrapingDog requires 6 second delays
        self.min_products_required = 5
        self.min_review_threshold = 10  # Minimum reviews for quality products
        
        if not self.api_key:
            logger.warning("ScrapingDog API key not found in config!")
    
    async def rate_limit(self):
        """Implement rate limiting for ScrapingDog"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_delay:
            delay = self.min_delay - time_since_last
            logger.info(f"Rate limiting: waiting {delay:.2f} seconds")
            await asyncio.sleep(delay)
        
        self.last_request_time = time.time()
    
    def generate_search_variations(self, base_term: str) -> List[str]:
        """Generate multiple search variations for better product discovery"""
        variations = [base_term]
        
        # Add common synonyms and variations
        term_variations = {
            'amplifier': ['amplifiers', 'amp', 'amps'],
            'speaker': ['speakers', 'audio'],
            'headphone': ['headphones', 'headset', 'earbuds'],
            'camera': ['cameras', 'cam'],
            'laptop': ['laptops', 'notebook', 'computer'],
            'phone': ['phones', 'smartphone', 'mobile'],
            'watch': ['watches', 'smartwatch'],
            'tablet': ['tablets', 'pad'],
            'mouse': ['mice', 'gaming mouse'],
            'keyboard': ['keyboards', 'gaming keyboard'],
            'monitor': ['monitors', 'display', 'screen'],
            'router': ['routers', 'wifi router'],
            'charger': ['chargers', 'charging cable'],
            'cable': ['cables', 'cord'],
            'case': ['cases', 'cover'],
            'battery': ['batteries', 'power bank'],
            'adapter': ['adapters', 'converter'],
            'mount': ['mounts', 'mounting'],
            'stand': ['stands', 'holder'],
            'light': ['lights', 'lighting', 'lamp'],
            'fan': ['fans', 'cooling'],
            'drive': ['drives', 'storage'],
            'memory': ['ram', 'memory card'],
            'processor': ['cpu', 'chip'],
            'graphics': ['gpu', 'video card'],
            'audio': ['sound', 'music'],
            'video': ['recording', 'streaming'],
            'gaming': ['game', 'esports'],
            'wireless': ['bluetooth', 'wifi'],
            'portable': ['mobile', 'travel'],
            'professional': ['pro', 'studio'],
            'outdoor': ['waterproof', 'rugged'],
            'indoor': ['home', 'office'],
            'car': ['automotive', 'vehicle'],
            'marine': ['boat', 'waterproof'],
            'motorcycle': ['bike', 'motorbike']
        }
        
        # Generate variations
        words = base_term.lower().split()
        for word in words:
            if word in term_variations:
                for variation in term_variations[word]:
                    # Replace word with variation
                    new_term = base_term.lower().replace(word, variation)
                    if new_term not in variations:
                        variations.append(new_term)
        
        # Add broader and narrower terms
        broader_terms = []
        narrower_terms = []
        
        if 'wireless' in base_term:
            broader_terms.append(base_term.replace('wireless ', ''))
        if 'gaming' in base_term:
            broader_terms.append(base_term.replace('gaming ', ''))
        if 'professional' in base_term:
            broader_terms.append(base_term.replace('professional ', ''))
        
        # Add common product categories
        if any(word in base_term for word in ['amplifier', 'speaker', 'headphone']):
            narrower_terms.append(f"{base_term} audio")
        if any(word in base_term for word in ['camera', 'video']):
            narrower_terms.append(f"{base_term} recording")
        if any(word in base_term for word in ['laptop', 'computer']):
            narrower_terms.append(f"{base_term} pc")
        
        variations.extend(broader_terms)
        variations.extend(narrower_terms)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_variations = []
        for term in variations:
            if term not in seen:
                seen.add(term)
                unique_variations.append(term)
        
        return unique_variations[:8]  # Limit to 8 variations to avoid too many API calls
    
    async def quick_product_count(self, search_term: str) -> Tuple[int, List[Dict]]:
        """Quickly check how many products Amazon has for a search term"""
        try:
            await self.rate_limit()
            
            logger.info(f"🔍 Checking product count for: {search_term}")
            
            # Amazon search URL
            target_url = f"https://www.amazon.com/s?k={quote(search_term)}&s=review-rank"
            
            # ScrapingDog parameters
            params = {
                'api_key': self.api_key,
                'url': target_url,
                'dynamic': 'false',
                'country': 'us'
            }
            
            async with httpx.AsyncClient(timeout=86400) as client:
                response = await client.get(self.base_url, params=params)
                
                if response.status_code != 200:
                    logger.warning(f"ScrapingDog returned {response.status_code} for: {search_term}")
                    return 0, []
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find all products
                products = soup.select('[data-component-type="s-search-result"]')
                
                if not products:
                    logger.warning(f"No products found for: {search_term}")
                    return 0, []
                
                # Quick validation - check if products have reviews
                quality_products = []
                for product in products[:10]:  # Check first 10 products
                    try:
                        # Get review count
                        review_elem = product.select_one('span.a-size-base.s-underline-text')
                        if review_elem:
                            review_text = review_elem.text.strip()
                            review_count = int(review_text.replace(',', '')) if review_text.replace(',', '').isdigit() else 0
                            
                            if review_count >= self.min_review_threshold:
                                # Get basic product info
                                title_elem = product.select_one('h2 span')
                                title = title_elem.text.strip() if title_elem else 'Unknown'
                                
                                rating_elem = product.select_one('span.a-icon-alt')
                                rating_text = rating_elem.text if rating_elem else '0 out of 5 stars'
                                rating = float(rating_text.split()[0]) if rating_text else 0.0
                                
                                quality_products.append({
                                    'title': title,
                                    'reviews': review_count,
                                    'rating': rating,
                                    'score': review_count * rating
                                })
                    except Exception as e:
                        logger.debug(f"Error parsing product: {e}")
                        continue
                
                logger.info(f"Found {len(products)} total products, {len(quality_products)} with {self.min_review_threshold}+ reviews")
                return len(quality_products), quality_products
                
        except Exception as e:
            logger.error(f"Error checking product count for {search_term}: {e}")
            return 0, []
    
    async def validate_title_for_amazon(self, title: str) -> Dict:
        """
        Validate if a title has enough products on Amazon
        
        Args:
            title: Airtable title like "Top 5 Value-for-Money Marine Subwoofers 2025"
            
        Returns:
            {
                'valid': True/False,
                'primary_search_term': 'best_working_term',
                'product_count': 15,
                'confidence': 0.85,
                'sample_products': [...],
                'alternative_terms': [...],
                'validation_message': 'Found 15 quality products...'
            }
        """
        
        logger.info(f"🔍 Validating title: {title}")
        
        # Import the product category extractor
        import sys
        sys.path.append('/home/claude-workflow')
        from mcp_servers.product_category_extractor_server import ProductCategoryExtractorMCPServer
        
        # Extract category
        extractor = ProductCategoryExtractorMCPServer(self.config['anthropic_api_key'])
        category_result = await extractor.extract_product_category(title)
        
        primary_category = category_result['primary_category']
        search_terms = category_result['search_terms']
        
        logger.info(f"📋 Primary category: {primary_category}")
        logger.info(f"🔍 Search terms: {search_terms}")
        
        # Generate additional search variations
        all_search_terms = [primary_category] + search_terms
        
        # Add variations for each term
        expanded_terms = []
        for term in all_search_terms:
            variations = self.generate_search_variations(term)
            expanded_terms.extend(variations)
        
        # Remove duplicates
        unique_terms = list(dict.fromkeys(expanded_terms))
        
        logger.info(f"🔄 Testing {len(unique_terms)} search variations")
        
        # Test each search term
        best_result = {
            'valid': False,
            'primary_search_term': primary_category,
            'product_count': 0,
            'confidence': 0.0,
            'sample_products': [],
            'alternative_terms': [],
            'validation_message': 'No suitable products found on Amazon'
        }
        
        for term in unique_terms:
            try:
                count, products = await self.quick_product_count(term)
                
                if count >= self.min_products_required:
                    # Calculate confidence based on product count and quality
                    avg_rating = sum(p['rating'] for p in products) / len(products) if products else 0
                    avg_reviews = sum(p['reviews'] for p in products) / len(products) if products else 0
                    
                    # Confidence factors
                    count_factor = min(count / 10, 1.0)  # More products = higher confidence
                    rating_factor = avg_rating / 5.0     # Higher ratings = higher confidence
                    review_factor = min(avg_reviews / 100, 1.0)  # More reviews = higher confidence
                    
                    confidence = (count_factor * 0.4 + rating_factor * 0.3 + review_factor * 0.3)
                    
                    if confidence > best_result['confidence']:
                        best_result = {
                            'valid': True,
                            'primary_search_term': term,
                            'product_count': count,
                            'confidence': confidence,
                            'sample_products': products[:5],  # Top 5 products
                            'alternative_terms': [t for t in unique_terms if t != term][:5],
                            'validation_message': f'Found {count} quality products (avg {avg_rating:.1f}⭐, {avg_reviews:.0f} reviews)'
                        }
                        
                        logger.info(f"✅ Good match: {term} - {count} products (confidence: {confidence:.2f})")
                        
                        # If we found a really good match, stop searching
                        if confidence > 0.8 and count >= 10:
                            break
                else:
                    logger.info(f"❌ Insufficient products: {term} - {count} products")
                    
            except Exception as e:
                logger.error(f"Error testing term '{term}': {e}")
                continue
        
        # Log final result
        if best_result['valid']:
            logger.info(f"✅ Title validation PASSED: {best_result['validation_message']}")
        else:
            logger.warning(f"❌ Title validation FAILED: {best_result['validation_message']}")
        
        return best_result

async def test_validator():
    """Test the validator with sample titles"""
    
    # Load config
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    validator = AmazonProductValidator(config)
    
    # Test titles
    test_titles = [
        "Top 5 Value-for-Money Marine Subwoofers 2025",
        "🔥 5 INSANE Car Amplifiers You Need in 2025! 🚗",
        "Best 5 Wireless Gaming Headsets 2025",
        "Top 5 Laptops for Students 2025",
        "5 Must-Have Kitchen Gadgets 2025"
    ]
    
    for title in test_titles:
        print(f"\n{'='*60}")
        print(f"Testing: {title}")
        print('='*60)
        
        result = await validator.validate_title_for_amazon(title)
        
        print(f"Valid: {result['valid']}")
        print(f"Best Term: {result['primary_search_term']}")
        print(f"Product Count: {result['product_count']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Message: {result['validation_message']}")
        
        if result['sample_products']:
            print(f"\nSample Products:")
            for i, product in enumerate(result['sample_products'], 1):
                print(f"  {i}. {product['title'][:50]}... ({product['reviews']} reviews, {product['rating']}⭐)")

if __name__ == "__main__":
    asyncio.run(test_validator())