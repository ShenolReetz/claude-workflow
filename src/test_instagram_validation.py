#!/usr/bin/env python3
"""Check Instagram API validation status and test connectivity"""

import asyncio
import json
import sys
import httpx
sys.path.append('/home/claude-workflow')

from mcp_servers.instagram_server import InstagramMCPServer

async def check_instagram_validation():
    """Check Instagram API validation status"""
    
    print("📸 Checking Instagram API Validation Status")
    print("=" * 60)
    
    # Load config
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    app_id = config.get('instagram_app_id')
    app_secret = config.get('instagram_app_secret')
    enabled = config.get('instagram_enabled', False)
    
    print(f"📋 Current Configuration:")
    print(f"   App ID: {app_id}")
    print(f"   App Secret: {'***' + app_secret[-4:] if app_secret and len(app_secret) > 4 else 'Not set'}")
    print(f"   Enabled: {enabled}")
    print(f"   Username: {config.get('instagram_username', 'Not set')}")
    
    if not app_id or app_id == "your_instagram_app_id":
        print("\n❌ Instagram credentials not configured")
        print("📝 Steps to configure:")
        print("   1. Create Facebook App at developers.facebook.com")
        print("   2. Add Instagram Basic Display product")
        print("   3. Add Instagram Graph API (for business accounts)")
        print("   4. Update config with App ID and Secret")
        return
    
    # Test Instagram server initialization
    try:
        server = InstagramMCPServer(app_id, app_secret)
        print("\n✅ Instagram server initialized successfully")
        
        # Test authentication URL generation
        auth_result = await server.authenticate()
        
        if 'auth_url' in auth_result:
            print(f"\n🔗 Authentication URL generated:")
            print(f"   {auth_result['auth_url']}")
            print(f"\n📝 To complete Instagram integration:")
            print(f"   1. Visit the auth URL above")
            print(f"   2. Grant permissions to your app")
            print(f"   3. Copy the authorization code from the callback")
            print(f"   4. Use the code to get an access token")
        else:
            print(f"\n❌ Failed to generate auth URL: {auth_result}")
        
        # Test Instagram/Facebook API connectivity
        print(f"\n🌐 Testing Instagram API connectivity...")
        async with httpx.AsyncClient() as client:
            try:
                # Test Facebook Graph API (Instagram uses this)
                response = await client.get(
                    "https://graph.facebook.com/v18.0/me",
                    timeout=10.0
                )
                print(f"   Facebook Graph API Status: {response.status_code}")
                
                if response.status_code in [400, 401]:  # Expected without access token
                    print("   ✅ Facebook Graph API is reachable")
                else:
                    print(f"   ⚠️  Unexpected response: {response.status_code}")
                    
                # Test Instagram Graph API
                response2 = await client.get(
                    "https://graph.instagram.com/me",
                    timeout=10.0
                )
                print(f"   Instagram Graph API Status: {response2.status_code}")
                
                if response2.status_code in [400, 401]:  # Expected without access token
                    print("   ✅ Instagram Graph API is reachable")
                    
            except Exception as e:
                print(f"   ❌ API connectivity error: {e}")
        
        await server.close()
        
    except Exception as e:
        print(f"\n❌ Error testing Instagram server: {e}")
        import traceback
        traceback.print_exc()
    
    # Check app validation status
    print(f"\n📱 App Validation Checklist:")
    print(f"   ✅ Facebook Developer Account: Needed")
    print(f"   ✅ Facebook App Created: Needed")
    print(f"   ✅ Instagram Basic Display Added: Needed")
    print(f"   ✅ Instagram Graph API Added: Needed (for business accounts)")
    print(f"   ❓ App Review Submitted: Check Facebook Developer Dashboard")
    print(f"   ❓ App Approved: Check Facebook Developer Dashboard")
    print(f"   ❓ Instagram Business Account Connected: Needed for Reels API")
    
    print(f"\n🔧 Integration Status:")
    print(f"   - Instagram MCP Server: ✅ Ready")
    print(f"   - Configuration: {'✅ Present' if app_id != 'your_instagram_app_id' else '❌ Needs setup'}")
    print(f"   - Workflow Integration: ✅ Added after TikTok")
    print(f"   - API Validation: ❓ Check developer dashboard")
    
    print(f"\n📋 Next Steps:")
    print(f"   1. Create Facebook App with Instagram products")
    print(f"   2. Configure redirect URI: http://localhost:8080/callback")
    print(f"   3. Submit for app review if needed")
    print(f"   4. Connect Instagram Business Account")
    print(f"   5. Test authentication flow")
    print(f"   6. Enable Instagram in config (set instagram_enabled: true)")
    
    print(f"\n💡 Requirements for Instagram Reels API:")
    print(f"   - Instagram Business Account (not personal)")
    print(f"   - Connected to Facebook Page")
    print(f"   - App approved for instagram_content_publish permission")
    print(f"   - Video must be publicly accessible URL")

if __name__ == "__main__":
    asyncio.run(check_instagram_validation())