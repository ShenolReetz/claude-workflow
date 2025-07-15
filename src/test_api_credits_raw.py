#!/usr/bin/env python3
"""
Test API Credits - Raw Response Testing
"""

import asyncio
import httpx
import json
import sys
sys.path.append('/home/claude-workflow')

async def test_json2video_credits():
    """Test JSON2Video API credits endpoint"""
    
    # Load config
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    api_key = config.get('json2video_api_key')
    if not api_key:
        print("❌ No JSON2Video API key found")
        return
    
    print("🎬 Testing JSON2Video API Credits")
    print("=" * 50)
    print(f"API Key: {api_key[:20]}...")
    
    client = httpx.AsyncClient(timeout=30.0)
    
    try:
        # Test different endpoints
        endpoints = [
            ("Account Info", "https://api.json2video.com/v2/account"),
            ("User Info", "https://api.json2video.com/v2/user"),
            ("Credits", "https://api.json2video.com/v2/credits"),
            ("Projects", "https://api.json2video.com/v2/projects")
        ]
        
        headers = {
            'x-api-key': api_key,
            'Content-Type': 'application/json'
        }
        
        for name, url in endpoints:
            print(f"\n🔍 Testing {name}: {url}")
            
            try:
                response = await client.get(url, headers=headers)
                print(f"   Status: {response.status_code}")
                print(f"   Headers: {dict(response.headers)}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"   Response: {json.dumps(data, indent=2)}")
                    except:
                        print(f"   Raw Text: {response.text}")
                else:
                    print(f"   Error: {response.text}")
                    
            except Exception as e:
                print(f"   Exception: {e}")
                
    finally:
        await client.aclose()


async def test_scrapingdog_credits():
    """Test ScrapingDog API credits endpoint"""
    
    # Load config
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    api_key = config.get('scrapingdog_api_key')
    if not api_key:
        print("❌ No ScrapingDog API key found")
        return
    
    print("\n🐕 Testing ScrapingDog API Credits")
    print("=" * 50)
    print(f"API Key: {api_key[:20]}...")
    
    client = httpx.AsyncClient(timeout=30.0)
    
    try:
        # Test different endpoints
        endpoints = [
            ("Account Info", f"https://api.scrapingdog.com/account?api_key={api_key}"),
            ("Usage", f"https://api.scrapingdog.com/usage?api_key={api_key}"),
            ("Balance", f"https://api.scrapingdog.com/balance?api_key={api_key}")
        ]
        
        for name, url in endpoints:
            print(f"\n🔍 Testing {name}: {url.replace(api_key, 'API_KEY')}")
            
            try:
                response = await client.get(url)
                print(f"   Status: {response.status_code}")
                print(f"   Headers: {dict(response.headers)}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"   Response: {json.dumps(data, indent=2)}")
                    except:
                        print(f"   Raw Text: {response.text}")
                else:
                    print(f"   Error: {response.text}")
                    
            except Exception as e:
                print(f"   Exception: {e}")
                
    finally:
        await client.aclose()


async def test_openai_credits():
    """Test OpenAI API credits endpoint"""
    
    # Load config
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    api_key = config.get('openai_api_key')
    if not api_key:
        print("❌ No OpenAI API key found")
        return
    
    print("\n🤖 Testing OpenAI API Credits")
    print("=" * 50)
    print(f"API Key: {api_key[:20]}...")
    
    client = httpx.AsyncClient(timeout=30.0)
    
    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        # Test different endpoints
        endpoints = [
            ("Usage", "https://api.openai.com/v1/usage"),
            ("Billing", "https://api.openai.com/v1/dashboard/billing/subscriptions"),
            ("Organizations", "https://api.openai.com/v1/organizations"),
            ("Models", "https://api.openai.com/v1/models")
        ]
        
        for name, url in endpoints:
            print(f"\n🔍 Testing {name}: {url}")
            
            try:
                response = await client.get(url, headers=headers)
                print(f"   Status: {response.status_code}")
                print(f"   Headers: {dict(response.headers)}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if name == "Models":
                            print(f"   Response: Found {len(data.get('data', []))} models")
                        else:
                            print(f"   Response: {json.dumps(data, indent=2)}")
                    except:
                        print(f"   Raw Text: {response.text}")
                else:
                    print(f"   Error: {response.text}")
                    
            except Exception as e:
                print(f"   Exception: {e}")
                
    finally:
        await client.aclose()


async def main():
    """Run all API credit tests"""
    
    print("🔍 API Credits Raw Response Testing")
    print("=" * 60)
    
    await test_json2video_credits()
    await test_scrapingdog_credits()
    await test_openai_credits()
    
    print("\n" + "=" * 60)
    print("✅ API testing complete!")


if __name__ == "__main__":
    asyncio.run(main())