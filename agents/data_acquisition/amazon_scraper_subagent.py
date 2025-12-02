"""
Amazon Scraper SubAgent
========================
Scrapes Amazon products using ScrapingDog API.
"""

import sys
import asyncio
from typing import Dict, Any, List

sys.path.append('/home/claude-workflow')

from agents.base_subagent import BaseSubAgent


class AmazonScraperSubAgent(BaseSubAgent):
    """
    Scrapes Amazon product data:
    - Search products by title
    - Extract product details
    - Get images, prices, ratings

    Uses production_amazon_scraper_mcp_server for actual scraping
    """

    def __init__(self, name: str, config: Dict[str, Any], parent_agent_id: str = None):
        super().__init__(name, config, parent_agent_id)

        # Store ScrapingDog API key
        self.scrapingdog_api_key = config.get('scrapingdog_api_key')

    async def execute_task(self, task: Dict[str, Any]) -> Any:
        """
        Scrape Amazon products

        Args:
            task: Task with 'title' and 'num_products' (default 5)

        Returns:
            List of scraped products
        """
        title = task.get('title')
        num_products = task.get('num_products', 5)

        if not title:
            raise ValueError("No title provided for scraping")

        self.logger.info(f"🔍 Scraping Amazon for: {title} (top {num_products})")

        try:
            # Use real Amazon scraper
            from mcp_servers.production_progressive_amazon_scraper_async import ProductionProgressiveAmazonScraperAsync

            scraper = ProductionProgressiveAmazonScraperAsync(
                self.scrapingdog_api_key,
                self.config.get('openai_api_key')
            )

            # Search for products using search_with_variants_async
            # This returns (products_list, best_variant)
            products, best_variant = await scraper.search_with_variants_async(
                title=title,
                target_products=num_products,
                min_reviews=10
            )

            if not products:
                raise RuntimeError("Amazon scraping failed: No products found")

            # Map field names to match expected format
            mapped_products = []
            for i, product in enumerate(products, 1):
                mapped_product = {
                    'title': product.get('title', ''),
                    'price': product.get('price', ''),
                    'rating': product.get('rating', 0),
                    'review_count': product.get('reviews', 0),  # Map 'reviews' to 'review_count'
                    'image_url': product.get('image', ''),      # Map 'image' to 'image_url'
                    'product_url': product.get('link', ''),     # Map 'link' to 'product_url'
                    'asin': product.get('asin', ''),
                    'description': product.get('description', ''),
                    'is_prime': product.get('is_prime', False),
                    'score': product.get('score', 0)
                }
                mapped_products.append(mapped_product)

                # Log each product to verify real data
                img_url = mapped_product.get('image_url', '')
                is_real_amazon = 'amazon' in img_url.lower() or 'media-amazon' in img_url.lower()
                self.logger.info(f"   Product {i}: {mapped_product['title'][:50]}...")
                self.logger.info(f"              Image: {'✅ Real Amazon' if is_real_amazon else '❌ Not Amazon'} - {img_url[:50]}...")

            self.logger.info(f"✅ Found {len(mapped_products)} REAL Amazon products with images")

            return {
                'products': mapped_products,
                'title': title,
                'count': len(mapped_products)
            }

        except Exception as e:
            self.logger.error(f"❌ Amazon scraping failed: {e}")
            raise

    async def validate_input(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input parameters"""
        if 'title' not in task or not task['title']:
            return {'valid': False, 'error': 'Missing or empty title'}

        return {'valid': True}

    async def validate_output(self, result: Any) -> Dict[str, Any]:
        """Validate output result"""
        if not isinstance(result, dict):
            return {'valid': False, 'error': 'Result must be a dictionary'}

        if 'products' not in result:
            return {'valid': False, 'error': 'Missing products in result'}

        products = result['products']
        if not isinstance(products, list):
            return {'valid': False, 'error': 'Products must be a list'}

        if len(products) == 0:
            return {'valid': False, 'error': 'No products found'}

        # Validate each product has required fields
        required_fields = ['title', 'price', 'rating', 'image_url', 'product_url']
        for product in products:
            for field in required_fields:
                if field not in product:
                    return {'valid': False, 'error': f'Product missing field: {field}'}

        return {'valid': True}
