#!/usr/bin/env python3
"""
Check which field is set as Primary in Airtable
"""

import asyncio
import json
from mcp_servers.Test_airtable_server import AirtableMCPServer

async def check_primary_field():
    """Check which field is the Primary field in Airtable"""
    print("🔍 Checking Airtable Primary field...")
    
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
        # Get a few pending records to examine
        all_records = server.airtable.get_all(formula="Status = 'Pending'", max_records=10)
        
        if all_records:
            print(f"✅ Found {len(all_records)} pending records")
            
            # Check for different field names
            field_tests = ['TitleID', 'ID', 'id', 'Title_ID', 'RecordID']
            
            print("\n🔍 Testing different field names:")
            for field_name in field_tests:
                values = []
                for record in all_records[:5]:
                    value = record['fields'].get(field_name, None)
                    if value is not None:
                        values.append(value)
                
                if values:
                    print(f"  ✅ {field_name}: Found values {values}")
                else:
                    print(f"  ❌ {field_name}: No values found")
            
            # Show the first record's complete structure
            print(f"\n📋 First record structure:")
            first_record = all_records[0]
            print(f"Record ID: {first_record['id']}")
            
            # Look specifically for ID-related fields
            id_fields = {}
            for field_name, field_value in first_record['fields'].items():
                if 'id' in field_name.lower() or isinstance(field_value, (int, float)):
                    id_fields[field_name] = field_value
            
            print(f"ID-related fields: {id_fields}")
            
            # Test sorting by ID field
            print(f"\n🔢 Testing sorting by ID field...")
            if 'ID' in first_record['fields']:
                # Sort records by ID
                def get_id(record):
                    id_value = record['fields'].get('ID', float('inf'))
                    return id_value if isinstance(id_value, (int, float)) else float('inf')
                
                sorted_records = sorted(all_records, key=get_id)
                
                print("Sorted records by ID:")
                for i, record in enumerate(sorted_records[:5]):
                    id_val = record['fields'].get('ID', 'N/A')
                    title_preview = record['fields'].get('Title', 'No Title')[:50]
                    print(f"  {i+1}. ID: {id_val} - {title_preview}...")
            else:
                print("❌ ID field not found for sorting test")
        
        else:
            print("❌ No pending records found")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_primary_field())