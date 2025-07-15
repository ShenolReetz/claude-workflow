#!/usr/bin/env python3
"""
Update Airtable with a test record that should work
"""

import asyncio
import json
import sys
sys.path.append('/home/claude-workflow')

from mcp_servers.airtable_server import AirtableMCPServer

async def update_test_record():
    """Update a test record in Airtable"""
    
    # Load config
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    # Initialize Airtable
    airtable = AirtableMCPServer(
        config['airtable_api_key'],
        config['airtable_base_id'],
        config['airtable_table_name']
    )
    
    # Working title that we tested
    working_title = "🔥 TOP 5 Gaming Headsets That Will Blow Your Mind! 🎮"
    
    print(f"🔄 Updating test record with working title...")
    
    # Get the current pending title record
    pending_title = await airtable.get_pending_titles()
    
    if pending_title:
        record_id = pending_title['record_id']
        print(f"📋 Found record ID: {record_id}")
        
        # Update the record with working title and reset status
        await airtable.update_record(record_id, {
            'VideoTitle': working_title,
            'Status': 'Pending',
            'ProductNo1Title': '',
            'ProductNo2Title': '',
            'ProductNo3Title': '',
            'ProductNo4Title': '',
            'ProductNo5Title': ''
        })
        
        print(f"✅ Updated record with working title: {working_title}")
        print(f"🎯 Status set to: Pending")
        print(f"📝 Product fields cleared for fresh test")
        
        return True
    else:
        print("❌ No pending title found to update")
        return False

if __name__ == "__main__":
    result = asyncio.run(update_test_record())
    if result:
        print("\n🎉 Test record updated successfully!")
    else:
        print("\n💥 Failed to update test record")