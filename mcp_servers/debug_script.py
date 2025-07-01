import asyncio
import json
import sys
sys.path.append('/app')

from mcp_servers.content_generation_server import ContentGenerationMCPServer

async def debug_script():
    with open('/app/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    server = ContentGenerationMCPServer(config['anthropic_api_key'])
    
    title = "Top 5 New Car Mono Amplifiers Releases 2025"
    keywords = ['car amplifiers', 'mono amp', 'car audio']
    
    print("🔍 Generating script...")
    script_data = await server.generate_countdown_script(title, keywords)
    
    print(f"\n📊 Script type: {type(script_data)}")
    print(f"📊 Script keys: {script_data.keys() if isinstance(script_data, dict) else 'Not a dict'}")
    
    if isinstance(script_data, dict):
        print(f"📊 Has products: {'products' in script_data}")
        if 'products' in script_data:
            products = script_data['products']
            print(f"📊 Products count: {len(products)}")
            print(f"📊 First product: {products[0] if products else 'None'}")
    
    print(f"\n📝 Full script data:")
    print(json.dumps(script_data, indent=2))

if __name__ == "__main__":
    asyncio.run(debug_script())
