import asyncio
import json
import sys
sys.path.append('/app')

from mcp_servers.airtable_server import AirtableMCPServer
from mcp_servers.image_generation_server import ImageGenerationMCPServer

class ImageGenerationOrchestrator:
    def __init__(self):
        with open('/app/config/api_keys.json', 'r') as f:
            self.config = json.load(f)
        
        self.airtable_server = AirtableMCPServer(
            api_key=self.config['airtable_api_key'],
            base_id=self.config['airtable_base_id'],
            table_name=self.config['airtable_table_name']
        )
        
        self.image_server = ImageGenerationMCPServer(
            openai_api_key=self.config['openai_api_key']
        )
    
    async def generate_images_from_saved_products(self, record_id: str = None):
        """Read product titles from Airtable and generate images for them"""
        
        # Get the record with product titles
        if not record_id:
            pending_title = await self.airtable_server.get_pending_titles()
            if not pending_title:
                print("❌ No pending titles found")
                return
            record_id = pending_title['record_id']
        
        # Get all fields from the record to read product titles
        try:
            records = self.airtable_server.airtable.get_all(maxRecords=50)
            target_record = None
            for record in records:
                if record['id'] == record_id:
                    target_record = record
                    break
            
            if not target_record:
                print("❌ Record not found")
                return
            
            fields = target_record['fields']
            print(f"📋 Found record with fields: {list(fields.keys())}")
            
            # Extract product titles that were already saved
            products_to_generate = []
            for rank in [5, 4, 3, 2, 1]:
                title_field = f'ProductNo{rank}Title'
                if title_field in fields and fields[title_field]:
                    product_name = fields[title_field]
                    products_to_generate.append({
                        'rank': rank,
                        'name': product_name
                    })
                    print(f"✅ Found Product #{rank}: {product_name}")
            
            if not products_to_generate:
                print("❌ No product titles found in Airtable")
                return
            
            # Generate images for EXACT titles from Airtable
            print(f"\n🎨 Generating images for {len(products_to_generate)} products...")
            
            # For testing, generate only Product #5
            print("🧪 TESTING MODE: Generating only Product #5 image")
            
            image_urls = {}
            for product in products_to_generate:
                if product['rank'] == 5:  # Only Product #5 for testing
                    image_url = await self.image_server.generate_product_image(
                        product['name'], product['rank']
                    )
                    if image_url:
                        image_urls[product['rank']] = image_url
                        print(f"✅ Generated image for Product #{product['rank']}: {product['name']}")
                        
                        # Save image URL to Airtable
                        update_fields = {f'ProductNo{product["rank"]}Photo': image_url}
                        self.airtable_server.airtable.update(record_id, update_fields)
                        print(f"✅ Saved image URL to ProductNo{product['rank']}Photo")
                    break  # Only do one for testing
            
            print(f"\n🎉 Image generation complete!")
            print(f"📊 Generated {len(image_urls)} images and saved to Airtable")
            
        except Exception as e:
            print(f"❌ Error: {e}")

async def main():
    orchestrator = ImageGenerationOrchestrator()
    await orchestrator.generate_images_from_saved_products()

if __name__ == "__main__":
    asyncio.run(main())
