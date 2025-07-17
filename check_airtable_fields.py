#!/usr/bin/env python3
"""
Check Airtable fields to find the sequential ID field
"""

import asyncio
import json
from mcp_servers.Test_airtable_server import AirtableMCPServer

async def check_airtable_fields():
    """Check what fields are available in Airtable records"""
    print("🔍 Checking Airtable fields to find sequential ID...")
    
    # Load configuration
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    # Initialize server
    server = AirtableMCPServer(
        api_key=config['airtable_api_key'],
        base_id=config['airtable_base_id'],
        table_name=config['airtable_table_name']
    )
    
    try:
        # Get all pending records to examine fields
        all_records = server.airtable.get_all(formula="Status = 'Pending'", max_records=5)
        
        if all_records:
            print(f"✅ Found {len(all_records)} pending records")
            
            for i, record in enumerate(all_records[:3]):
                print(f"\n--- Record {i+1} ---")
                print(f"Record ID: {record['id']}")
                print(f"Available fields: {list(record['fields'].keys())}")
                
                # Show first few field values
                for field_name, field_value in list(record['fields'].items())[:10]:
                    if isinstance(field_value, str) and len(field_value) > 50:
                        print(f"  {field_name}: {field_value[:50]}...")
                    else:
                        print(f"  {field_name}: {field_value}")
                        
                # Look for potential ID fields
                potential_id_fields = [k for k in record['fields'].keys() if 'id' in k.lower() or 'number' in k.lower() or k.isdigit()]
                if potential_id_fields:
                    print(f"  Potential ID fields: {potential_id_fields}")
        else:
            print("❌ No pending records found")
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_airtable_fields())