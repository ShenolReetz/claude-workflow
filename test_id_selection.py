#!/usr/bin/env python3
"""
Test ID-based title selection
"""

import asyncio
import json
from mcp_servers.Test_airtable_server import AirtableMCPServer

async def test_id_selection():
    """Test the ID-based title selection"""
    print("🧪 Testing ID-based title selection...")
    
    # Load configuration
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    # Initialize server
    server = AirtableMCPServer(
        api_key=config['airtable_api_key'],
        base_id=config['airtable_base_id'],
        table_name=config['airtable_table_name']
    )
    
    # Test getting pending titles
    print("\n🔍 Testing get_pending_titles with ID-based selection...")
    
    for i in range(3):
        print(f"\n--- Test {i+1} ---")
        pending_title = await server.get_pending_titles()
        
        if pending_title:
            print(f"✅ Found pending title:")
            print(f"   ID Number: {pending_title.get('id_number', 'N/A')}")
            print(f"   Record ID: {pending_title['record_id']}")
            print(f"   Title: {pending_title['title'][:60]}...")
            print(f"   Status: {pending_title['status']}")
        else:
            print("❌ No pending titles found")
            break
    
    print("\n🎯 ID-based selection test complete!")

if __name__ == "__main__":
    asyncio.run(test_id_selection())