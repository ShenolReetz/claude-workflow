import asyncio
import json
import sys
sys.path.append('/app')

from mcp_servers.airtable_server import AirtableMCPServer
from mcp_servers.voice_generation_server import VoiceGenerationMCPServer

class VoiceGenerationOrchestrator:
    def __init__(self):
        with open('/app/config/api_keys.json', 'r') as f:
            self.config = json.load(f)
        
        self.airtable_server = AirtableMCPServer(
            api_key=self.config['airtable_api_key'],
            base_id=self.config['airtable_base_id'],
            table_name=self.config['airtable_table_name']
        )
        
        self.voice_server = VoiceGenerationMCPServer(
            elevenlabs_api_key=self.config['elevenlabs_api_key']
        )
    
    async def generate_single_product_voice(self, record_id: str = None):
        """Generate ONLY Product #5 voice and save to Product5Mp3 field"""
        
        if not record_id:
            pending_title = await self.airtable_server.get_pending_titles()
            if not pending_title:
                print("❌ No pending titles found")
                return
            record_id = pending_title['record_id']
        
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
            print(f"📋 Found record - testing Product #5 voice")
            
            # Generate ONLY Product #5 voice
            rank = 5
            title_field = f'ProductNo{rank}Title'
            desc_field = f'ProductNo{rank}Description'
            
            if (title_field in fields and fields[title_field] and 
                desc_field in fields and fields[desc_field]):
                
                product_name = fields[title_field]
                product_desc = fields[desc_field]
                
                print(f"🎵 Generating voice for Product #{rank}: {product_name}")
                
                product_voice = await self.voice_server.generate_product_voice(
                    product_name, product_desc, rank
                )
                
                if product_voice:
                    # Now save to the ORIGINAL Product5Mp3 field (now Long Text type)
                    voice_updates = {f'Product{rank}Mp3': product_voice}
                    
                    print(f"💾 Saving to Product{rank}Mp3 field (Long Text)...")
                    try:
                        self.airtable_server.airtable.update(record_id, voice_updates)
                        print(f"✅ Successfully saved to Product{rank}Mp3!")
                        print(f"📊 Audio data: {len(product_voice)} characters saved")
                        print(f"🎵 You should now see the base64 audio data in your Product{rank}Mp3 column!")
                    except Exception as e:
                        print(f"❌ Save error: {e}")
                else:
                    print("❌ Voice generation failed")
            else:
                print("❌ Product #5 title/description not found")
                
        except Exception as e:
            print(f"❌ Error: {e}")

async def main():
    orchestrator = VoiceGenerationOrchestrator()
    await orchestrator.generate_single_product_voice()

if __name__ == "__main__":
    asyncio.run(main())
