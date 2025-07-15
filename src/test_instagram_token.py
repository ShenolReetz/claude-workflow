#!/usr/bin/env python3
"""
Test Instagram Token Management and Integration
"""

import asyncio
import json
import sys
sys.path.append('/home/claude-workflow')

from instagram_token_manager import InstagramTokenManager

async def test_instagram_token():
    """Test Instagram token management"""
    print("📸 Instagram Token Management Test")
    print("=" * 50)
    
    manager = InstagramTokenManager()
    
    # Step 1: Check current token status
    print("\n1️⃣ Checking current token status...")
    status = await manager.check_token_status()
    print(json.dumps(status, indent=2))
    
    if not status.get('has_token'):
        print("\n⚠️  No Instagram token found!")
        print("\n📝 To authenticate:")
        print("   1. Get the auth URL:")
        auth_url = await manager.get_auth_url()
        print(f"      {auth_url}")
        print("\n   2. Visit the URL and authorize the app")
        print("   3. Copy the code from the redirect URL")
        print("   4. Run: python3 src/instagram_token_manager.py authenticate --code YOUR_CODE")
        return
    
    # Step 2: Validate token
    print("\n2️⃣ Validating current token...")
    validation = await manager.validate_token()
    print(json.dumps(validation, indent=2))
    
    if not validation.get('valid'):
        print("\n❌ Token is invalid or expired!")
        print("   Please re-authenticate using the steps above.")
        return
    
    # Step 3: Check if refresh is needed
    if status.get('cached_data', {}).get('needs_refresh'):
        print("\n3️⃣ Token needs refresh...")
        refresh_result = await manager.refresh_token()
        print(json.dumps(refresh_result, indent=2))
    else:
        print("\n✅ Token is still valid and doesn't need refresh")
    
    # Step 4: Test Instagram integration
    print("\n4️⃣ Testing Instagram integration readiness...")
    
    # Load config to check if enabled
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    instagram_enabled = config.get('instagram_enabled', False)
    
    print(f"\n📊 Instagram Integration Status:")
    print(f"   - Enabled in config: {'✅' if instagram_enabled else '❌'}")
    print(f"   - Has valid token: {'✅' if validation.get('valid') else '❌'}")
    print(f"   - Username: @{validation.get('username', 'unknown')}")
    print(f"   - User ID: {validation.get('user_id', 'unknown')}")
    
    if status.get('cached_data'):
        cache = status['cached_data']
        print(f"   - Token expires: {cache.get('expires_at', 'unknown')}")
        print(f"   - Days remaining: {cache.get('days_remaining', 'unknown')}")
    
    print("\n✅ Summary:")
    if instagram_enabled and validation.get('valid'):
        print("   Instagram is ready for use in the workflow!")
    else:
        issues = []
        if not instagram_enabled:
            issues.append("Enable Instagram in config (set instagram_enabled: true)")
        if not validation.get('valid'):
            issues.append("Authenticate with Instagram to get a valid token")
        
        print("   Instagram needs setup:")
        for issue in issues:
            print(f"   - {issue}")
    
    return {
        'ready': instagram_enabled and validation.get('valid'),
        'enabled': instagram_enabled,
        'valid_token': validation.get('valid'),
        'username': validation.get('username'),
        'user_id': validation.get('user_id')
    }


if __name__ == "__main__":
    result = asyncio.run(test_instagram_token())
    print("\n" + "=" * 50)
    print("Test complete!")