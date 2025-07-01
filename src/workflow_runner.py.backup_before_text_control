
import asyncio
import json
import sys
import os
from datetime import datetime

# Add the project root to Python path
sys.path.append('/home/claude-workflow')

from mcp_servers.airtable_server import AirtableMCPServer
from mcp.amazon_affiliate_agent_mcp import run_amazon_affiliate_generation
from mcp_servers.content_generation_server import ContentGenerationMCPServer
from mcp.json2video_agent_mcp import run_video_creation
from mcp.google_drive_agent_mcp import upload_video_to_google_drive

class ContentPipelineOrchestrator:
    def __init__(self):
        # Load configuration
        with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
            self.config = json.load(f)
        
        # Initialize MCP servers
        self.airtable_server = AirtableMCPServer(
            api_key=self.config['airtable_api_key'],
            base_id=self.config['airtable_base_id'],
            table_name=self.config['airtable_table_name']
        )
        
        self.content_server = ContentGenerationMCPServer(
            anthropic_api_key=self.config['anthropic_api_key']
        )
        
    async def run_complete_workflow(self):
        """Run the complete content generation workflow"""
        print(f"🚀 Starting content workflow at {datetime.now()}")
        
        # Step 1: Get pending title from Airtable
        print("📋 Getting pending title from Airtable...")
        pending_title = await self.airtable_server.get_pending_titles()
        
        if not pending_title:
            print("❌ No pending titles found. Exiting.")
            return
        
        print(f"✅ Found title: {pending_title['title']}")
        
        # Step 2: Generate SEO keywords
        print("🔍 Generating SEO keywords...")
        keywords = await self.content_server.generate_seo_keywords(
            pending_title['title'], 
            "Electronics"  # You can make this dynamic later
        )
        
        # Step 3: Optimize title
        print("🎯 Optimizing title for social media...")
        optimized_title = await self.content_server.optimize_title(
            pending_title['title'], 
            keywords
        )
        
        # Step 4: Generate countdown script
        print("📝 Generating countdown script...")
        script_data = await self.content_server.generate_countdown_script(
            optimized_title, 
            keywords
        )
        
        # Step 5: Generate blog post
        #print("📄 Generating blog post...")
        #blog_post = await self.content_server.generate_blog_post(
        #    optimized_title, 
        #    script_data, 
        #    keywords
        #)
        print("📄 Blog generation skipped (testing mode - saves tokens)")
        blog_post = "Blog post generation disabled during testing to save tokens."
        # Step 6: Save everything back to Airtable
        print("💾 Saving generated content to Airtable...")
        content_data = {
            'keywords': keywords,
            'optimized_title': optimized_title,
            'script': script_data,
        #    'blog_post': blog_post #desabled for testing
        }
        
        await self.airtable_server.save_generated_content(
            pending_title['record_id'], 
            content_data
        )
        

        # Step 6.5: Generate Amazon Affiliate Links (NEW)
        print("🔗 Generating Amazon affiliate links...")
        try:
            affiliate_result = await run_amazon_affiliate_generation(
                self.config,
                pending_title['record_id']
            )
            
            if affiliate_result['success']:
                print(f"✅ Generated {affiliate_result.get('affiliate_links_generated', 0)} affiliate links")
                print(f"   📦 Processed {affiliate_result.get('products_processed', 0)} products")
            else:
                print(f"⚠️ Affiliate link generation had issues: {affiliate_result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error generating affiliate links: {str(e)}")
            # Continue workflow even if affiliate links fail


        # Step 6.7: Create Video with JSON2Video (NEW)
        print("🎬 Creating video with JSON2Video...")
        try:
            video_result = await run_video_creation(
                self.config,
                pending_title['record_id']
            )
            
            print(f"🔍 DEBUG: video_result = {video_result}")
            if video_result and video_result.get('success', False):
                print(f"✅ Video creation started! Movie ID: {video_result['movie_id']}")
                
                # Upload to Google Drive if video URL exists
                video_url = video_result.get('video_url')
                print(f'🔍 DEBUG: video_url from result = {video_url}')
                if video_url and video_url.strip():
                    print(f"☁️ Uploading video to Google Drive...")
                    drive_result = await upload_video_to_google_drive(
                        self.config,
                        video_url,
                        optimized_title,
                        pending_title['record_id']
                    )
                    
                    if drive_result['success']:
                        print(f"✅ Video uploaded to Google Drive: {drive_result['drive_url']}")
                        # Update Airtable with Google Drive URL in FinalVideo field
                        await self.airtable_server.update_record(
                            pending_title['record_id'],
                            {'FinalVideo': drive_result['drive_url']}
                        )
                        print(f"✅ Updated FinalVideo field in Airtable with: {drive_result['drive_url']}")
                    else:
                        print(f"⚠️ Failed to upload to Google Drive: {drive_result.get('error')}")


                
        except Exception as e:
            print(f"❌ Error creating video: {str(e)}")
            # Continue workflow even if video creation fails

        # Step 7: Update status to "Done"
        print("✅ Updating record status to 'Done'...")
        await self.airtable_server.update_record_status(
            pending_title['record_id'], 
            "Processing"
        )
        
        print("🎉 Complete workflow finished successfully!")
        print(f"📊 Summary:")
        print(f"   Original: {pending_title['title']}")
        print(f"   Optimized: {optimized_title}")
        print(f"   Keywords: {len(keywords)} generated")
        print(f"   Script: {len(script_data.get('products', []))} products")
        print(f"   Blog: {len(blog_post)} characters")
        print(f"   Blog: Skipped (testing mode)")
        if "affiliate_result" in locals():
            print(f"   Affiliate Links: {affiliate_result.get("affiliate_links_generated", 0)} generated")
        if "video_result" in locals():
            if video_result["success"]:
                print(f"   Video: Started (ID: {video_result.get("movie_id", "N/A")})")
            else:
                print(f"   Video: Failed ({video_result.get("error", "Unknown")})")

async def main():
    orchestrator = ContentPipelineOrchestrator()
    await orchestrator.run_complete_workflow()

if __name__ == "__main__":
    asyncio.run(main())
