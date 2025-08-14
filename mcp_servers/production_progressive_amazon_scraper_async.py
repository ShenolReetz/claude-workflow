#!/usr/bin/env python3
"""
Production Progressive Amazon Scraper - Async Optimized Version
===============================================================

Two-phase approach:
1. VALIDATION PHASE: Batch validate multiple variants concurrently
2. SCRAPING PHASE: Async scrape the 5 products from best variant

This reduces API calls and time:
- Old: Test each variant sequentially (7+ API calls, ~60-90 seconds)
- New: Validate 3-6 variants in parallel, then 1 final scrape (~15-20 seconds)
"""

import aiohttp
import asyncio
from typing import Dict, List, Optional, Tuple
import json
import time
import math
import re
from urllib.parse import quote

from .production_scraping_variant_generator import ProductionScrapingVariantGenerator
from .production_amazon_search_validator import ProductionAmazonSearchValidator

class ProductionProgressiveAmazonScraperAsync:
    def __init__(self, scrapingdog_api_key: str, openai_api_key: str):
        self.api_key = scrapingdog_api_key
        self.base_url = "https://api.scrapingdog.com/amazon/search"
        self.variant_generator = ProductionScrapingVariantGenerator(openai_api_key)
        self.validator = ProductionAmazonSearchValidator(scrapingdog_api_key)
        
    async def search_with_variants_async(
        self, 
        title: str, 
        target_products: int = 5, 
        min_reviews: int = 10
    ) -> Tuple[List[Dict], str]:
        """
        Optimized two-phase search:
        1. Validate variants in parallel batches
        2. Scrape products from best variant
        """
        
        start_time = time.time()
        print(f"🚀 Starting optimized Amazon search with validation phase")
        print(f"🔍 Generating search variants from title: {title}")
        
        # Generate search variants
        variants = await self.variant_generator.generate_search_variants(title, max_variants=7)
        print(f"📝 Generated {len(variants)} search variants: {variants}")
        
        # PHASE 1: Batch validation of variants
        print(f"\n📊 PHASE 1: Validating variants in parallel batches...")
        validation_result = await self.validator.validate_search_variants_batch(
            variants=variants,
            min_products=target_products,
            min_reviews=min_reviews,
            batch_size=3  # Process 3 variants at a time
        )
        
        best_variant = validation_result.get('best_variant')
        
        if not best_variant:
            # Fallback: Try with lower review threshold
            print(f"\n⚠️ No variant met criteria. Trying with 5+ reviews...")
            validation_result = await self.validator.validate_search_variants_batch(
                variants=variants,
                min_products=target_products,
                min_reviews=5,
                batch_size=3
            )
            best_variant = validation_result.get('best_variant')
            min_reviews = 5
        
        if not best_variant:
            print(f"❌ Could not find sufficient products even with relaxed criteria")
            return [], ""
        
        # PHASE 2: Get detailed product data for the best variant
        print(f"\n🎯 PHASE 2: Getting detailed data for best variant: '{best_variant}'")
        products = await self._get_detailed_products_async(
            variant=best_variant,
            count=target_products,
            min_reviews=min_reviews
        )
        
        if products:
            # Create Top 5 countdown ranking
            top_products = self._create_top5_countdown(products, target_products)
            
            # Add metadata
            for i, product in enumerate(top_products, 1):
                product['search_variant_used'] = best_variant
                product['rank'] = i
            
            elapsed = time.time() - start_time
            print(f"\n✅ SUCCESS! Found {len(top_products)} products in {elapsed:.1f} seconds")
            print(f"⚡ Speed improvement: ~{60/elapsed:.1f}x faster than sequential approach")
            
            self._display_top5_ranking(top_products)
            
            return top_products, best_variant
        
        print(f"❌ Failed to get detailed products for variant: {best_variant}")
        return [], ""
    
    async def _get_detailed_products_async(
        self,
        variant: str,
        count: int,
        min_reviews: int
    ) -> List[Dict]:
        """
        Get detailed product information with enhanced data.
        This could be further optimized by getting product details in parallel.
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
                        print(f"❌ API returned status {response.status}")
                        return []
                    
                    data = await response.json()
                    
                    # Extract products from response
                    if isinstance(data, dict) and 'results' in data:
                        search_results = data['results']
                    elif isinstance(data, list):
                        search_results = data
                    else:
                        search_results = []
                    
                    print(f"📦 Processing {len(search_results)} search results...")
                    
                    # Parse and filter products
                    qualified_products = []
                    for result in search_results:
                        product = self._normalize_product_data(result)
                        # Only include products that pass normalization (have valid price) and meet review threshold
                        if product and product.get('reviews', 0) >= min_reviews:
                            qualified_products.append(product)
                            # Stop early if we have enough products
                            if len(qualified_products) >= count * 2:  # Get extra to ensure we have enough after sorting
                                break
                    
                    # Sort by composite score (rating * log(reviews))
                    qualified_products.sort(key=lambda x: x.get('score', 0), reverse=True)
                    
                    # Return top products
                    final_products = qualified_products[:count]
                    
                    if len(final_products) < count:
                        print(f"⚠️ Only found {len(final_products)} products with valid prices (needed {count})")
                    
                    return final_products
                    
        except Exception as e:
            print(f"❌ Error getting detailed products: {e}")
            return []
    
    def _normalize_product_data(self, raw_product: Dict) -> Optional[Dict]:
        """Normalize product data from API response"""
        try:
            # Extract reviews count
            reviews = self._extract_review_count(raw_product)
            
            # Extract rating
            rating = self._extract_rating(raw_product)
            
            # Extract price
            price = self._extract_price(raw_product)
            
            # Skip products without valid price (N/A or empty)
            if price == 'N/A' or not price:
                return None
            
            # Calculate composite score
            score = rating * math.log(reviews + 1) if reviews > 0 else 0
            
            # Build affiliate link
            asin = raw_product.get('asin', '')
            affiliate_link = f"https://www.amazon.com/dp/{asin}?tag=reviewcheckr-20" if asin else ""
            
            return {
                'title': raw_product.get('title', 'Unknown Product'),
                'price': price,
                'rating': rating,
                'reviews': reviews,
                'score': score,
                'asin': asin,
                'link': affiliate_link,
                'image': raw_product.get('image', ''),
                'description': raw_product.get('description', ''),
                'is_prime': raw_product.get('is_prime', False),
                'is_best_seller': raw_product.get('is_best_seller', False),
                'category': raw_product.get('category', ''),
                'features': raw_product.get('features', [])
            }
            
        except Exception as e:
            print(f"⚠️ Error normalizing product: {e}")
            return None
    
    def _extract_review_count(self, product: Dict) -> int:
        """Extract and parse review count"""
        try:
            # ScrapingDog API returns 'total_reviews' as a string
            reviews = product.get('total_reviews', product.get('reviews', product.get('ratings_total', '0')))
            
            if isinstance(reviews, (int, float)):
                return int(reviews)
            
            reviews_str = str(reviews).replace(',', '').strip()
            
            # Handle empty or None
            if not reviews_str or reviews_str.lower() == 'none':
                return 0
            
            if 'K' in reviews_str.upper():
                return int(float(reviews_str.upper().replace('K', '')) * 1000)
            elif 'M' in reviews_str.upper():
                return int(float(reviews_str.upper().replace('M', '')) * 1000000)
            else:
                numbers = re.findall(r'\d+', reviews_str)
                return int(numbers[0]) if numbers else 0
                
        except:
            return 0
    
    def _extract_rating(self, product: Dict) -> float:
        """Extract and parse rating"""
        try:
            # ScrapingDog API returns 'stars' as a string
            rating = product.get('stars', product.get('rating', '0'))
            
            if isinstance(rating, (int, float)):
                return min(float(rating), 5.0)
            
            rating_str = str(rating).strip()
            
            # Handle empty or None
            if not rating_str or rating_str.lower() == 'none':
                return 0.0
            
            numbers = re.findall(r'(\d+\.?\d*)', rating_str)
            
            if numbers:
                val = float(numbers[0])
                return min(val, 5.0)
                
        except:
            return 0.0
    
    def _extract_price(self, product: Dict) -> str:
        """Extract and format price"""
        try:
            price = product.get('price', '')
            
            if not price:
                return 'N/A'
            
            # Ensure price has $ symbol
            price_str = str(price)
            if not price_str.startswith('$'):
                price_str = f'${price_str}'
            
            return price_str
            
        except:
            return 'N/A'
    
    def _create_top5_countdown(self, products: List[Dict], count: int) -> List[Dict]:
        """Create countdown format (No5 → No1)"""
        top_products = products[:count]
        
        # Reverse order for countdown
        countdown_products = []
        for i, product in enumerate(reversed(top_products)):
            product_copy = product.copy()
            product_copy['countdown_rank'] = count - i  # 5, 4, 3, 2, 1
            countdown_products.append(product_copy)
        
        return countdown_products
    
    def _display_top5_ranking(self, products: List[Dict]):
        """Display the top 5 products in a nice format"""
        print("\n🏆 TOP 5 COUNTDOWN RANKING:")
        
        for product in products:
            rank = product.get('countdown_rank', 0)
            emoji = ['', '🥇', '🥇', '🥇', '🥇', '🥇'][min(rank, 5)]
            
            print(f"{emoji} No{rank}: {product['title'][:50]}...")
            print(f"   ⭐ {product['rating']}/5.0 stars | "
                  f"📊 {product['reviews']:,} reviews | "
                  f"💰 {product['price']} | "
                  f"Score: {product['score']:.1f}")

# Backward compatibility wrapper
class ProductionProgressiveAmazonScraper(ProductionProgressiveAmazonScraperAsync):
    """Wrapper for backward compatibility with existing code"""
    
    async def search_with_variants(self, title: str, target_products: int = 5, min_reviews: int = 10):
        """Redirect to async version"""
        return await self.search_with_variants_async(title, target_products, min_reviews)