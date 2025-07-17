#!/usr/bin/env python3
"""
Populate the ID column with sequential numbers from 1 to total titles (top to bottom)
"""

import asyncio
import json
from typing import Dict
from mcp_servers.Test_airtable_server import AirtableMCPServer

class IDPopulator:
    """Populate ID column with sequential numbers"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.airtable_server = AirtableMCPServer(
            api_key=config['airtable_api_key'],
            base_id=config['airtable_base_id'],
            table_name=config['airtable_table_name']
        )
    
    async def populate_id_column(self):
        """Populate the ID column with sequential numbers from 1 to total"""
        print("🔢 Starting to populate ID column with sequential numbers...")
        
        try:
            # Get all records in natural order (top to bottom)
            print("📋 Fetching all records from Airtable...")
            all_records = self.airtable_server.airtable.get_all()
            
            if not all_records:
                print("❌ No records found")
                return
            
            print(f"✅ Found {len(all_records)} total records")
            
            # Update each record with its sequential ID (1, 2, 3, ...)
            batch_size = 10  # Process in small batches to avoid API limits
            updated_count = 0
            
            for i in range(0, len(all_records), batch_size):
                batch = all_records[i:i+batch_size]
                
                print(f"📝 Processing batch {i//batch_size + 1}: records {i+1} to {min(i+batch_size, len(all_records))}")
                
                for j, record in enumerate(batch):
                    record_id = record['id']
                    sequential_id = i + j + 1  # Sequential number starting from 1
                    
                    try:
                        # Update the ID field with the sequential number
                        await self.airtable_server.update_record(record_id, {'ID': sequential_id})
                        updated_count += 1
                        
                        # Show progress for some records
                        if sequential_id <= 10 or sequential_id % 100 == 0:
                            title = record['fields'].get('Title', 'No Title')[:50]
                            print(f"  ✅ Record #{sequential_id}: {title}...")
                        
                    except Exception as e:
                        print(f"  ❌ Error updating record {record_id} (ID #{sequential_id}): {e}")
                
                # Show batch completion
                if (i + batch_size) % 100 == 0 or (i + batch_size) >= len(all_records):
                    print(f"  Batch complete: {min(i+batch_size, len(all_records))}/{len(all_records)} records processed")
            
            print(f"\n✅ ID column population complete!")
            print(f"📊 Total records updated: {updated_count}/{len(all_records)}")
            print(f"🔢 ID range: 1 to {len(all_records)}")
            
            # Verify a few records
            await self.verify_id_population()
            
        except Exception as e:
            print(f"❌ Error populating ID column: {e}")
            import traceback
            traceback.print_exc()
    
    async def verify_id_population(self):
        """Verify the ID population worked correctly"""
        print("\n🔍 Verifying ID population...")
        
        try:
            # Get first few records to verify
            sample_records = self.airtable_server.airtable.get_all(max_records=5)
            
            print("📋 Sample of ID assignments:")
            for record in sample_records:
                record_id = record['id']
                id_value = record['fields'].get('ID', 'NOT SET')
                title = record['fields'].get('Title', 'No Title')[:50]
                
                print(f"  Record {record_id}: ID = {id_value}, Title = {title}...")
            
            print("✅ ID verification complete")
            
        except Exception as e:
            print(f"❌ Error verifying ID population: {e}")

async def main():
    """Main function to run the ID population"""
    print("🚀 Starting ID Column Population")
    print("🔢 Will assign sequential numbers 1, 2, 3... from top to bottom")
    
    # Load configuration
    try:
        with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return
    
    # Initialize populator
    populator = IDPopulator(config)
    
    try:
        # Populate ID column
        await populator.populate_id_column()
        
        print(f"\n🎯 ID COLUMN POPULATION COMPLETE!")
        print(f"✅ All titles now have sequential ID numbers")
        print(f"📝 Ready for TitleID-based selection in workflows")
        
    except Exception as e:
        print(f"❌ Error in ID population: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())