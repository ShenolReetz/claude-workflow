import json
from airtable import Airtable

# Load config
with open('/app/config/api_keys.json', 'r') as f:
    config = json.load(f)

# Initialize Airtable
airtable = Airtable(
    config['airtable_base_id'], 
    config['airtable_table_name'], 
    config['airtable_api_key']
)

print(f"🔍 Connected to:")
print(f"   Base ID: {config['airtable_base_id']}")
print(f"   Table: {config['airtable_table_name']}")

try:
    # Get the first record
    records = airtable.get_all(maxRecords=1)
    if records:
        record_id = records[0]['id']
        
        print(f"\n🧪 Testing field creation on record: {record_id}")
        
        # Try to update ProductNo5Title field
        test_fields = {
            'ProductNo5Title': 'Test Product 5',
            'ProductNo4Title': 'Test Product 4', 
            'ProductNo3Title': 'Test Product 3',
            'ProductNo2Title': 'Test Product 2',
            'ProductNo1Title': 'Test Product 1'
        }
        
        for field_name, value in test_fields.items():
            try:
                airtable.update(record_id, {field_name: value})
                print(f"✅ Successfully updated {field_name}")
            except Exception as e:
                print(f"❌ Failed to update {field_name}: {e}")
                
        # Now get the record again to see if fields appear
        print(f"\n🔍 Checking fields after update...")
        updated_records = airtable.get_all(maxRecords=1)
        if updated_records:
            all_fields = list(updated_records[0]['fields'].keys())
            print(f"📋 Fields after update ({len(all_fields)}):")
            for field in sorted(all_fields):
                print(f"   - {field}")
                
except Exception as e:
    print(f"❌ Error: {e}")
