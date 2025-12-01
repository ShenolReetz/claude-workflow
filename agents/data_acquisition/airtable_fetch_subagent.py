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
from agents.utils.airtable_client import AirtableClient


class AirtableFetchSubAgent(BaseSubAgent):
    """
    Handles all Airtable operations:
    - Fetch pending titles
    - Save product data
    - Update record status

    Uses the mcp__airtable MCP tools directly
    """

    def __init__(self, name: str, config: Dict[str, Any], parent_agent_id: str = None):
        super().__init__(name, config, parent_agent_id)

        # Store Airtable configuration
        self.api_key = config.get('airtable_api_key')
        self.base_id = config.get('airtable_base_id', 'appTtNBJ8dAnjvkPP')
        self.table_id = config.get('airtable_table_id', 'tblhGDEW6eUbmaYZx')
        self.table_name = config.get('airtable_table_name', 'Video Titles')

        # Initialize Airtable client
        self.airtable = AirtableClient(self.api_key, self.base_id, self.table_id)

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
        self.logger.info("📥 Fetching pending title from Airtable...")

        try:
            # Fetch pending records sorted by ID (oldest first)
            records = self.airtable.list_records(
                formula="Status = 'Pending'",
                max_records=1,
                sort=['ID']  # Ascending by default
            )

            if not records or len(records) == 0:
                self.logger.warning("⚠️  No pending titles found")
                return None

            record = records[0]
            record_id = record['id']
            fields = record['fields']

            self.logger.info(f"✅ Fetched record: {record_id} - {fields.get('Title', 'Untitled')}")

            # Update status to 'Processing' immediately
            self._update_status(record_id, 'Processing')

            return {
                'record_id': record_id,
                'title': fields.get('Title', ''),
                'notes': fields.get('VideoDescription', ''),
                'created_time': fields.get('ID', 0)
            }

        except Exception as e:
            self.logger.error(f"❌ Airtable fetch failed: {e}")
            raise

    def _update_status(self, record_id: str, status: str):
        """Update record status in Airtable"""
        try:
            self.airtable.update_record(record_id, {'Status': status})
            self.logger.info(f"✅ Updated status to '{status}' for record {record_id}")

        except Exception as e:
            self.logger.warning(f"⚠️  Failed to update status: {e}")

    async def _save_products(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Save product data to Airtable"""
        record_id = task.get('record_id')
        products = task.get('products', [])

        if not record_id or not products:
            raise ValueError("Missing record_id or products")

        self.logger.info(f"💾 Saving {len(products)} products to Airtable...")

        try:
            # Build fields dictionary for all 5 products
            fields = {}

            for i, product in enumerate(products[:5], 1):
                # Product fields (8 fields per product = 40 total)
                prefix = f"ProductNo{i}"

                fields[f"{prefix}Title"] = product.get('title', '')
                fields[f"{prefix}Description"] = product.get('description', '')
                fields[f"{prefix}Photo"] = product.get('image_url', '')
                fields[f"{prefix}Price"] = float(product.get('price', 0))
                fields[f"{prefix}Rating"] = float(product.get('rating', 0))
                fields[f"{prefix}Reviews"] = int(product.get('review_count', 0))
                fields[f"{prefix}AffiliateLink"] = product.get('product_url', '')

                # Status fields - set to "Ready" after saving
                fields[f"{prefix}TitleStatus"] = "Ready"
                fields[f"{prefix}DescriptionStatus"] = "Ready"
                fields[f"{prefix}PhotoStatus"] = "Ready"

            # Update Airtable record with all product data
            self.airtable.update_record(record_id, fields)

            self.logger.info(f"✅ Saved {len(products)} products to Airtable ({len(fields)} fields updated)")

            return {
                'record_id': record_id,
                'products_saved': len(products),
                'fields_updated': len(fields)
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
