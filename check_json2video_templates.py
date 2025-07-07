#!/usr/bin/env python3
import httpx
import json
import asyncio
import sys

async def check_templates(api_key):
    """Check available templates in JSON2Video"""
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print("🔍 Checking JSON2Video API...")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Try different endpoints to find templates
        endpoints = [
            "/v2/templates",
            "/v1/templates", 
            "/templates",
            "/v2/movies/templates"
        ]
        
        base_url = "https://api.json2video.com"
        
        for endpoint in endpoints:
            try:
                print(f"\n📡 Trying: {base_url}{endpoint}")
                response = await client.get(f"{base_url}{endpoint}", headers=headers)
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Success! Found data:")
                    print(json.dumps(data, indent=2)[:500] + "...")
                    return data
                else:
                    print(f"   ❌ {response.text[:100]}")
                    
            except Exception as e:
                print(f"   ⚠️ Error: {str(e)}")
        
        # Also try to get account info
        print("\n📡 Checking account info...")
        try:
            response = await client.get(f"{base_url}/v2/account", headers=headers)
            if response.status_code == 200:
                print("✅ Account info:")
                print(json.dumps(response.json(), indent=2))
        except Exception as e:
            print(f"⚠️ Error getting account info: {e}")

if __name__ == "__main__":
    # Load config
    try:
        with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
            config = json.load(f)
            api_key = config.get('json2video_api_key')
            
        if not api_key:
            print("❌ ERROR: JSON2Video API key not found!")
            sys.exit(1)
            
        print(f"🔑 Using API key: {api_key[:10]}...{api_key[-4:]}")
        asyncio.run(check_templates(api_key))
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
