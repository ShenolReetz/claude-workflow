#!/usr/bin/env python3
"""
Test Amazon Affiliate MCP Server - Hardcoded responses for testing
Purpose: Test affiliate link generation without consuming API tokens
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestAmazonAffiliateMCPServer:
    """Test Amazon Affiliate MCP Server with hardcoded responses"""
    
    def __init__(self, affiliate_tag: str):
        self.affiliate_tag = affiliate_tag
        logger.info("🧪 Test Amazon Affiliate Server initialized")
    
    async def generate_affiliate_link(self, asin: str) -> Dict[str, Any]:
        """Return hardcoded affiliate link for testing"""
        
        logger.info(f"🧪 Test: Generating affiliate link for ASIN '{asin}' (hardcoded)")
        
        # Generate test affiliate link
        test_affiliate_link = f"https://amazon.com/dp/{asin}?tag={self.affiliate_tag}&ref=test_affiliate"
        
        logger.info(f"✅ Test: Generated affiliate link")
        
        return {
            'success': True,
            'affiliate_link': test_affiliate_link,
            'asin': asin,
            'affiliate_tag': self.affiliate_tag,
            'test_mode': True,
            'api_calls_used': 0
        }