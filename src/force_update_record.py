#!/usr/bin/env python3
"""
Force update the record to use gaming headsets title
"""

import asyncio
import json
import sys
sys.path.append('/home/claude-workflow')

from mcp_servers.airtable_server import AirtableMCPServer

async def force_update_record():
    """Force update the record"""
    
    # Load config
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    # Initialize Airtable
    airtable = AirtableMCPServer(
        config['airtable_api_key'],
        config['airtable_base_id'],
        config['airtable_table_name']
    )
    
    # Force update the specific record
    record_id = "rec00Yb60qB6jOXSE"
    working_title = "🔥 TOP 5 Gaming Headsets That Will Blow Your Mind! 🎮"
    
    print(f"🔄 Force updating record {record_id}...")
    
    try:
        # Update the record
        await airtable.update_record(record_id, {
            'VideoTitle': working_title,
            'Status': 'Pending'
        })
        
        print(f"✅ Updated record with: {working_title}")
        
        # Verify the update
        record = await airtable.get_record_by_id(record_id)
        if record:
            current_title = record.get('fields', {}).get('VideoTitle', 'N/A')
            current_status = record.get('fields', {}).get('Status', 'N/A')
            print(f"📋 Verified title: {current_title}")
            print(f"📋 Verified status: {current_status}")
            
            return current_title == working_title
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(force_update_record())
    if result:
        print("\n🎉 Record updated successfully!")
    else:
        print("\n💥 Failed to update record")