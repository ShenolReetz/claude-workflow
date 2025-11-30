"""
Data Acquisition Agent
======================
Main agent that manages all data fetching and validation tasks.
"""

import asyncio
import logging
from typing import Dict, Any, List
import sys

sys.path.append('/home/claude-workflow')

from agents.base_agent import BaseAgent
from .airtable_fetch_subagent import AirtableFetchSubAgent
from .amazon_scraper_subagent import AmazonScraperSubAgent
from .category_extractor_subagent import CategoryExtractorSubAgent
from .product_validator_subagent import ProductValidatorSubAgent


class DataAcquisitionAgent(BaseAgent):
    """
    Manages all data acquisition tasks:
    - Fetching titles from Airtable
    - Scraping Amazon products
    - Extracting categories
    - Validating product data
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__("data_acquisition", config)

        # Initialize sub-agents
        self.sub_agents = [
            AirtableFetchSubAgent("airtable_fetch", config, self.agent_id),
            AmazonScraperSubAgent("amazon_scraper", config, self.agent_id),
            CategoryExtractorSubAgent("category_extractor", config, self.agent_id),
            ProductValidatorSubAgent("product_validator", config, self.agent_id),
        ]

        self.logger.info(f"✅ DataAcquisitionAgent initialized with {len(self.sub_agents)} sub-agents")

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute data acquisition task

        Args:
            task: Task parameters with 'phase' key

        Returns:
            Data acquisition results
        """
        phase = task.get('phase', '')
        self.logger.info(f"📋 Executing data acquisition phase: {phase}")

        try:
            if phase == 'fetch_title':
                return await self._fetch_title(task)

            elif phase == 'scrape_amazon':
                return await self._scrape_products(task)

            elif phase == 'extract_category':
                return await self._extract_category(task)

            elif phase == 'validate_products':
                return await self._validate_products(task)

            elif phase == 'save_to_airtable':
                return await self._save_to_airtable(task)

            else:
                raise ValueError(f"Unknown phase: {phase}")

        except Exception as e:
            self.logger.error(f"❌ Data acquisition failed: {e}")
            raise

    async def _fetch_title(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch pending title from Airtable"""
        self.logger.info("📥 Fetching pending title from Airtable...")

        result = await self.delegate_to_subagent('AirtableFetchSubAgent', task)

        if not result['success']:
            raise RuntimeError(f"Failed to fetch title: {result.get('error')}")

        return {
            'record_id': result['result']['record_id'],
            'title': result['result']['title'],
            'status': 'fetched'
        }

    async def _scrape_products(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Scrape Amazon products"""
        self.logger.info("🔍 Scraping Amazon products...")

        title = task.get('params', {}).get('fetch_title', {}).get('title')
        if not title:
            raise ValueError("No title provided for scraping")

        scrape_task = {
            **task,
            'title': title,
            'num_products': 5
        }

        result = await self.delegate_to_subagent('AmazonScraperSubAgent', scrape_task)

        if not result['success']:
            raise RuntimeError(f"Failed to scrape products: {result.get('error')}")

        return {
            'products': result['result']['products'],
            'count': len(result['result']['products']),
            'status': 'scraped'
        }

    async def _extract_category(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Extract product category from title"""
        self.logger.info("🏷️  Extracting category...")

        title = task.get('params', {}).get('fetch_title', {}).get('title')
        if not title:
            raise ValueError("No title provided for category extraction")

        extract_task = {
            **task,
            'title': title
        }

        result = await self.delegate_to_subagent('CategoryExtractorSubAgent', extract_task)

        if not result['success']:
            raise RuntimeError(f"Failed to extract category: {result.get('error')}")

        return {
            'category': result['result']['category'],
            'keywords': result['result'].get('keywords', []),
            'status': 'extracted'
        }

    async def _validate_products(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Validate scraped products"""
        self.logger.info("✅ Validating products...")

        products = task.get('params', {}).get('scrape_amazon', {}).get('products', [])
        if not products:
            raise ValueError("No products provided for validation")

        validate_task = {
            **task,
            'products': products
        }

        result = await self.delegate_to_subagent('ProductValidatorSubAgent', validate_task)

        if not result['success']:
            raise RuntimeError(f"Failed to validate products: {result.get('error')}")

        return {
            'valid_products': result['result']['valid_products'],
            'validation_report': result['result']['report'],
            'status': 'validated'
        }

    async def _save_to_airtable(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Save validated products to Airtable"""
        self.logger.info("💾 Saving products to Airtable...")

        record_id = task.get('params', {}).get('fetch_title', {}).get('record_id')
        products = task.get('params', {}).get('validate_products', {}).get('valid_products', [])

        if not record_id or not products:
            raise ValueError("Missing record_id or products for saving")

        save_task = {
            **task,
            'record_id': record_id,
            'products': products
        }

        # Use Airtable subagent to save
        result = await self.delegate_to_subagent('AirtableFetchSubAgent', save_task)

        if not result['success']:
            raise RuntimeError(f"Failed to save to Airtable: {result.get('error')}")

        return {
            'record_id': record_id,
            'saved_products': len(products),
            'status': 'saved'
        }

    def get_capabilities(self) -> List[str]:
        """Return list of capabilities"""
        return [
            'fetch_title',
            'scrape_amazon',
            'extract_category',
            'validate_products',
            'save_to_airtable'
        ]
