#!/usr/bin/env python3
"""
Test the Airtable keywords update method
"""

import asyncio
import json
import sys
sys.path.append('/home/claude-workflow')

from mcp_servers.airtable_server import AirtableMCPServer

async def test_airtable_keywords():
    """Test the Airtable keywords update method"""
    
    # Load config
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    # Initialize Airtable
    airtable = AirtableMCPServer(
        config['airtable_api_key'],
        config['airtable_base_id'],
        config['airtable_table_name']
    )
    
    print("🔍 Testing Airtable keywords method...")
    
    # Check if method exists
    if hasattr(airtable, 'update_multi_platform_keywords'):
        print("✅ Method update_multi_platform_keywords exists")
    else:
        print("❌ Method update_multi_platform_keywords does NOT exist")
        print("📋 Available methods:")
        methods = [method for method in dir(airtable) if not method.startswith('_')]
        for method in methods:
            print(f"   - {method}")
        return False
    
    # Test data
    test_keywords = {
        'youtube': ['gaming headsets', 'best headsets 2025', 'top gaming gear'],
        'instagram': ['#gaming', '#headsets', '#tech', '#gamingsetup'],
        'tiktok': ['gaming finds', 'tech haul', 'must have'],
        'wordpress': ['best gaming headsets 2025', 'gaming headset reviews'],
        'universal': ['gaming headsets', 'wireless headsets', 'gaming audio']
    }
    
    # Test with specific record
    test_record_id = "rec00Yb60qB6jOXSE"
    
    try:
        result = await airtable.update_multi_platform_keywords(test_record_id, test_keywords)
        print(f"✅ Method executed successfully: {result}")
        return True
    except Exception as e:
        print(f"❌ Method failed: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_airtable_keywords())
    if result:
        print("\n🎉 Airtable keywords method working!")
    else:
        print("\n💥 Airtable keywords method failed")