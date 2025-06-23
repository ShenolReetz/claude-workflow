import asyncio
import json
import sys
import os
from datetime import datetime

# Add the project root to Python path
sys.path.append('/app')

from mcp_servers.airtable_server import AirtableMCPServer
from mcp_servers.content_generation_server import ContentGenerationMCPServer
from mcp_servers.image_generation_server import ImageGenerationMCPServer

class ContentPipelineOrchestrator:
    def __init__(self):
        # Load configuration
        with open('/app/config/api_keys.json', 'r') as f:
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
        
        self.image_server = ImageGenerationMCPServer(
            openai_api_key=self.config['openai_api_key']
        )
        
    async def run_workflow_with_single_image(self):
        """Run workflow with only ONE image generation (for testing)"""
        print(f"🚀 Starting content workflow with single image test at {datetime.now()}")
        
        # Step 1-4: Same as before (get title, keywords, optimize, script)
        pending_title = await self.airtable_server.get_pending_titles()
        if not pending_title:
            print("❌ No pending titles found. Exiting.")
            return
            
        print(f"✅ Found title: {pending_title['title']}")
        
        keywords = await self.content_server.generate_seo_keywords(
            pending_title['title'], "Electronics"
        )
        
        optimized_title = await self.content_server.optimize_title(
            pending_title['title'], keywords
        )
        
        script_data = await self.content_server.generate_countdown_script(
            optimized_title, keywords
        )
        
        # Step 5: Generate ONLY Product #5 image (most expensive product)
        print("🎨 Generating image for Product #5 only (testing mode)...")
        products = script_data.get('products', [])
        
        image_urls = {}
        if products:
            # Find Product #5 (highest rank)
            product_5 = None
            for product in products:
                if product.get('rank') == 5:
                    product_5 = product
                    break
            
            if product_5:
                image_url = await self.image_server.generate_product_image(
                    product_5.get('name', ''), 5
                )
                if image_url:
                    image_urls[5] = image_url
                    print(f"✅ Generated image for Product #5: {product_5.get('name')}")
                else:
                    print("❌ Failed to generate image for Product #5")
        
        # Step 6: Save everything (including single image)
        print("💾 Saving generated content to Airtable...")
        content_data = {
            'keywords': keywords,
            'optimized_title': optimized_title,
            'script': script_data,
            'image_urls': image_urls  # Only contains Product #5 image
        }
        
        await self.airtable_server.save_generated_content(
            pending_title['record_id'], content_data
        )
        
        print("🎉 Single-image workflow finished successfully!")
        print(f"📊 Summary:")
        print(f"   Keywords: {len(keywords)} generated")
        print(f"   Script: {len(script_data.get('products', []))} products")
        print(f"   Images: {len(image_urls)} generated (Product #5 only)")

async def main():
    orchestrator = ContentPipelineOrchestrator()
    await orchestrator.run_workflow_with_single_image()

if __name__ == "__main__":
    asyncio.run(main())
