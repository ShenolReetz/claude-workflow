#!/usr/bin/env python3
"""
Debug script to show exactly what's happening during scraping
"""
import asyncio
import aiohttp
import json
import time
from urllib.parse import quote

async def debug_amazon_scraping():
    """Debug the Amazon scraping process with detailed timing"""
    
    scrapingdog_api_key = "685b2b45ce0d20b7a6a43a6f"  # From config
    base_url = "https://api.scrapingdog.com/amazon/search"
    
    search_query = "New Laptop Sleeves Releases"
    
    print(f"🔍 DEBUG: Starting Amazon scraping test...")
    print(f"📋 Search query: {search_query}")
    print(f"🌐 API URL: {base_url}")
    print(f"🔑 API Key: {scrapingdog_api_key[:10]}...")
    
    params = {
        'api_key': scrapingdog_api_key,
        'domain': 'com', 
        'query': search_query,
        'page': '1',
        'country': 'us'
    }
    
    print(f"📝 Request parameters: {json.dumps(params, indent=2)}")
    
    start_time = time.time()
    print(f"⏰ Making API request at {time.strftime('%H:%M:%S')}")
    
    try:
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(base_url, params=params) as response:
                request_time = time.time() - start_time
                print(f"⏰ API response received in {request_time:.2f} seconds")
                print(f"📊 Status Code: {response.status}")
                print(f"🔧 Content-Type: {response.headers.get('content-type', 'N/A')}")
                
                if response.status == 200:
                    response_text = await response.text()
                    print(f"📏 Response length: {len(response_text)} characters")
                    print(f"📋 First 500 characters:")
                    print("-" * 50)
                    print(response_text[:500])
                    print("-" * 50)
                    
                    # Try to parse as JSON
                    try:
                        data = json.loads(response_text)
                        print(f"✅ JSON parsing successful")
                        print(f"🔍 Response type: {type(data)}")
                        
                        if isinstance(data, dict):
                            print(f"📋 Dictionary keys: {list(data.keys())}")
                            if 'results' in data:
                                products = data['results']
                                print(f"🛍️ Found {len(products)} products")
                                
                                # Show first product details
                                if products:
                                    first_product = products[0]
                                    print(f"🔍 First product sample:")
                                    for key, value in first_product.items():
                                        print(f"   {key}: {str(value)[:100]}")
                                        
                        elif isinstance(data, list):
                            print(f"📋 List with {len(data)} items")
                            
                    except json.JSONDecodeError as e:
                        print(f"❌ JSON decode error: {e}")
                        print(f"❌ Raw response: {response_text}")
                        
                else:
                    print(f"❌ HTTP Error {response.status}")
                    error_text = await response.text()
                    print(f"❌ Error response: {error_text}")
                    
    except Exception as e:
        print(f"❌ Request error: {e}")
        print(f"❌ Error type: {type(e)}")

if __name__ == "__main__":
    asyncio.run(debug_amazon_scraping())