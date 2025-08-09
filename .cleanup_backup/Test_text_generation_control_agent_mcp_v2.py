#!/usr/bin/env python3
"""
Test Text Generation Control Agent MCP V2
Hardcoded responses for testing - no API usage
"""

import asyncio
import json
import logging
from typing import Dict, List
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))

# Import test servers
from mcp_servers.Test_text_generation_control_server import TestTextGenerationControlMCPServer
from mcp_servers.Test_airtable_server import TestAirtableMCPServer
from mcp_servers.Test_content_generation_server import TestContentGenerationMCPServer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestTextGenerationControlAgentMCP:
    """Test Agent with hardcoded responses and automatic success"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.control_server = TestTextGenerationControlMCPServer(config)
        self.airtable_server = TestAirtableMCPServer(
            api_key=config.get('airtable_api_key', 'test-key'),
            base_id=config.get('airtable_base_id', 'test-base'),
            table_name=config.get('airtable_table_name', 'test-table')
        )
        self.content_server = TestContentGenerationMCPServer(
            anthropic_api_key=config.get('anthropic_api_key', 'test-key')
        )
        
        print("🧪 TEST MODE: Text Generation Control Agent using hardcoded responses")
        logger.info("🧪 Test Text Generation Control Agent initialized")
        
    async def control_validate_and_regenerate(self, record_id: str, max_attempts: int = 3) -> Dict:
        """
        Test version - always succeeds with hardcoded validation results
        """
        logger.info(f"🎮 Test: Text Control Agent starting validation loop for record {record_id}")
        print(f"🧪 TEST: Starting text validation for record {record_id}")
        
        attempt = 1  # Always succeed on first attempt in test mode
        
        # Simulate getting record data
        print(f"🧪 TEST: Simulating record retrieval for {record_id}")
        
        # Hardcoded successful validation
        test_products = [
            {
                'number': 1,
                'title': 'Premium Gaming Headset with Crystal Clear Audio',
                'description': 'Experience immersive gaming with our top-rated headset featuring 7.1 surround sound.'
            },
            {
                'number': 2,
                'title': 'Professional Wireless Gaming Headset',
                'description': 'Enjoy lag-free gaming with our premium wireless headset and 20-hour battery life.'
            },
            {
                'number': 3,
                'title': 'RGB LED Gaming Headset with Microphone',
                'description': 'Stand out with customizable RGB lighting and studio-quality microphone.'
            },
            {
                'number': 4,
                'title': 'Comfortable Over-Ear Gaming Headset',
                'description': 'Game for hours in comfort with our ergonomically designed cushioned headset.'
            },
            {
                'number': 5,
                'title': 'Budget-Friendly Gaming Headset',
                'description': 'Get great gaming audio without breaking the bank with this value headset.'
            }
        ]
        
        # Test validation (always passes)
        print(f"🧪 TEST: Running validation on {len(test_products)} products")
        validation_result = await self.control_server.check_countdown_products(
            test_products, ['gaming', 'headset', 'audio'], 'Electronics'
        )
        
        # Always succeed in test mode
        logger.info("✅ Test: All products passed validation!")
        print("🧪 TEST: All products validated successfully")
        
        # Simulate Airtable update
        await self.airtable_server.update_record(record_id, {
            'TextControlStatus': 'Validated',
            'GenerationAttempts': attempt
        })
        
        return {
            'success': True,
            'all_valid': True,
            'attempts': attempt,
            'validation_results': validation_result,
            'test_mode': True,
            'api_usage': 0  # No API tokens used in test mode
        }
    
    async def validate_text_lengths(self, record_id: str) -> Dict:
        """Test version - validate text lengths with hardcoded success"""
        logger.info(f"📏 Test: Validating text lengths for record {record_id}")
        print(f"🧪 TEST: Validating text lengths for record {record_id}")
        
        # Hardcoded successful validation results
        validation_results = {
            'VideoTitle': {'length': 65, 'status': 'valid', 'max_length': 100},
            'VideoDescription': {'length': 145, 'status': 'valid', 'max_length': 200},
            'ProductNo1Title': {'length': 48, 'status': 'valid', 'max_length': 60},
            'ProductNo1Description': {'length': 85, 'status': 'valid', 'max_length': 100},
            'ProductNo2Title': {'length': 52, 'status': 'valid', 'max_length': 60},
            'ProductNo2Description': {'length': 78, 'status': 'valid', 'max_length': 100},
            'ProductNo3Title': {'length': 46, 'status': 'valid', 'max_length': 60},
            'ProductNo3Description': {'length': 92, 'status': 'valid', 'max_length': 100},
            'ProductNo4Title': {'length': 54, 'status': 'valid', 'max_length': 60},
            'ProductNo4Description': {'length': 88, 'status': 'valid', 'max_length': 100},
            'ProductNo5Title': {'length': 49, 'status': 'valid', 'max_length': 60},
            'ProductNo5Description': {'length': 82, 'status': 'valid', 'max_length': 100}
        }
        
        all_valid = True
        total_fields = len(validation_results)
        valid_fields = sum(1 for v in validation_results.values() if v['status'] == 'valid')
        
        logger.info(f"✅ Test: Text length validation complete - {valid_fields}/{total_fields} valid")
        print(f"🧪 TEST: Text lengths validated - {valid_fields}/{total_fields} fields valid")
        
        return {
            'success': True,
            'all_valid': all_valid,
            'validation_results': validation_results,
            'summary': {
                'total_fields': total_fields,
                'valid_fields': valid_fields,
                'invalid_fields': 0
            },
            'test_mode': True,
            'api_usage': 0
        }
    
    async def regenerate_invalid_texts(self, record_id: str, invalid_fields: List[str]) -> Dict:
        """Test version - simulate text regeneration with hardcoded success"""
        logger.info(f"🔄 Test: Regenerating {len(invalid_fields)} invalid texts for record {record_id}")
        print(f"🧪 TEST: Simulating text regeneration for {len(invalid_fields)} fields")
        
        # Simulate regeneration delay
        await asyncio.sleep(0.5)
        
        # Hardcoded regenerated content
        regenerated_content = {}
        for field in invalid_fields:
            if 'Title' in field:
                regenerated_content[field] = f"Optimized {field.replace('ProductNo', 'Product ')} Content"
            else:
                regenerated_content[field] = f"Regenerated description for {field} with perfect length and SEO optimization."
        
        # Update Airtable with new content
        await self.airtable_server.update_record(record_id, regenerated_content)
        
        logger.info(f"✅ Test: Successfully regenerated {len(regenerated_content)} fields")
        print(f"🧪 TEST: Regenerated {len(regenerated_content)} fields successfully")
        
        return {
            'success': True,
            'regenerated_fields': list(regenerated_content.keys()),
            'regenerated_content': regenerated_content,
            'test_mode': True,
            'api_usage': 0
        }
    
    async def full_text_validation_workflow(self, record_id: str) -> Dict:
        """Complete text validation workflow with hardcoded success"""
        logger.info(f"🚀 Test: Starting full text validation workflow for record {record_id}")
        print(f"🧪 TEST: Full text validation workflow starting")
        
        # Step 1: Validate text lengths
        length_validation = await self.validate_text_lengths(record_id)
        
        # Step 2: Check if regeneration needed (in test mode, always skip)
        if not length_validation['all_valid']:
            print(f"🧪 TEST: Would regenerate invalid fields, but skipping in test mode")
        
        # Step 3: Final quality check
        quality_check = await self.control_validate_and_regenerate(record_id)
        
        # Combine results
        workflow_result = {
            'success': True,
            'record_id': record_id,
            'length_validation': length_validation,
            'quality_validation': quality_check,
            'overall_status': 'validated',
            'total_attempts': 1,
            'test_mode': True,
            'api_usage': 0,
            'workflow_time': '2.5 seconds (simulated)'
        }
        
        logger.info(f"🎉 Test: Full text validation workflow completed successfully")
        print(f"🧪 TEST: Full text validation workflow completed - ✅ SUCCESS")
        
        return workflow_result

async def test_run_text_control_with_regeneration(record_data: Dict, config: Dict) -> Dict:
    """Test version of text control with hardcoded success"""
    print("🧪 Running test text control with regeneration (no API calls)")
    
    # Always return success with hardcoded data
    updated_record = record_data.copy()
    
    # Mark all status fields as "Ready" for testing
    status_fields = [
        'VideoTitleStatus', 'VideoDescriptionStatus',
        'ProductNo1TitleStatus', 'ProductNo1DescriptionStatus',
        'ProductNo2TitleStatus', 'ProductNo2DescriptionStatus', 
        'ProductNo3TitleStatus', 'ProductNo3DescriptionStatus',
        'ProductNo4TitleStatus', 'ProductNo4DescriptionStatus',
        'ProductNo5TitleStatus', 'ProductNo5DescriptionStatus'
    ]
    
    for field in status_fields:
        updated_record[field] = 'Ready'
    
    print("✅ All text validation passed - all content optimal for timing")
    
    return {
        'success': True,
        'updated_record': updated_record,
        'validation_results': {field: 'Ready' for field in status_fields},
        'regenerations_needed': 0,
        'total_validation_time': '0.1s',
        'api_calls_used': 0
    }

# Test function
if __name__ == "__main__":
    async def test_agent():
        config = {
            'anthropic_api_key': 'test-key',
            'airtable_api_key': 'test-key',
            'airtable_base_id': 'test-base',
            'airtable_table_name': 'test-table'
        }
        
        agent = TestTextGenerationControlAgentMCP(config)
        
        print("🧪 Testing Text Generation Control Agent")
        print("=" * 50)
        
        # Test full workflow
        result = await agent.full_text_validation_workflow('test-record-123')
        
        print(f"\n📊 Test Result: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
        print(f"🧪 API Usage: {result['api_usage']} tokens")
        print(f"⏱️ Workflow Time: {result['workflow_time']}")
        
    asyncio.run(test_agent())