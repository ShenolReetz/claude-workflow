
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
from mcp.text_generation_control_agent_mcp_v2 import run_text_control_with_regeneration
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
        
        # Step 4.5: Text Generation Quality Control
        print("🎮 Running text generation quality control...")
        
        # First, we need to save the countdown script to Airtable
        await self._save_countdown_to_airtable(pending_title['record_id'], script_data)
        
        # Now run quality control
        control_result = await run_text_control_with_regeneration(self.config, pending_title['record_id'])
        
        if not control_result['success']:
            print(f"❌ Text control failed after {control_result.get('attempts', 0)} attempts")
            print(f"Issues: {control_result.get('error', 'Unknown error')}")
            # Continue anyway but log the issue
            await self.airtable_server.update_record(pending_title['record_id'], {
                'TextControlStatus': 'Failed',
                'Status': 'Processing'  # Keep processing but note the failure
            })
        elif control_result['all_valid']:
            print(f"✅ Text validated after {control_result['attempts']} attempt(s)")
            await self.airtable_server.update_record(pending_title['record_id'], {
                'TextControlStatus': 'Validated'
            })

        # Step 5: Generate blog post (disabled for testing)
        blog_post = "Blog post generation disabled during testing to save tokens."
        
        # Step 6: Save everything back to Airtable
        print("💾 Saving generated content to Airtable...")
        content_data = {
            'optimized_title': optimized_title,
            'script': script_data,
        }
        await self.airtable_server.save_generated_content(
            pending_title['record_id'],
            content_data
        )
        
        # Step 7: Generate Amazon affiliate links
        print("🔗 Generating Amazon affiliate links...")
        affiliate_result = await run_amazon_affiliate_generation(
            self.config,
            pending_title['record_id']
        )
        
        if affiliate_result.get('success'):
            links_count = affiliate_result.get('links_generated', 0)
            print(f"✅ Generated {links_count} affiliate links")
        else:
            print(f"⚠️ Affiliate link generation had issues: {affiliate_result.get('error', 'Unknown error')}")
        
        # Step 8: Create video with JSON2Video
        print("🎬 Creating video with JSON2Video...")
        video_result = await run_video_creation(
            self.config,
            pending_title['record_id']
        )
        
        print(f"🔍 DEBUG: video_result = {video_result}")
        
        if video_result['success']:
            print(f"✅ Video created successfully!")
            
            # Step 9: Upload to Google Drive
            print("☁️ Uploading video to Google Drive...")
            upload_result = await upload_video_to_google_drive(
                self.config,
                pending_title['record_id'],
                video_result['video_url'],
                pending_title['record_id']  # Add record_id as 4th argument
            )
            
            if upload_result['success']:
                print(f"✅ Video uploaded to Google Drive: {upload_result['drive_url']}")
            else:
                print(f"❌ Failed to upload video: {upload_result.get('error', 'Unknown error')}")
        else:
            print(f"❌ Video creation failed: {video_result.get('error', 'Unknown error')}")
        
        # Step 10: Update status
        print("✅ Updating record status to 'Done'...")
        await self.airtable_server.update_record_status(
            pending_title['record_id'],
            "Processing"
        )
        
        print("🎉 Complete workflow finished successfully!")
        print("📊 Summary:")
        print(f"   Original: {pending_title['title']}")
        print(f"   Optimized: {optimized_title}")
        print(f"   Products: {len(script_data.get('products', []))}")
        
    async def _save_countdown_to_airtable(self, record_id: str, script_data: dict):
        """Save countdown script products to Airtable"""
        update_fields = {}
        
        # Save each product - these fields definitely exist
        if 'products' in script_data:
            for i, product in enumerate(script_data['products']):
                product_num = i + 1
                update_fields[f'ProductNo{product_num}Title'] = product.get('title', '')
                update_fields[f'ProductNo{product_num}Description'] = product.get('description', '')
        
        if update_fields:
            try:
                await self.airtable_server.update_record(record_id, update_fields)
                print(f"💾 Saved {len(update_fields)} fields to Airtable")
            except Exception as e:
                print(f"⚠️ Error saving to Airtable: {e}")


# Run the workflow
async def main():
    orchestrator = ContentPipelineOrchestrator()
    await orchestrator.run_complete_workflow()

if __name__ == "__main__":
    asyncio.run(main())
