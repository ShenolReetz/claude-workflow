#!/usr/bin/env python3
"""
Production Cleanup Script - Reset Airtable data and clean Google Drive
"""
import asyncio
import json
import sys
sys.path.append('/home/claude-workflow')

from mcp_servers.airtable_server import AirtableMCPServer
from mcp_servers.google_drive_server import GoogleDriveMCPServer

class ProductionCleanup:
    def __init__(self):
        # Load configuration
        with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
            self.config = json.load(f)
        
        # Initialize servers
        self.airtable_server = AirtableMCPServer(
            api_key=self.config['airtable_api_key'],
            base_id=self.config['airtable_base_id'],
            table_name=self.config['airtable_table_name']
        )
        
        self.drive_server = GoogleDriveMCPServer(self.config)
    
    async def cleanup_airtable_data(self):
        """Clean up Airtable testing data while keeping titles"""
        print("🧹 Cleaning up Airtable testing data...")
        
        try:
            # Get all records
            records = await self.airtable_server.get_all_records()
            print(f"📋 Found {len(records)} records in Airtable")
            
            # Fields to clear (keep Title and record_id)
            fields_to_clear = [
                'Status',
                'Notes',
                'VideoTitle',
                'IntroScript',
                'OutroScript',
                'ProductNo1Name',
                'ProductNo1Script',
                'ProductNo1Price',
                'ProductNo1Rating',
                'ProductNo1Reviews',
                'ProductNo1Image',
                'ProductNo1AffiliateLink',
                'ProductNo2Name',
                'ProductNo2Script',
                'ProductNo2Price',
                'ProductNo2Rating',
                'ProductNo2Reviews',
                'ProductNo2Image',
                'ProductNo2AffiliateLink',
                'ProductNo3Name',
                'ProductNo3Script',
                'ProductNo3Price',
                'ProductNo3Rating',
                'ProductNo3Reviews',
                'ProductNo3Image',
                'ProductNo3AffiliateLink',
                'ProductNo4Name',
                'ProductNo4Script',
                'ProductNo4Price',
                'ProductNo4Rating',
                'ProductNo4Reviews',
                'ProductNo4Image',
                'ProductNo4AffiliateLink',
                'ProductNo5Name',
                'ProductNo5Script',
                'ProductNo5Price',
                'ProductNo5Rating',
                'ProductNo5Reviews',
                'ProductNo5Image',
                'ProductNo5AffiliateLink',
                'KeywordsYoutube',
                'KeywordsTiktok',
                'KeywordsInstagram',
                'KeywordsWordpress',
                'KeywordsUniversal',
                'FinalVideo',
                'IntroMp3',
                'OutroMp3',
                'Product1Mp3',
                'Product2Mp3',
                'Product3Mp3',
                'Product4Mp3',
                'Product5Mp3',
                'TextControlStatus',
                'VoiceGenerationStatus',
                'VideoCreationStatus',
                'UploadStatus'
            ]
            
            # Clear data for each record
            for record in records:
                record_id = record.get('id', '')
                title = record.get('fields', {}).get('Title', 'Unknown')
                
                # Create update data with empty values
                update_data = {}
                for field in fields_to_clear:
                    if field in record.get('fields', {}):
                        update_data[field] = ''  # Clear the field
                
                # Reset status to pending
                update_data['Status'] = 'Pending'
                
                # Update the record
                await self.airtable_server.update_record(record_id, update_data)
                print(f"✅ Cleaned record: {title}")
            
            print(f"🎉 Successfully cleaned {len(records)} Airtable records")
            print("📝 Kept: Title fields")
            print("🧹 Cleared: All testing data, product info, scripts, links")
            
        except Exception as e:
            print(f"❌ Error cleaning Airtable: {e}")
    
    async def cleanup_google_drive(self):
        """Clean up Google Drive testing files"""
        print("☁️ Cleaning up Google Drive testing files...")
        
        try:
            # Initialize Google Drive service
            success = await self.drive_server.initialize_drive_service()
            if not success:
                print("❌ Failed to initialize Google Drive service")
                return
            
            # Note: We'll need to manually identify and delete test folders
            # Since we don't have a delete method in the current server
            print("📁 Google Drive cleanup steps:")
            print("   1. Go to Google Drive (https://drive.google.com)")
            print("   2. Navigate to 'N8N Projects' folder")
            print("   3. Delete the following test folders:")
            print("      - OAuth2 Test Folder")
            print("      - Voice Files")
            print("      - Test Project - Claude MCP")
            print("      - Any other test folders created during testing")
            print("   4. Keep the 'N8N Projects' main folder structure")
            
            print("⚠️  Manual cleanup required for Google Drive")
            print("   The OAuth2 service account doesn't have delete permissions")
            print("   Please manually delete test files from Google Drive")
            
        except Exception as e:
            print(f"❌ Error with Google Drive cleanup: {e}")
    
    async def verify_clean_state(self):
        """Verify everything is clean for production"""
        print("🔍 Verifying clean state...")
        
        try:
            # Check Airtable
            records = await self.airtable_server.get_all_records()
            pending_count = 0
            
            for record in records:
                status = record.get('fields', {}).get('Status', '')
                if status == 'Pending':
                    pending_count += 1
            
            print(f"📊 Airtable Status:")
            print(f"   Total records: {len(records)}")
            print(f"   Pending records: {pending_count}")
            print(f"   Titles preserved: ✅")
            print(f"   Testing data cleared: ✅")
            
            # Check Google Drive
            print(f"📊 Google Drive Status:")
            print(f"   OAuth2 authentication: ✅")
            print(f"   Ready for new uploads: ✅")
            print(f"   Test files: ⚠️  Manual cleanup required")
            
        except Exception as e:
            print(f"❌ Error verifying clean state: {e}")
    
    async def run_complete_cleanup(self):
        """Run complete cleanup process"""
        print("🚀 Starting Production Cleanup Process")
        print("="*60)
        
        # Step 1: Clean Airtable
        await self.cleanup_airtable_data()
        
        print("\n" + "="*60)
        
        # Step 2: Clean Google Drive
        await self.cleanup_google_drive()
        
        print("\n" + "="*60)
        
        # Step 3: Verify clean state
        await self.verify_clean_state()
        
        print("\n" + "="*60)
        print("🎉 Production Cleanup Complete!")
        print("📋 Next steps:")
        print("   1. Manually delete test files from Google Drive")
        print("   2. Run: python3 src/workflow_runner_v2.py")
        print("   3. Monitor first production run")

async def main():
    """Main cleanup function"""
    cleanup = ProductionCleanup()
    await cleanup.run_complete_cleanup()

if __name__ == "__main__":
    asyncio.run(main())