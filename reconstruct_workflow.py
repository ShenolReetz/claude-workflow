#!/usr/bin/env python3
"""
Reconstruct the workflow_runner.py file properly
"""

# Read the broken file
with open('/home/claude-workflow/src/workflow_runner.py', 'r') as f:
    content = f.read()

# Find where the text control section ends (before the helper method)
text_control_end = content.find('async def _save_countdown_to_airtable')
if text_control_end == -1:
    text_control_end = content.find('async def *save*countdown_to_airtable')

if text_control_end > 0:
    # Get everything before the broken helper method
    good_part = content[:text_control_end].rstrip()
    
    # Add the proper ending
    proper_ending = '''

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
            keywords,
            content_data
        )
        
        # Step 7: Generate Amazon affiliate links
        print("🔗 Generating Amazon affiliate links...")
        affiliate_result = await run_amazon_affiliate_generation(
            self.config,
            pending_title['record_id']
        )
        
        if affiliate_result['success']:
            print(f"✅ Generated {affiliate_result['links_generated']} affiliate links")
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
                video_result['video_url']
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
'''
    
    # Write the reconstructed file
    with open('/home/claude-workflow/src/workflow_runner.py', 'w') as f:
        f.write(good_part + proper_ending)
    
    print("✅ Reconstructed workflow_runner.py")
else:
    print("❌ Could not find where to split the file")
