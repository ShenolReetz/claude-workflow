"""
Airtable Fetch SubAgent
========================
Fetches pending titles from Airtable and saves product data.
"""

import sys
import asyncio
from typing import Dict, Any

sys.path.append('/home/claude-workflow')

from agents.base_subagent import BaseSubAgent
from mcp_servers.production_airtable_server import ProductionAirtableMCPServer


class AirtableFetchSubAgent(BaseSubAgent):
    """
    Handles all Airtable operations:
    - Fetch pending titles
    - Save product data
    - Update record status
    """

    def __init__(self, name: str, config: Dict[str, Any], parent_agent_id: str = None):
        super().__init__(name, config, parent_agent_id)

        # Initialize Airtable MCP server
        self.airtable = ProductionAirtableMCPServer(
            api_key=config.get('airtable_api_key'),
            base_id=config.get('airtable_base_id'),
            table_id=config.get('airtable_table_id')
        )

    async def execute_task(self, task: Dict[str, Any]) -> Any:
        """
        Execute Airtable operation

        Args:
            task: Task with operation type ('fetch' or 'save')

        Returns:
            Operation result
        """
        operation = task.get('operation', 'fetch')

        if operation == 'fetch':
            return await self._fetch_pending_title()

        elif operation == 'save':
            return await self._save_products(task)

        else:
            # Default: fetch pending title
            return await self._fetch_pending_title()

    async def _fetch_pending_title(self) -> Dict[str, Any]:
        """Fetch one pending title from Airtable"""
        self.logger.info("📥 Fetching pending title...")

        try:
            # Get records with status='pending'
            records = await self.airtable.get_records_by_status('pending', limit=1)

            if not records:
                raise ValueError("No pending titles found in Airtable")

            record = records[0]

            return {
                'record_id': record['id'],
                'title': record['fields'].get('Title', ''),
                'notes': record['fields'].get('Notes', ''),
                'created_time': record.get('createdTime', '')
            }

        except Exception as e:
            self.logger.error(f"❌ Airtable fetch failed: {e}")
            raise

    async def _save_products(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Save product data to Airtable"""
        record_id = task.get('record_id')
        products = task.get('products', [])

        if not record_id or not products:
            raise ValueError("Missing record_id or products")

        self.logger.info(f"💾 Saving {len(products)} products to Airtable...")

        try:
            # Prepare product data fields
            fields = {
                'Status': 'Data Scraped',
                'ProductCount': len(products),
            }

            # Add product-specific fields
            for i, product in enumerate(products[:5], 1):  # Max 5 products
                fields[f'Product{i}Title'] = product.get('title', '')
                fields[f'Product{i}Price'] = product.get('price', '')
                fields[f'Product{i}Rating'] = float(product.get('rating', 0))
                fields[f'Product{i}Reviews'] = int(product.get('review_count', 0))
                fields[f'Product{i}Image'] = product.get('image_url', '')
                fields[f'Product{i}URL'] = product.get('product_url', '')
                fields[f'Product{i}ASIN'] = product.get('asin', '')

            # Update record
            await self.airtable.update_record(record_id, fields)

            return {
                'record_id': record_id,
                'products_saved': len(products)
            }

        except Exception as e:
            self.logger.error(f"❌ Airtable save failed: {e}")
            raise

    async def validate_input(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input parameters"""
        operation = task.get('operation', 'fetch')

        if operation == 'save':
            if 'record_id' not in task:
                return {'valid': False, 'error': 'Missing record_id'}
            if 'products' not in task:
                return {'valid': False, 'error': 'Missing products'}

        return {'valid': True}

    async def validate_output(self, result: Any) -> Dict[str, Any]:
        """Validate output result"""
        if isinstance(result, dict):
            if 'record_id' in result or 'title' in result:
                return {'valid': True}

        return {'valid': False, 'error': 'Invalid result format'}
