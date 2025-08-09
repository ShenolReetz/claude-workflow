#!/usr/bin/env python3
"""
Production Amazon Category Scraper - Real Category Scraping
"""

import aiohttp
from typing import Dict, List, Optional
from urllib.parse import quote

class ProductionAmazonCategoryScraper:
    def __init__(self, scrapingdog_api_key: str):
        self.api_key = scrapingdog_api_key
        self.base_url = "https://api.scrapingdog.com/amazon/categories"
        
    async def scrape_category(self, category: str, num_products: int = 5) -> List[Dict]:
        """Scrape products from a specific Amazon category"""
        try:
            params = {
                'api_key': self.api_key,
                'domain': 'com',
                'category': category,
                'page': 1
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        products = data.get('products', [])
                        
                        # Sort by best sellers rank
                        sorted_products = sorted(
                            products,
                            key=lambda x: x.get('best_seller_rank', 999999)
                        )
                        
                        return sorted_products[:num_products]
                    else:
                        print(f"❌ Category scraping failed: {response.status}")
                        return []
                        
        except Exception as e:
            print(f"❌ Error scraping category: {e}")
            return []
    
    async def get_category_bestsellers(self, category: str) -> List[Dict]:
        """Get bestsellers from a category"""
        products = await self.scrape_category(category, 10)
        return [p for p in products if p.get('is_best_seller', False)][:5]