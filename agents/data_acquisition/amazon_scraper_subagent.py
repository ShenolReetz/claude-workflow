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
from mcp_servers.production_progressive_amazon_scraper_async import ProductionProgressiveAmazonScraper


class AmazonScraperSubAgent(BaseSubAgent):
    """
    Scrapes Amazon product data:
    - Search products by title
    - Extract product details
    - Get images, prices, ratings
    """

    def __init__(self, name: str, config: Dict[str, Any], parent_agent_id: str = None):
        super().__init__(name, config, parent_agent_id)

        # Initialize Amazon scraper
        self.scraper = ProductionProgressiveAmazonScraper(
            scrapingdog_api_key=config.get('scrapingdog_api_key')
        )

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
            # Use the scraper to find products
            products = await self.scraper.search_and_scrape(
                search_query=title,
                max_products=num_products
            )

            self.logger.info(f"✅ Found {len(products)} products")

            return {
                'products': products,
                'title': title,
                'count': len(products)
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
