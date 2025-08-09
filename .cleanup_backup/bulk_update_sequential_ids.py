#!/usr/bin/env python3
"""
🚀 PRODUCTION WORKFLOW FILE - DO NOT DELETE 🚀
This file is part of the Production Flow system.
⚠️  DO NOT DELETE during cleanup phases - Required for production operations.

Bulk Update Airtable IDs to Sequential - Direct API Approach
Updates all records to have sequential IDs: 1, 2, 3, 4, 5... etc.

Purpose: Maintains clean sequential ID numbering for production workflow efficiency
Usage: Run when IDs become scattered or need reorganization
Status: Production-ready utility script
"""

import requests
import json
import time
from typing import List, Dict, Any

class AirtableBulkUpdater:
    def __init__(self):
        # Load configuration
        with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
            config = json.load(f)
        
        self.api_key = config['airtable_api_key']
        self.base_id = config['airtable_base_id']
        self.table_id = "tblhGDEW6eUbmaYZx"  # Use table ID instead of name
        self.base_url = f"https://api.airtable.com/v0/{self.base_id}/{self.table_id}"
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        print(f"🚀 Airtable Bulk ID Updater Initialized")
        print(f"📋 Base ID: {self.base_id}")
        print(f"🏠 Table ID: {self.table_id}")
    
    def get_all_records(self) -> List[Dict[str, Any]]:
        """Get all records from the table"""
        all_records = []
        offset = None
        page = 1
        
        print(f"\n📥 Fetching all records from Airtable...")
        
        while True:
            # Build URL with parameters
            params = {
                'sort[0][field]': 'ID',
                'sort[0][direction]': 'asc',
                'fields[]': 'ID',  # Only get the ID field to minimize response size
                'pageSize': 100  # Maximum allowed by Airtable
            }
            
            if offset:
                params['offset'] = offset
            
            try:
                response = requests.get(self.base_url, headers=self.headers, params=params)
                response.raise_for_status()
                
                data = response.json()
                records = data.get('records', [])
                all_records.extend(records)
                
                print(f"   📄 Page {page}: {len(records)} records (Total: {len(all_records)})")
                page += 1
                
                # Check if there are more records
                offset = data.get('offset')
                if not offset:
                    break
                    
                # Rate limiting - be nice to Airtable API
                time.sleep(0.2)
                
            except requests.exceptions.RequestException as e:
                print(f"❌ Error fetching records: {e}")
                if hasattr(e.response, 'text'):
                    print(f"   Response: {e.response.text}")
                break
        
        print(f"✅ Total records fetched: {len(all_records)}")
        return all_records
    
    def update_records_batch(self, records_to_update: List[Dict[str, Any]]) -> bool:
        """Update a batch of records (max 10 per Airtable API limit)"""
        if not records_to_update:
            return True
            
        payload = {
            "records": records_to_update
        }
        
        try:
            response = requests.patch(self.base_url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error updating batch: {e}")
            if hasattr(e.response, 'text'):
                print(f"   Response: {e.response.text}")
            return False
    
    def update_all_ids_sequential(self):
        """Update all record IDs to be sequential"""
        print(f"\n🎯 Starting Sequential ID Update Process")
        print(f"=" * 50)
        
        # Get all records
        all_records = self.get_all_records()
        
        if not all_records:
            print("❌ No records found!")
            return False
        
        total_records = len(all_records)
        print(f"\n📊 Processing {total_records} records...")
        
        # Prepare updates in batches of 10 (Airtable API limit)
        batch_size = 10
        successful_updates = 0
        failed_updates = 0
        
        for i in range(0, total_records, batch_size):
            batch = all_records[i:i + batch_size]
            batch_records = []
            
            for j, record in enumerate(batch):
                new_sequential_id = i + j + 1  # Sequential ID starting from 1
                current_id = record.get('fields', {}).get('ID', 'Unknown')
                
                batch_records.append({
                    "id": record['id'],
                    "fields": {
                        "ID": new_sequential_id
                    }
                })
            
            # Update this batch
            batch_num = (i // batch_size) + 1
            total_batches = (total_records + batch_size - 1) // batch_size
            
            print(f"🔄 Batch {batch_num}/{total_batches}: Updating records {i+1}-{min(i+batch_size, total_records)}")
            
            if self.update_records_batch(batch_records):
                successful_updates += len(batch_records)
                print(f"   ✅ Success: {len(batch_records)} records updated")
            else:
                failed_updates += len(batch_records)
                print(f"   ❌ Failed: {len(batch_records)} records")
            
            # Progress indicator
            progress = (batch_num / total_batches) * 100
            print(f"   📈 Progress: {progress:.1f}% ({successful_updates}/{total_records} completed)")
            
            # Rate limiting
            time.sleep(0.3)
        
        # Final summary
        print(f"\n🎉 SEQUENTIAL ID UPDATE COMPLETED!")
        print(f"=" * 50)
        print(f"✅ Successfully updated: {successful_updates} records")
        print(f"❌ Failed updates: {failed_updates} records")
        print(f"📊 Success rate: {(successful_updates/total_records)*100:.1f}%")
        
        if failed_updates == 0:
            print(f"🎯 ALL RECORDS NOW HAVE SEQUENTIAL IDs (1 to {total_records})")
        
        return failed_updates == 0

def main():
    """Main execution function"""
    print("🚀 AIRTABLE SEQUENTIAL ID BULK UPDATE")
    print("=" * 50)
    print("📋 This will update ALL record IDs to be sequential: 1, 2, 3, 4, 5...")
    print("⚠️  This operation will modify ALL records in the table")
    
    updater = AirtableBulkUpdater()
    success = updater.update_all_ids_sequential()
    
    if success:
        print(f"\n🎉 SUCCESS: All records now have sequential IDs!")
        print(f"✨ Ready for fresh production workflow")
    else:
        print(f"\n⚠️  PARTIAL SUCCESS: Some updates failed")
        print(f"🔄 You may need to run this again for failed records")

if __name__ == "__main__":
    main()