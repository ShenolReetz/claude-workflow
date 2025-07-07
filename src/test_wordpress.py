import asyncio
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.wordpress_mcp import publish_to_wordpress

async def test():
    # Load config
    with open('config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    # Test data
    test_data = {
        'VideoTitle': '🔥 Test Review: Top 5 Gaming Laptops 2025',
        'VideoDescription': 'This is a test post from our automation system to verify WordPress integration.',
        'ProductNo1Title': 'ASUS ROG Strix G15',
        'ProductNo1Description': 'Powerful gaming laptop with RTX 4070.',
        'ProductNo1AffiliateLink': 'https://www.amazon.com/dp/B0TEST123/ref=nosim?tag=reviewch3kr0d-20'
    }
    
    result = await publish_to_wordpress(config, test_data)
    print('Result:', result)

if __name__ == "__main__":
    asyncio.run(test())
