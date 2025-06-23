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

print("🔍 Getting ALL records to see all available fields...")
try:
    # Get more records to see all possible fields
    records = airtable.get_all(maxRecords=10)
    
    all_fields = set()
    for record in records:
        all_fields.update(record['fields'].keys())
    
    print(f"📋 Found {len(all_fields)} unique fields across {len(records)} records:")
    for field in sorted(all_fields):
        print(f"   - {field}")
    
    # Check specifically for ProductNo fields
    product_fields = [f for f in all_fields if 'ProductNo' in f or 'Product' in f]
    print(f"\n🎯 Product-related fields ({len(product_fields)}):")
    for field in sorted(product_fields):
        print(f"   - {field}")
        
    # Test updating one field to see what happens
    if records:
        record_id = records[0]['id']
        print(f"\n🧪 Testing update on record: {record_id}")
        
        # Try to update KeyWords field (we know this exists)
        try:
            airtable.update(record_id, {'KeyWords': 'test, keywords, from, api'})
            print("✅ Update test successful!")
        except Exception as e:
            print(f"❌ Update test failed: {e}")
            
except Exception as e:
    print(f"❌ Error: {e}")
