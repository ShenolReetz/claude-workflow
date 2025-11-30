"""
Product Validator SubAgent
===========================
Validates scraped Amazon products for quality and completeness.
"""

import sys
import asyncio
from typing import Dict, Any, List

sys.path.append('/home/claude-workflow')

from agents.base_subagent import BaseSubAgent


class ProductValidatorSubAgent(BaseSubAgent):
    """
    Validates product data:
    - Checks required fields present
    - Validates URLs and images
    - Ensures price and rating format
    - Filters low-quality products

    Note: All validation logic is self-contained in this subagent.
    No external MCP server needed.
    """

    def __init__(self, name: str, config: Dict[str, Any], parent_agent_id: str = None):
        super().__init__(name, config, parent_agent_id)

        # Validation thresholds
        self.min_rating = config.get('min_product_rating', 3.5)
        self.min_reviews = config.get('min_product_reviews', 10)

    async def execute_task(self, task: Dict[str, Any]) -> Any:
        """
        Validate products

        Args:
            task: Task with 'products' list

        Returns:
            Valid products and validation report
        """
        products = task.get('products', [])

        if not products:
            raise ValueError("No products provided for validation")

        self.logger.info(f"✅ Validating {len(products)} products...")

        try:
            valid_products = []
            validation_report = {
                'total': len(products),
                'valid': 0,
                'invalid': 0,
                'issues': []
            }

            for i, product in enumerate(products, 1):
                is_valid, issues = await self._validate_product(product)

                if is_valid:
                    valid_products.append(product)
                    validation_report['valid'] += 1
                else:
                    validation_report['invalid'] += 1
                    validation_report['issues'].append({
                        'product_index': i,
                        'title': product.get('title', 'Unknown'),
                        'issues': issues
                    })

            self.logger.info(f"✅ Validation complete: {validation_report['valid']}/{validation_report['total']} valid")

            return {
                'valid_products': valid_products,
                'report': validation_report
            }

        except Exception as e:
            self.logger.error(f"❌ Product validation failed: {e}")
            raise

    async def _validate_product(self, product: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate a single product

        Returns:
            (is_valid, list_of_issues)
        """
        issues = []

        # Check required fields
        required_fields = ['title', 'price', 'rating', 'review_count', 'image_url', 'product_url', 'asin']
        for field in required_fields:
            if field not in product or not product[field]:
                issues.append(f"Missing required field: {field}")

        # Validate title
        if 'title' in product:
            if len(product['title']) < 10:
                issues.append("Title too short")
            if len(product['title']) > 300:
                issues.append("Title too long")

        # Validate price
        if 'price' in product:
            try:
                price_str = product['price'].replace('$', '').replace(',', '')
                price = float(price_str)
                if price <= 0:
                    issues.append("Invalid price (zero or negative)")
                if price > 10000:
                    issues.append("Price suspiciously high")
            except (ValueError, AttributeError):
                issues.append("Invalid price format")

        # Validate rating
        if 'rating' in product:
            try:
                rating = float(product['rating'])
                if rating < 0 or rating > 5:
                    issues.append("Rating out of range (0-5)")
                if rating < self.min_rating:
                    issues.append(f"Rating below minimum threshold ({self.min_rating})")
            except (ValueError, AttributeError):
                issues.append("Invalid rating format")

        # Validate review count
        if 'review_count' in product:
            try:
                reviews = int(product['review_count'])
                if reviews < self.min_reviews:
                    issues.append(f"Review count below minimum threshold ({self.min_reviews})")
            except (ValueError, AttributeError):
                issues.append("Invalid review count format")

        # Validate image URL
        if 'image_url' in product:
            img_url = product['image_url']
            if not img_url.startswith('http'):
                issues.append("Invalid image URL")
            if not any(ext in img_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                issues.append("Image URL missing image extension")

        # Validate product URL
        if 'product_url' in product:
            prod_url = product['product_url']
            if not prod_url.startswith('http'):
                issues.append("Invalid product URL")
            if 'amazon' not in prod_url.lower():
                issues.append("Product URL not from Amazon")

        # Validate ASIN
        if 'asin' in product:
            asin = product['asin']
            if len(asin) != 10:
                issues.append("Invalid ASIN length (should be 10 characters)")

        is_valid = len(issues) == 0

        return is_valid, issues

    async def validate_input(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input parameters"""
        if 'products' not in task:
            return {'valid': False, 'error': 'Missing products'}

        products = task['products']
        if not isinstance(products, list):
            return {'valid': False, 'error': 'Products must be a list'}

        if len(products) == 0:
            return {'valid': False, 'error': 'Empty products list'}

        return {'valid': True}

    async def validate_output(self, result: Any) -> Dict[str, Any]:
        """Validate output result"""
        if not isinstance(result, dict):
            return {'valid': False, 'error': 'Result must be a dictionary'}

        if 'valid_products' not in result:
            return {'valid': False, 'error': 'Missing valid_products in result'}

        if 'report' not in result:
            return {'valid': False, 'error': 'Missing report in result'}

        return {'valid': True}
