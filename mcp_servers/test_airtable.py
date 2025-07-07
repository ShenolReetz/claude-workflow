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

print("Testing basic Airtable connection...")
try:
    # Try to get all records (first 3)
    records = airtable.get_all(maxRecords=3)
    print(f"✅ Connected! Found {len(records)} records")
    
    if records:
        print("First record fields:", list(records[0]['fields'].keys()))
        print("First record data:", records[0]['fields'])
    
except Exception as e:
    print(f"❌ Connection failed: {e}")
