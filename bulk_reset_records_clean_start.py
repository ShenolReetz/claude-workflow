#!/usr/bin/env python3
"""
🚀 PRODUCTION WORKFLOW FILE - DO NOT DELETE 🚀
This file is part of the Production Flow system.
⚠️  DO NOT DELETE during cleanup phases - Required for production operations.

Bulk Reset Airtable Records for Clean Start - Direct API Approach
Resets all records with status "Completed", "Processing", or "Skipped" to "Pending"
Clears all data fields except Title and ID for fresh start

Purpose: Provides clean slate for production workflow restarts
Usage: Run when you need to reset processed records for fresh start
Status: Production-ready utility script
"""

import requests
import json
import time
from typing import List, Dict, Any, Optional

class AirtableCleanStartResetter:
    def __init__(self):
        # Load configuration
        with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
            config = json.load(f)
        
        self.api_key = config['airtable_api_key']
        self.base_id = config['airtable_base_id']
        self.table_id = "tblhGDEW6eUbmaYZx"
        self.base_url = f"https://api.airtable.com/v0/{self.base_id}/{self.table_id}"
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        print(f"🧹 Airtable Clean Start Resetter Initialized")
        print(f"📋 Base ID: {self.base_id}")
        print(f"🏠 Table ID: {self.table_id}")
        
        # Fields to preserve (keep these as-is)
        self.fields_to_preserve = {
            'TitleID',  # Primary field
            'Title',    # Title content
            'ID'        # Sequential ID we just updated
        }
        
        # Define all fields that need to be cleared/reset
        self.fields_to_clear = [
            # Status and workflow fields - reset to default values
            'Status',  # Will be set to 'Pending'
            'Content Category', 'VideoTitle', 'VideoTitleStatus', 'VideoDescription', 'VideoDescriptionStatus',
            'VideoProductionRDY',  # Will be set to 'Pending'
            
            # Product fields (1-5) - clear all
            'ProductNo1Title', 'ProductNo1TitleStatus', 'ProductNo1Description', 'ProductNo1DescriptionStatus', 
            'ProductNo1Photo', 'ProductNo1PhotoStatus', 'ProductNo1Price', 'ProductNo1Rating', 'ProductNo1Reviews', 'ProductNo1AffiliateLink',
            
            'ProductNo2Title', 'ProductNo2TitleStatus', 'ProductNo2Description', 'ProductNo2DescriptionStatus',
            'ProductNo2Photo', 'ProductNo2PhotoStatus', 'ProductNo2Price', 'ProductNo2Rating', 'ProductNo2Reviews', 'ProductNo2AffiliateLink',
            
            'ProductNo3Title', 'ProductNo3TitleStatus', 'ProductNo3Description', 'ProductNo3DescriptionStatus',
            'ProductNo3Photo', 'ProductNo3PhotoStatus', 'ProductNo3Price', 'ProductNo3Rating', 'ProductNo3Reviews', 'ProductNo3AffiliateLink',
            
            'ProductNo4Title', 'ProductNo4TitleStatus', 'ProductNo4Description', 'ProductNo4DescriptionStatus',
            'ProductNo4Photo', 'ProductNo4PhotoStatus', 'ProductNo4Price', 'ProductNo4Rating', 'ProductNo4Reviews', 'ProductNo4AffiliateLink',
            
            'ProductNo5Title', 'ProductNo5TitleStatus', 'ProductNo5Description', 'ProductNo5DescriptionStatus',
            'ProductNo5Photo', 'ProductNo5PhotoStatus', 'ProductNo5Price', 'ProductNo5Rating', 'ProductNo5Reviews', 'ProductNo5AffiliateLink',
            
            # Audio/Video fields - clear all
            'KeyWords', 'IntroMp3', 'OutroMp3', 'Product1Mp3', 'Product2Mp3', 'Product3Mp3', 'Product4Mp3', 'Product5Mp3',
            'IntroPhoto', 'OutroPhoto', 'FinalVideo',
            
            # Social Media fields - clear all
            'YouTubeURL', 'YouTubeKeywords', 'YouTubeTitle', 'YouTubeDescription',
            'TikTokURL', 'TikTokVideoID', 'TikTokPublishID', 'TikTokStatus', 'TikTokCaption', 'TikTokHashtags', 
            'TikTokUsername', 'TikTokKeywords', 'TikTokTitle', 'TikTokDescription',
            'InstagramHashtags', 'InstagramTitle', 'InstagramCaption',
            'WordPressSEO', 'WordPressTitle', 'WordPressContent',
            'UniversalKeywords',
            
            # Script fields - clear all
            'IntroHook', 'OutroCallToAction', 'VideoScript',
            
            # Analytics fields - clear all
            'SEOScore', 'TitleOptimizationScore', 'KeywordDensity', 'EngagementPrediction',
            'PlatformReadiness', 'ContentValidationStatus', 'ValidationIssues',
            'RegenerationCount', 'LastOptimizationDate',
            
            # Technical fields - clear all
            'TextControlStatus', 'JSON2VideoProjectID', 'GenerationAttempts'
        ]
    
    def get_records_to_reset(self) -> List[Dict[str, Any]]:
        """Get all records that need to be reset (Completed, Processing, Skipped status)"""
        target_records = []
        offset = None
        page = 1
        
        print(f"\n🔍 Finding records with status 'Completed', 'Processing', or 'Skipped'...")
        
        while True:
            # Build URL with parameters - get records that need resetting
            params = {
                'sort[0][field]': 'ID',
                'sort[0][direction]': 'asc',
                'filterByFormula': 'OR({Status} = "Completed", {Status} = "Processing", {Status} = "Skipped")',
                'pageSize': 100  # Maximum allowed by Airtable
            }
            
            if offset:
                params['offset'] = offset
            
            try:
                response = requests.get(self.base_url, headers=self.headers, params=params)
                response.raise_for_status()
                
                data = response.json()
                records = data.get('records', [])
                target_records.extend(records)
                
                print(f"   📄 Page {page}: {len(records)} records to reset (Total: {len(target_records)})")
                page += 1
                
                # Check if there are more records
                offset = data.get('offset')
                if not offset:
                    break
                    
                # Rate limiting
                time.sleep(0.2)
                
            except requests.exceptions.RequestException as e:
                print(f"❌ Error fetching records: {e}")
                if hasattr(e.response, 'text'):
                    print(f"   Response: {e.response.text}")
                break
        
        print(f"✅ Found {len(target_records)} records to reset")
        return target_records
    
    def create_reset_fields(self) -> Dict[str, Any]:
        """Create the field values for resetting records based on actual field types"""
        reset_fields = {}
        
        # Define field-specific reset values based on Airtable field types
        field_reset_map = {
            # Main Status fields
            'Status': 'Pending',
            'VideoProductionRDY': 'Pending',
            
            # All Status fields to 'Pending'
            'VideoTitleStatus': 'Pending',
            'VideoDescriptionStatus': 'Pending',
            'ProductNo1TitleStatus': 'Pending',
            'ProductNo1DescriptionStatus': 'Pending',
            'ProductNo1PhotoStatus': 'Pending',
            'ProductNo2TitleStatus': 'Pending',
            'ProductNo2DescriptionStatus': 'Pending',
            'ProductNo2PhotoStatus': 'Pending',
            'ProductNo3TitleStatus': 'Pending',
            'ProductNo3DescriptionStatus': 'Pending',
            'ProductNo3PhotoStatus': 'Pending',
            'ProductNo4TitleStatus': 'Pending',
            'ProductNo4DescriptionStatus': 'Pending',
            'ProductNo4PhotoStatus': 'Pending',
            'ProductNo5TitleStatus': 'Pending',
            'ProductNo5DescriptionStatus': 'Pending',
            'ProductNo5PhotoStatus': 'Pending',
            
            # Single Select fields with specific options
            'TikTokStatus': None,  # Clear entirely 
            'ContentValidationStatus': 'Draft',  # Default to Draft
            
            # Multiple select fields
            'Content Category': [],  # Empty array for multiple record links
            'PlatformReadiness': [],  # Empty array for multiple selects
            
            # Text fields (singleLineText, multilineText, richText)
            'VideoTitle': '',
            'VideoDescription': '',
            'ProductNo1Title': '',
            'ProductNo1Description': '',
            'ProductNo2Title': '',
            'ProductNo2Description': '',
            'ProductNo3Title': '',
            'ProductNo3Description': '',
            'ProductNo4Title': '',
            'ProductNo4Description': '',
            'ProductNo5Title': '',
            'ProductNo5Description': '',
            'KeyWords': '',
            'YouTubeKeywords': '',
            'InstagramHashtags': '',
            'TikTokKeywords': '',
            'WordPressSEO': '',
            'UniversalKeywords': '',
            'YouTubeTitle': '',
            'TikTokTitle': '',
            'InstagramTitle': '',
            'WordPressTitle': '',
            'YouTubeDescription': '',
            'TikTokDescription': '',
            'InstagramCaption': '',
            'WordPressContent': '',
            'IntroHook': '',
            'OutroCallToAction': '',
            'VideoScript': '',
            'TextControlStatus': '',
            'JSON2VideoProjectID': '',
            'TikTokVideoID': '',
            'TikTokPublishID': '',
            'TikTokCaption': '',
            'TikTokHashtags': '',
            'TikTokUsername': '',
            'ValidationIssues': '',
            
            # URL fields
            'ProductNo1Photo': '',
            'ProductNo2Photo': '',
            'ProductNo3Photo': '',
            'ProductNo4Photo': '',
            'ProductNo5Photo': '',
            'IntroMp3': '',
            'OutroMp3': '',
            'Product1Mp3': '',
            'Product2Mp3': '',
            'Product3Mp3': '',
            'Product4Mp3': '',
            'Product5Mp3': '',
            'IntroPhoto': '',
            'OutroPhoto': '',
            'FinalVideo': '',
            'ProductNo1AffiliateLink': '',
            'ProductNo2AffiliateLink': '',
            'ProductNo3AffiliateLink': '',
            'ProductNo4AffiliateLink': '',
            'ProductNo5AffiliateLink': '',
            'YouTubeURL': '',
            'TikTokURL': '',
            
            # Number fields (set to null, not 0, to truly clear them)
            'GenerationAttempts': None,
            'ProductNo1Price': None,
            'ProductNo2Price': None,
            'ProductNo3Price': None,
            'ProductNo4Price': None,
            'ProductNo5Price': None,
            'ProductNo1Rating': None,
            'ProductNo2Rating': None,
            'ProductNo3Rating': None,
            'ProductNo4Rating': None,
            'ProductNo5Rating': None,
            'ProductNo1Reviews': None,
            'ProductNo2Reviews': None,
            'ProductNo3Reviews': None,
            'ProductNo4Reviews': None,
            'ProductNo5Reviews': None,
            'SEOScore': None,
            'TitleOptimizationScore': None,
            'KeywordDensity': None,
            'EngagementPrediction': None,
            'RegenerationCount': None,
            
            # Date fields
            'LastOptimizationDate': None,
        }
        
        return field_reset_map
    
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
    
    def reset_all_records(self):
        """Reset all records with Completed/Processing/Skipped status to clean state"""
        print(f"\n🧹 Starting Clean Start Reset Process")
        print(f"=" * 50)
        
        # Get records to reset
        records_to_reset = self.get_records_to_reset()
        
        if not records_to_reset:
            print("✅ No records found with 'Completed', 'Processing', or 'Skipped' status!")
            print("🎯 All records are already clean or in 'Pending' status")
            return True
        
        total_records = len(records_to_reset)
        print(f"\n📊 Resetting {total_records} records to clean state...")
        print(f"🎯 Action: Status → 'Pending', Clear all data except Title & ID")
        
        # Prepare the reset field values
        reset_fields = self.create_reset_fields()
        print(f"📋 Will clear/reset {len(reset_fields)} fields per record")
        
        # Process in batches of 10 (Airtable API limit)
        batch_size = 10
        successful_updates = 0
        failed_updates = 0
        
        for i in range(0, total_records, batch_size):
            batch = records_to_reset[i:i + batch_size]
            batch_records = []
            
            for record in batch:
                current_status = record.get('fields', {}).get('Status', 'Unknown')
                current_id = record.get('fields', {}).get('ID', 'Unknown')
                title = record.get('fields', {}).get('Title', 'No Title')
                
                batch_records.append({
                    "id": record['id'],
                    "fields": reset_fields.copy()  # Use the same reset fields for all records
                })
            
            # Update this batch
            batch_num = (i // batch_size) + 1
            total_batches = (total_records + batch_size - 1) // batch_size
            
            print(f"🧹 Batch {batch_num}/{total_batches}: Resetting records {i+1}-{min(i+batch_size, total_records)}")
            
            if self.update_records_batch(batch_records):
                successful_updates += len(batch_records)
                print(f"   ✅ Success: {len(batch_records)} records reset to clean state")
            else:
                failed_updates += len(batch_records)
                print(f"   ❌ Failed: {len(batch_records)} records")
            
            # Progress indicator
            progress = (batch_num / total_batches) * 100
            print(f"   📈 Progress: {progress:.1f}% ({successful_updates}/{total_records} completed)")
            
            # Rate limiting
            time.sleep(0.3)
        
        # Final summary
        print(f"\n🎉 CLEAN START RESET COMPLETED!")
        print(f"=" * 50)
        print(f"✅ Successfully reset: {successful_updates} records")
        print(f"❌ Failed resets: {failed_updates} records")
        print(f"📊 Success rate: {(successful_updates/total_records)*100:.1f}%")
        
        if failed_updates == 0:
            print(f"🎯 ALL TARGETED RECORDS NOW RESET TO CLEAN STATE")
            print(f"✨ Status: 'Pending' | All fields cleared except Title & ID")
        
        return failed_updates == 0

def main():
    """Main execution function"""
    print("🧹 AIRTABLE CLEAN START RESET")
    print("=" * 50)
    print("📋 This will reset records with 'Completed', 'Processing', or 'Skipped' status")
    print("🎯 Action: Set Status → 'Pending' and clear all data except Title & ID")
    print("⚠️  This will clear ALL content data for targeted records")
    
    resetter = AirtableCleanStartResetter()
    success = resetter.reset_all_records()
    
    if success:
        print(f"\n🎉 SUCCESS: All targeted records reset to clean state!")
        print(f"✨ Ready for fresh production workflow with clean data")
    else:
        print(f"\n⚠️  PARTIAL SUCCESS: Some resets failed")
        print(f"🔄 You may need to run this again for failed records")

if __name__ == "__main__":
    main()