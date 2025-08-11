#!/usr/bin/env python3
"""
Production Progressive Amazon Scraper
===================================

Enhanced scraper that tests multiple search variants until finding sufficient products.
Uses variant generator and progressive testing to ensure successful product discovery.
"""

import aiohttp
import asyncio
from typing import Dict, List, Optional, Tuple
import json
from urllib.parse import quote
import re

from .Production_scraping_variant_generator import ProductionScrapingVariantGenerator

class ProductionProgressiveAmazonScraper:
    def __init__(self, scrapingdog_api_key: str, openai_api_key: str):
        self.api_key = scrapingdog_api_key
        self.base_url = "https://api.scrapingdog.com/amazon/search"
        self.variant_generator = ProductionScrapingVariantGenerator(openai_api_key)
        
    async def search_with_variants(
        self, 
        title: str, 
        target_products: int = 5, 
        min_reviews: int = 10
    ) -> Tuple[List[Dict], str]:
        """
        Search Amazon products using multiple variants until finding sufficient products.
        
        Args:
            title: Original title to extract variants from
            target_products: Number of products needed (default 5)
            min_reviews: Minimum reviews per product (default 10)
            
        Returns:
            Tuple of (products_list, successful_variant)
        """
        
        print(f"🔍 Generating search variants from title: {title}")
        
        # Generate search variants
        variants = await self.variant_generator.generate_search_variants(title, max_variants=7)
        print(f"📝 Generated {len(variants)} search variants: {variants}")
        
        # Test each variant progressively
        for i, variant in enumerate(variants, 1):
            print(f"\n🔄 Testing variant {i}/{len(variants)}: '{variant}'")
            
            try:
                # Search products with current variant
                products = await self._search_products_api(variant)
                
                # Filter products by review count
                qualified_products = self._filter_by_reviews(products, min_reviews)
                
                print(f"📊 Found {len(qualified_products)} products with {min_reviews}+ reviews")
                
                # Check if we have enough qualified products
                if len(qualified_products) >= target_products:
                    # Create Top 5 countdown ranking (No1 = best rating + most reviews)
                    top_products = self._create_top5_countdown(qualified_products, target_products)
                    print(f"✅ SUCCESS! Created Top 5 countdown from {len(qualified_products)} products")
                    self._display_top5_ranking(top_products)
                    
                    # Add variant info to each product
                    for product in top_products:
                        product['search_variant_used'] = variant
                        product['variant_attempt_number'] = i
                    
                    return top_products, variant
                
                else:
                    print(f"⚠️ Not enough products ({len(qualified_products)}/{target_products}). Trying next variant...")
                    
            except Exception as e:
                print(f"❌ Error with variant '{variant}': {e}")
                continue
        
        # If no variant succeeded, try basic fallback terms
        print(f"⚠️ Could not find {target_products} products with {min_reviews}+ reviews")
        print("🔄 Trying basic fallback terms...")
        
        # Extract basic keywords and try simple searches
        basic_terms = self._extract_basic_keywords(title)
        for term in basic_terms:
            try:
                print(f"🔄 Testing basic term: '{term}'")
                products = await self._search_products_api(term)
                qualified_products = self._filter_by_reviews(products, min_reviews)
                
                if len(qualified_products) >= target_products:
                    top_products = self._create_top5_countdown(qualified_products, target_products)
                    print(f"✅ SUCCESS with basic term '{term}'!")
                    self._display_top5_ranking(top_products)
                    return top_products, term
                    
            except Exception as e:
                print(f"❌ Error with basic term '{term}': {e}")
                continue
        
        # Try again with lower review threshold
        return await self._fallback_search(variants, target_products, min_reviews=5)
    
    async def _search_products_api(self, search_query: str) -> List[Dict]:
        """Search Amazon products using ScrapingDog API"""
        try:
            params = {
                'api_key': self.api_key,
                'domain': 'com',
                'query': search_query,
                'page': '1',
                'country': 'us'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params, timeout=30) as response:
                    if response.status == 200:
                        # Check content type before trying to parse as JSON
                        content_type = response.headers.get('content-type', '')
                        response_text = await response.text()
                        
                        if 'application/json' in content_type:
                            try:
                                data = json.loads(response_text)
                                
                                # ScrapingDog returns a dict with 'results' key containing the products
                                if isinstance(data, dict) and 'results' in data:
                                    search_results = data['results']
                                elif isinstance(data, list):
                                    search_results = data
                                else:
                                    search_results = []
                                
                                # Parse and normalize product data
                                products = []
                                for result in search_results:
                                    product = self._normalize_product_data(result)
                                    if product:
                                        products.append(product)
                                
                                print(f"✅ Successfully parsed {len(products)} products from API")
                                return products
                            except json.JSONDecodeError as e:
                                print(f"❌ JSON decode error: {e}")
                                print(f"❌ Response text: {response_text[:500]}...")
                                return []
                        else:
                            print(f"❌ ScrapingDog returned HTML instead of JSON. Content type: {content_type}")
                            print(f"❌ Response preview: {response_text[:200]}...")
                            print(f"❌ Full URL: {self.base_url}?{params}")
                            return []
                    else:
                        print(f"❌ API error {response.status}: {await response.text()}")
                        return []
                        
        except Exception as e:
            print(f"❌ ScrapingDog API error: {e}")
            return []
    
    def _filter_by_reviews(self, products: List[Dict], min_reviews: int) -> List[Dict]:
        """Filter products by minimum review count and sort by quality metrics"""
        
        qualified = []
        for product in products:
            review_count = self._extract_review_count(product.get('reviews', '0'))
            rating = float(product.get('rating', 0))
            
            if review_count >= min_reviews and rating > 0:
                product['review_count_int'] = review_count
                product['rating_float'] = rating
                qualified.append(product)
        
        # Sort by review count and rating (best first)
        qualified.sort(
            key=lambda x: (x['review_count_int'], x['rating_float']), 
            reverse=True
        )
        
        return qualified
    
    async def _fallback_search(
        self, 
        variants: List[str], 
        target_products: int, 
        min_reviews: int = 5
    ) -> Tuple[List[Dict], str]:
        """Fallback search with lower review threshold"""
        
        print(f"🔄 Fallback: Searching with {min_reviews}+ reviews requirement...")
        
        for variant in variants:
            products = await self._search_products_api(variant)
            qualified = self._filter_by_reviews(products, min_reviews)
            
            if len(qualified) >= target_products:
                selected = qualified[:target_products]
                print(f"✅ Fallback SUCCESS with variant '{variant}'")
                
                for product in selected:
                    product['search_variant_used'] = variant
                    product['fallback_search'] = True
                
                return selected, variant
        
        # Last resort: return whatever we can find
        print("⚠️ Last resort: Returning any available products...")
        for variant in variants:
            products = await self._search_products_api(variant)
            if products:
                selected = products[:target_products]
                print(f"🔄 Returning {len(selected)} products (may not meet review criteria)")
                
                for product in selected:
                    product['search_variant_used'] = variant
                    product['last_resort'] = True
                
                return selected, variant
        
        return [], "No successful variant"
    
    def _normalize_product_data(self, result: Dict) -> Optional[Dict]:
        """Normalize ScrapingDog API response to consistent format"""
        try:
            return {
                'name': result.get('title', ''),
                'title': result.get('title', ''),
                'price': result.get('price', ''),
                'rating': result.get('stars', '0'),
                'reviews': result.get('total_reviews', '0'),
                'image_url': result.get('image', ''),
                'product_url': result.get('url', ''),
                'description': result.get('title', ''),
                'availability': 'In Stock',
                'brand': '',
                'category': '',
                'prime': result.get('has_prime', False),
                'bestseller': False,
                'asin': result.get('asin', '')
            }
        except Exception as e:
            print(f"❌ Error normalizing product data: {e}")
            return None

    def _extract_basic_keywords(self, title: str) -> List[str]:
        """Extract basic keywords from title for fallback searches"""
        # Remove common words and extract main product keywords
        common_words = {'top', '5', 'best', 'most', 'popular', 'on', 'amazon', '2025', '2024', 'new', 'releases', 'with', 'amazing', 'features'}
        
        # Split and clean title
        words = re.findall(r'\b[a-zA-Z]+\b', title.lower())
        keywords = [word for word in words if word not in common_words and len(word) > 2]
        
        # Create basic search terms
        basic_terms = []
        
        # Single most important keywords
        if keywords:
            basic_terms.extend(keywords[:3])  # Take top 3 keywords
        
        # Two-word combinations
        if len(keywords) >= 2:
            basic_terms.append(f"{keywords[0]} {keywords[1]}")
        
        # Add some generic fallbacks for the category
        if any(word in title.lower() for word in ['satellite', 'dish', 'mount']):
            basic_terms.extend(['satellite dish mount', 'dish mount', 'tv mount'])
        elif any(word in title.lower() for word in ['monitor', 'screen', 'display']):
            basic_terms.extend(['computer monitor', 'monitor', 'display'])
        elif any(word in title.lower() for word in ['headphone', 'audio', 'sound']):
            basic_terms.extend(['headphones', 'audio equipment'])
        
        return basic_terms[:5]  # Return max 5 basic terms

    def _create_top5_countdown(self, products: List[Dict], target_products: int) -> List[Dict]:
        """Create Top 5 countdown ranking based on rating quality and review count"""
        
        # Calculate ranking score for each product
        scored_products = []
        for product in products:
            rating = float(product.get('rating', 0))
            reviews = int(str(product.get('reviews', '0')).replace(',', '').replace('+', ''))
            
            # Weighted scoring: Rating is primary (70%), Review count is secondary (30%)
            # Rating weight: 4.5+ stars = excellent, 4.0+ = good, 3.5+ = acceptable
            rating_score = rating * 70  # Max 350 points for 5.0 stars
            
            # Review count weight: Logarithmic scale to handle large ranges
            import math
            review_score = math.log10(max(reviews, 1)) * 30  # Max ~120 points for 1M+ reviews
            
            total_score = rating_score + review_score
            
            product_with_score = product.copy()
            product_with_score['_ranking_score'] = total_score
            product_with_score['_rating_float'] = rating
            product_with_score['_reviews_int'] = reviews
            
            scored_products.append(product_with_score)
        
        # Sort by total score (highest first) = No1 position
        scored_products.sort(key=lambda x: x['_ranking_score'], reverse=True)
        
        # Return top N products (No1, No2, No3, No4, No5)
        return scored_products[:target_products]
    
    def _display_top5_ranking(self, top_products: List[Dict]):
        """Display the Top 5 countdown ranking"""
        print("\n🏆 TOP 5 COUNTDOWN RANKING:")
        for i, product in enumerate(top_products, 1):
            title = product.get('title', 'Unknown')[:50] + "..."
            rating = product.get('_rating_float', 0)
            reviews = product.get('_reviews_int', 0)
            score = product.get('_ranking_score', 0)
            price = product.get('price', 'N/A')
            
            print(f"🥇 No{i}: {title}")
            print(f"   ⭐ {rating}/5.0 stars | 📊 {reviews:,} reviews | 💰 {price} | Score: {score:.1f}")
    
    def _extract_review_count(self, reviews_text: str) -> int:
        """Extract numeric review count from text like '(1,234 reviews)' or '1.2K'"""
        if not reviews_text:
            return 0
            
        # Remove parentheses and extra text
        clean_text = re.sub(r'[^\d,K\.]+', '', str(reviews_text))
        
        if 'K' in clean_text.upper():
            # Handle "1.2K" format
            number = float(re.sub(r'[^0-9.]', '', clean_text))
            return int(number * 1000)
        else:
            # Handle "1,234" format
            number_str = re.sub(r'[^0-9]', '', clean_text)
            return int(number_str) if number_str else 0

if __name__ == "__main__":
    # Test the progressive scraper
    async def test_scraper():
        scraper = ProductionProgressiveAmazonScraper("test-key", "test-openai-key")
        
        test_title = "Top 5 Webcam Stands Most Popular on Amazon 2025"
        products, variant = await scraper.search_with_variants(test_title)
        
        print(f"\nFinal Results:")
        print(f"Successful variant: {variant}")
        print(f"Products found: {len(products)}")
        
        for i, product in enumerate(products, 1):
            print(f"{i}. {product['title'][:50]}... - {product['reviews']} reviews")
    
    # asyncio.run(test_scraper())