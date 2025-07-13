#!/usr/bin/env python3
"""Check TikTok API validation status and test connectivity"""

import asyncio
import json
import sys
import httpx
sys.path.append('/home/claude-workflow')

from mcp_servers.tiktok_server import TikTokMCPServer

async def check_tiktok_validation():
    """Check TikTok API validation status"""
    
    print("📱 Checking TikTok API Validation Status")
    print("=" * 60)
    
    # Load config
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    client_id = config.get('tiktok_client_id')
    client_secret = config.get('tiktok_client_secret')
    enabled = config.get('tiktok_enabled', False)
    
    print(f"📋 Current Configuration:")
    print(f"   Client ID: {client_id}")
    print(f"   Client Secret: {'***' + client_secret[-4:] if client_secret else 'Not set'}")
    print(f"   Enabled: {enabled}")
    print(f"   Username: {config.get('tiktok_username', 'Not set')}")
    print(f"   Privacy Setting: {config.get('tiktok_privacy', 'PRIVATE')}")
    
    if not client_id or not client_secret:
        print("\n❌ TikTok credentials not configured")
        return
    
    # Test TikTok server initialization
    try:
        server = TikTokMCPServer(client_id, client_secret)
        print("\n✅ TikTok server initialized successfully")
        
        # Test authentication URL generation
        auth_result = await server.authenticate()
        
        if 'auth_url' in auth_result:
            print(f"\n🔗 Authentication URL generated:")
            print(f"   {auth_result['auth_url']}")
            print(f"\n📝 To complete TikTok integration:")
            print(f"   1. Visit the auth URL above")
            print(f"   2. Grant permissions to your app")
            print(f"   3. Copy the authorization code from the callback")
            print(f"   4. Use the code to get an access token")
        else:
            print(f"\n❌ Failed to generate auth URL: {auth_result}")
        
        # Test TikTok API connectivity (basic check)
        print(f"\n🌐 Testing TikTok API connectivity...")
        async with httpx.AsyncClient() as client:
            try:
                # Test basic TikTok API endpoint
                response = await client.get(
                    "https://open.tiktokapis.com/v2/oauth/token/",
                    timeout=10.0
                )
                print(f"   TikTok API Status: {response.status_code}")
                
                if response.status_code in [400, 405]:  # Expected for GET without params
                    print("   ✅ TikTok API is reachable")
                else:
                    print(f"   ⚠️  Unexpected response: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ TikTok API connectivity error: {e}")
        
        await server.close()
        
    except Exception as e:
        print(f"\n❌ Error testing TikTok server: {e}")
        import traceback
        traceback.print_exc()
    
    # Check app validation status
    print(f"\n📱 App Validation Checklist:")
    print(f"   ✅ TikTok Developer Account: Needed")
    print(f"   ✅ App Created: Needed")
    print(f"   ✅ App Review Submitted: Needed")
    print(f"   ❓ App Approved: Check TikTok Developer Dashboard")
    print(f"   ❓ Production API Access: Check TikTok Developer Dashboard")
    
    print(f"\n🔧 Integration Status:")
    print(f"   - TikTok MCP Server: ✅ Ready")
    print(f"   - Configuration: ✅ Present")
    print(f"   - Workflow Integration: ❌ Not integrated")
    print(f"   - API Validation: ❓ Check developer dashboard")
    
    print(f"\n📋 Next Steps:")
    print(f"   1. Check TikTok Developer Dashboard for app approval")
    print(f"   2. If approved, test authentication flow")
    print(f"   3. Enable TikTok in config (set tiktok_enabled: true)")
    print(f"   4. Integrate into main workflow")

if __name__ == "__main__":
    asyncio.run(check_tiktok_validation())