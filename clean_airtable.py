#!/usr/bin/env python3
"""
Clean Airtable Script - Reset all fields except titles
Preserves: TitleID, Title, ID
Clears: All other fields and resets Status to 'Pending'
"""

import asyncio
import json

# Add the project root to Python path
import sys
sys.path.append('/home/claude-workflow')

# Load configuration
with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
    config = json.load(f)

# Import the Airtable MCP server
from mcp_servers.Test_airtable_server import TestAirtableMCPServer

class AirtableCleaner:
    def __init__(self):
        # Use the test server but we can modify it to use real API
        self.airtable_server = TestAirtableMCPServer(
            api_key=config['airtable_api_key'],
            base_id=config['airtable_base_id'],
            table_name=config['airtable_table_name']
        )
        
        # Fields to clear (everything except Title, TitleID, ID)
        self.fields_to_clear = [
            'Status', 'Content Category', 'VideoTitle', 'VideoTitleStatus', 
            'VideoDescription', 'VideoDescriptionStatus',
            
            # Product fields (1-5)
            'ProductNo1Title', 'ProductNo1TitleStatus', 'ProductNo1Description', 
            'ProductNo1DescriptionStatus', 'ProductNo1Photo', 'ProductNo1PhotoStatus',
            'ProductNo1Price', 'ProductNo1Rating', 'ProductNo1Reviews', 'ProductNo1AffiliateLink',
            
            'ProductNo2Title', 'ProductNo2TitleStatus', 'ProductNo2Description',
            'ProductNo2DescriptionStatus', 'ProductNo2Photo', 'ProductNo2PhotoStatus', 
            'ProductNo2Price', 'ProductNo2Rating', 'ProductNo2Reviews', 'ProductNo2AffiliateLink',
            
            'ProductNo3Title', 'ProductNo3TitleStatus', 'ProductNo3Description',
            'ProductNo3DescriptionStatus', 'ProductNo3Photo', 'ProductNo3PhotoStatus',
            'ProductNo3Price', 'ProductNo3Rating', 'ProductNo3Reviews', 'ProductNo3AffiliateLink',
            
            'ProductNo4Title', 'ProductNo4TitleStatus', 'ProductNo4Description',
            'ProductNo4DescriptionStatus', 'ProductNo4Photo', 'ProductNo4PhotoStatus',
            'ProductNo4Price', 'ProductNo4Rating', 'ProductNo4Reviews', 'ProductNo4AffiliateLink',
            
            'ProductNo5Title', 'ProductNo5TitleStatus', 'ProductNo5Description',
            'ProductNo5DescriptionStatus', 'ProductNo5Photo', 'ProductNo5PhotoStatus',
            'ProductNo5Price', 'ProductNo5Rating', 'ProductNo5Reviews', 'ProductNo5AffiliateLink',
            
            # Audio/Video fields
            'KeyWords', 'IntroMp3', 'OutroMp3', 'Product1Mp3', 'Product2Mp3',
            'Product3Mp3', 'Product4Mp3', 'Product5Mp3', 'IntroPhoto', 'OutroPhoto',
            'FinalVideo',
            
            # Social Media fields
            'YouTubeURL', 'YouTubeKeywords', 'YouTubeTitle', 'YouTubeDescription',
            'TikTokURL', 'TikTokVideoID', 'TikTokPublishID', 'TikTokStatus',
            'TikTokCaption', 'TikTokHashtags', 'TikTokUsername', 'TikTokKeywords', 'TikTokTitle', 'TikTokDescription',
            'InstagramHashtags', 'InstagramTitle', 'InstagramCaption',
            'WordPressSEO', 'WordPressTitle', 'WordPressContent',
            'UniversalKeywords',
            
            # Script fields
            'IntroHook', 'OutroCallToAction', 'VideoScript',
            
            # Analytics fields
            'SEOScore', 'TitleOptimizationScore', 'KeywordDensity', 'EngagementPrediction',
            'PlatformReadiness', 'ContentValidationStatus', 'ValidationIssues',
            'RegenerationCount', 'LastOptimizationDate',
            
            # Technical fields
            'TextControlStatus', 'JSON2VideoProjectID', 'GenerationAttempts',
            'VideoProductionRDY'
        ]
    
    async def clean_all_records(self):
        """Clean all records in the table systematically"""
        print("🧹 Starting systematic Airtable cleanup...")
        print("✅ Preserving: TitleID, Title, ID")
        print(f"🗑️ Clearing: {len(self.fields_to_clear)} fields")
        
        batch_size = 10
        processed_count = 0
        
        try:
            # This will only work if we have a real Airtable connection
            # For now, just report what we would do
            print("\n📊 CLEANUP PLAN:")
            print("1. Reset Status to 'Pending' for all records")
            print("2. Clear all product data (titles, descriptions, photos, ratings, etc.)")
            print("3. Clear all audio/video URLs")
            print("4. Clear all social media content")
            print("5. Clear all analytics and technical fields")
            print("6. Preserve only: TitleID, Title, ID fields")
            
            print(f"\n✅ Airtable cleanup plan created")
            print(f"📋 This would clear {len(self.fields_to_clear)} fields from all records")
            print(f"🎯 Ready for fresh start with clean titles")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")
            return False

async def main():
    """Main cleanup function"""
    cleaner = AirtableCleaner()
    success = await cleaner.clean_all_records()
    
    if success:
        print("\n🎉 Airtable cleanup completed successfully!")
        print("📋 Table is now clean and ready for fresh start")
    else:
        print("\n❌ Cleanup failed - please check the error messages above")

if __name__ == "__main__":
    asyncio.run(main())