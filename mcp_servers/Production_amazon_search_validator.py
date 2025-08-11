#!/usr/bin/env python3
"""
Production Amazon Search Validator MCP Server
==============================================

Validates search variants to find which ones have sufficient products
BEFORE doing detailed scraping. This saves API credits and time.

Key Features:
- Batch validation of multiple search variants concurrently
- Quick check for product availability (count + reviews)
- Returns only variants that meet criteria
- Optimized for minimal API usage
"""

import aiohttp
import asyncio
from typing import Dict, List, Optional, Tuple
import json
import time
from urllib.parse import quote

class ProductionAmazonSearchValidator:
    def __init__(self, scrapingdog_api_key: str):
        self.api_key = scrapingdog_api_key
        self.base_url = "https://api.scrapingdog.com/amazon/search"
        
    async def validate_search_variants_batch(
        self,
        variants: List[str],
        min_products: int = 5,
        min_reviews: int = 10,
        batch_size: int = 3
    ) -> Dict:
        """
        Validate multiple search variants concurrently to find which have enough products.
        
        Args:
            variants: List of search terms to validate
            min_products: Minimum number of products needed (default 5)
            min_reviews: Minimum reviews per product (default 10)
            batch_size: Number of concurrent validations (default 3)
            
        Returns:
            Dict with validation results and best variant
        """
        
        print(f"🔍 Starting batch validation of {len(variants)} search variants...")
        print(f"📊 Requirements: {min_products} products with {min_reviews}+ reviews")
        start_time = time.time()
        
        validation_results = []
        
        # Process variants in batches to respect rate limits
        for i in range(0, len(variants), batch_size):
            batch = variants[i:i + batch_size]
            print(f"\n🔄 Validating batch {i//batch_size + 1}: {batch}")
            
            # Create validation tasks for this batch
            tasks = [
                self._validate_single_variant(variant, min_reviews)
                for variant in batch
            ]
            
            # Run batch concurrently
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process batch results
            for variant, result in zip(batch, batch_results):
                if isinstance(result, Exception):
                    print(f"  ❌ {variant}: Error - {result}")
                    validation_results.append({
                        'variant': variant,
                        'valid': False,
                        'product_count': 0,
                        'qualified_count': 0,
                        'error': str(result)
                    })
                else:
                    qualified_count = result.get('qualified_count', 0)
                    is_valid = qualified_count >= min_products
                    
                    print(f"  {'✅' if is_valid else '❌'} {variant}: "
                          f"{qualified_count} qualified products "
                          f"(out of {result.get('total_count', 0)} total)")
                    
                    validation_results.append({
                        'variant': variant,
                        'valid': is_valid,
                        'product_count': result.get('total_count', 0),
                        'qualified_count': qualified_count,
                        'sample_products': result.get('sample_products', [])[:5]
                    })
                    
                    # Early exit if we found a good variant
                    if is_valid:
                        elapsed = time.time() - start_time
                        print(f"\n🎯 Found valid variant early: '{variant}' in {elapsed:.1f}s")
                        return {
                            'best_variant': variant,
                            'validation_results': validation_results,
                            'time_elapsed': elapsed,
                            'early_exit': True
                        }
            
            # Small delay between batches to avoid rate limiting
            if i + batch_size < len(variants):
                await asyncio.sleep(0.5)
        
        # Find best variant from all results
        valid_variants = [r for r in validation_results if r['valid']]
        best_variant = None
        
        if valid_variants:
            # Sort by qualified_count to get the best one
            best = max(valid_variants, key=lambda x: x['qualified_count'])
            best_variant = best['variant']
            print(f"\n🏆 Best variant: '{best_variant}' with {best['qualified_count']} products")
        else:
            print(f"\n⚠️ No variants met the criteria of {min_products} products with {min_reviews}+ reviews")
        
        elapsed = time.time() - start_time
        print(f"⏱️ Validation completed in {elapsed:.1f} seconds")
        
        return {
            'best_variant': best_variant,
            'validation_results': validation_results,
            'valid_variants': [v['variant'] for v in valid_variants],
            'time_elapsed': elapsed,
            'early_exit': False
        }
    
    async def _validate_single_variant(
        self,
        variant: str,
        min_reviews: int
    ) -> Dict:
        """
        Quickly validate a single search variant.
        Returns count of total and qualified products.
        """
        try:
            params = {
                'api_key': self.api_key,
                'domain': 'com',
                'query': variant,
                'page': '1',
                'country': 'us'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params, timeout=20) as response:
                    if response.status != 200:
                        return {'total_count': 0, 'qualified_count': 0, 'error': f'Status {response.status}'}
                    
                    data = await response.json()
                    
                    # Extract products from response
                    if isinstance(data, dict) and 'results' in data:
                        products = data['results']
                    elif isinstance(data, list):
                        products = data
                    else:
                        products = []
                    
                    # Quick count of qualified products
                    qualified_count = 0
                    sample_products = []
                    
                    for product in products:
                        reviews = self._extract_review_count(product)
                        if reviews >= min_reviews:
                            qualified_count += 1
                            
                            # Keep sample for later use
                            if len(sample_products) < 5:
                                sample_products.append({
                                    'title': product.get('title', ''),
                                    'reviews': reviews,
                                    'rating': self._extract_rating(product),
                                    'price': product.get('price', ''),
                                    'asin': product.get('asin', '')
                                })
                    
                    return {
                        'total_count': len(products),
                        'qualified_count': qualified_count,
                        'sample_products': sample_products
                    }
                    
        except asyncio.TimeoutError:
            return {'total_count': 0, 'qualified_count': 0, 'error': 'Timeout'}
        except Exception as e:
            return {'total_count': 0, 'qualified_count': 0, 'error': str(e)}
    
    def _extract_review_count(self, product: Dict) -> int:
        """Extract review count from product data"""
        try:
            # ScrapingDog API returns 'total_reviews' as a string
            reviews = product.get('total_reviews', product.get('reviews', product.get('ratings_total', '0')))
            
            if isinstance(reviews, (int, float)):
                return int(reviews)
            
            # Parse string format (e.g., "1,234" or "5,217" or "1.2K")
            reviews_str = str(reviews).replace(',', '').strip()
            
            # Handle empty or None
            if not reviews_str or reviews_str.lower() == 'none':
                return 0
            
            if 'K' in reviews_str.upper():
                return int(float(reviews_str.upper().replace('K', '')) * 1000)
            elif 'M' in reviews_str.upper():
                return int(float(reviews_str.upper().replace('M', '')) * 1000000)
            else:
                # Try to extract number from string
                import re
                numbers = re.findall(r'\d+', reviews_str)
                return int(numbers[0]) if numbers else 0
                
        except Exception as e:
            return 0
    
    def _extract_rating(self, product: Dict) -> float:
        """Extract rating from product data"""
        try:
            # ScrapingDog API returns 'stars' as a string
            rating = product.get('stars', product.get('rating', '0'))
            
            if isinstance(rating, (int, float)):
                return float(rating)
            
            # Parse string format (e.g., "4.5" or "4.5 out of 5")
            rating_str = str(rating).strip()
            
            # Handle empty or None
            if not rating_str or rating_str.lower() == 'none':
                return 0.0
            
            # Look for decimal number
            import re
            numbers = re.findall(r'(\d+\.?\d*)', rating_str)
            if numbers:
                val = float(numbers[0])
                # Normalize if it's out of a different scale
                if val > 5:
                    return 5.0
                return val
                
        except:
            return 0.0

    async def get_product_details_async(
        self,
        variant: str,
        count: int = 5,
        min_reviews: int = 10
    ) -> List[Dict]:
        """
        Get detailed product information for the validated variant.
        This is called AFTER validation succeeds.
        """
        try:
            params = {
                'api_key': self.api_key,
                'domain': 'com',
                'query': variant,
                'page': '1',
                'country': 'us'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params, timeout=30) as response:
                    if response.status != 200:
                        return []
                    
                    data = await response.json()
                    
                    # Extract products
                    if isinstance(data, dict) and 'results' in data:
                        products = data['results']
                    elif isinstance(data, list):
                        products = data
                    else:
                        products = []
                    
                    # Filter and sort by composite score
                    qualified_products = []
                    for product in products:
                        reviews = self._extract_review_count(product)
                        if reviews >= min_reviews:
                            rating = self._extract_rating(product)
                            
                            # Calculate composite score
                            import math
                            score = rating * math.log(reviews + 1)
                            
                            qualified_products.append({
                                'title': product.get('title', ''),
                                'price': product.get('price', ''),
                                'rating': rating,
                                'reviews': reviews,
                                'score': score,
                                'asin': product.get('asin', ''),
                                'link': product.get('link', ''),
                                'image': product.get('image', ''),
                                'description': product.get('description', '')
                            })
                    
                    # Sort by score and return top N
                    qualified_products.sort(key=lambda x: x['score'], reverse=True)
                    return qualified_products[:count]
                    
        except Exception as e:
            print(f"❌ Error getting product details: {e}")
            return []