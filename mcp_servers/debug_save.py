import asyncio
import json
import sys
sys.path.append('/app')

from mcp_servers.airtable_server import AirtableMCPServer

async def debug_save():
    with open('/app/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    server = AirtableMCPServer(
        api_key=config['airtable_api_key'],
        base_id=config['airtable_base_id'],
        table_name=config['airtable_table_name']
    )
    
    # Mock content_data like the real workflow
    script_data = {
        "intro": "Test intro",
        "products": [
            {"rank": 5, "name": "Test Product 5", "script": "Test script 5"},
            {"rank": 4, "name": "Test Product 4", "script": "Test script 4"}
        ]
    }
    
    content_data = {
        'keywords': ['test', 'keywords'],
        'optimized_title': 'Test Title',
        'script': script_data  # This should be dict, not string
    }
    
    print(f"🔍 Script type in content_data: {type(content_data['script'])}")
    print(f"🔍 Script is dict: {isinstance(content_data['script'], dict)}")
    
    # Test saving
    result = await server.save_generated_content('rec00Yb60qB6jOXSE', content_data)
    print(f"✅ Save result: {result}")

if __name__ == "__main__":
    asyncio.run(debug_save())
