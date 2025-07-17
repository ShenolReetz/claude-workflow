#!/usr/bin/env python3

import asyncio
import json
import sys
import os
sys.path.append('/home/claude-workflow')

from mcp_servers.Test_default_text_validation_manager import TestDefaultTextValidationManager
from mcp_servers.Test_airtable_server import AirtableMCPServer

async def test_status_update():
    # Load API keys
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        api_keys = json.load(f)
    
    # Initialize components
    airtable_server = AirtableMCPServer(
        api_key=api_keys['airtable_api_key'],
        base_id=api_keys['airtable_base_id'],
        table_name=api_keys['airtable_table_name']
    )
    
    validation_manager = TestDefaultTextValidationManager()
    
    # Get a test record to work with
    print('🔍 Fetching test record...')
    records = await airtable_server.get_all_records()
    if not records:
        print('❌ No records found in Airtable')
        return
    
    test_record = records[0]
    record_id = test_record['id']
    title = test_record['fields'].get('Title', 'Unknown')
    
    print(f'📋 Testing with record: {record_id}')
    print(f'📝 Title: {title}')
    
    # Test the status update
    print('⏱️ Testing text validation status update...')
    result = await validation_manager.populate_default_validation_status(
        airtable_server,
        record_id
    )
    
    print(f'Result: {result}')
    
    if result.get('success'):
        print(f'✅ SUCCESS: Updated {result.get("columns_updated", 0)} columns')
        print(f'📊 Status value: {result.get("status_value", "Unknown")}')
        
        # Verify the update by fetching the record
        print('🔍 Verifying update...')
        updated_record = await airtable_server.get_record_by_id(record_id)
        if updated_record:
            fields = updated_record.get('fields', {})
            status_columns = validation_manager.validation_status_columns
            
            print('📊 Status column values:')
            all_correct = True
            for col in status_columns:
                value = fields.get(col, 'MISSING')
                expected = 'Ready'
                status = '✅' if value == expected else '❌'
                print(f'   {col}: {value} {status}')
                if value != expected:
                    all_correct = False
            
            if all_correct:
                print('🎉 All status columns correctly set to "Ready"!')
            else:
                print('❌ Some status columns have incorrect values')
                
            # Check VideoProductionRDY column
            video_production_status = fields.get('VideoProductionRDY', 'MISSING')
            print(f'\n🎬 VideoProductionRDY: {video_production_status}')
            
        else:
            print('❌ Could not fetch updated record')
    else:
        print(f'❌ FAILED: {result.get("error", "Unknown error")}')

if __name__ == "__main__":
    asyncio.run(test_status_update())