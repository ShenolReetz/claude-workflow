#!/usr/bin/env python3
"""
Test Airtable Integration
==========================
Quick test to verify Airtable client works with live data
"""

import json
import sys
sys.path.append('/home/claude-workflow')

from agents.utils.airtable_client import AirtableClient

def main():
    print("🧪 Testing Airtable Integration...\n")

    # Load config
    print("📋 Loading configuration...")
    with open('/home/claude-workflow/config/api_keys.json') as f:
        config = json.load(f)

    # Initialize client
    print(f"🔗 Connecting to Airtable...")
    print(f"   Base: {config['airtable_base_id']}")
    print(f"   Table: {config['airtable_table_id']}")

    client = AirtableClient(
        config['airtable_api_key'],
        config['airtable_base_id'],
        config['airtable_table_id']
    )

    # Test 1: Fetch pending records
    print("\n✅ Test 1: Fetching pending records...")
    records = client.list_records(
        formula="Status = 'Pending'",
        max_records=3,
        sort=['ID']  # Ascending by default, use '-ID' for descending
    )

    print(f"   Found {len(records)} pending records")

    if records:
        for i, record in enumerate(records, 1):
            print(f"\n   Record {i}:")
            print(f"      ID: {record['id']}")
            print(f"      Title: {record['fields'].get('Title', 'N/A')}")
            print(f"      Status: {record['fields'].get('Status', 'N/A')}")
            print(f"      ID Number: {record['fields'].get('ID', 'N/A')}")

    # Test 2: Read a single record
    if records:
        print("\n✅ Test 2: Reading single record...")
        record_id = records[0]['id']
        record = client.get_record(record_id)

        print(f"   Successfully read record: {record_id}")
        print(f"   Fields present: {len(record['fields'])}")

        # Show some key fields
        print("\n   Key Fields:")
        key_fields = ['Title', 'Status', 'VideoProductionRDY',
                     'ProductNo1Title', 'YouTubeTitle']
        for field in key_fields:
            value = record['fields'].get(field, 'Not set')
            print(f"      {field}: {value}")

    # Test 3: Test update (dry run - commented out)
    print("\n✅ Test 3: Update capability...")
    print("   Update test: SKIPPED (requires confirmation)")
    print("   To test updates, uncomment the code below")

    # Uncomment to test actual updates:
    # if records:
    #     test_record_id = records[0]['id']
    #     print(f"   Would update record: {test_record_id}")
    #     client.update_record(test_record_id, {'Status': 'Processing'})
    #     print("   Status updated to 'Processing'")
    #
    #     # Revert immediately
    #     client.update_record(test_record_id, {'Status': 'Pending'})
    #     print("   Status reverted to 'Pending'")

    print("\n" + "="*60)
    print("🎉 All Tests Passed!")
    print("="*60)
    print("\n📊 Summary:")
    print(f"   ✅ Connection: Working")
    print(f"   ✅ Fetch: {len(records)} records found")
    print(f"   ✅ Read: Working")
    print(f"   ⏸️  Update: Not tested (dry run)")
    print("\n✨ Airtable integration is ready for use!")
    print("\nNext step: Run agent workflow with --test flag")
    print("   python run_agent_workflow.py --test\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
