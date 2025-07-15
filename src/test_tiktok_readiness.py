#!/usr/bin/env python3
"""
Test TikTok Integration Readiness - Verify implementation is ready for activation
"""

import asyncio
import json
import sys
sys.path.append('/home/claude-workflow')

from mcp.tiktok_workflow_integration import TikTokWorkflowIntegration

async def test_tiktok_readiness():
    """Test TikTok integration readiness for when API is approved"""
    print("📱 TikTok Integration Readiness Test")
    print("=" * 50)
    
    # Load config
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    # Sample Airtable record
    test_record = {
        'VideoTitle': '🔥 Top 5 Gaming Headsets You NEED in 2025! 🎮',
        'VideoURL': 'https://example.com/test-video.mp4',
        'TikTokKeywords': 'gaming,headsets,tech,viral,musthave',
        'ProductNo1Title': 'SteelSeries Arctis Nova Pro',
        'ProductNo2Title': 'Razer BlackShark V2 Pro',
        'record_id': 'test123'
    }
    
    integration = TikTokWorkflowIntegration(config)
    
    print("\n1️⃣ Configuration Status:")
    print(f"   - TikTok enabled: {'✅' if integration.enabled else '❌'}")
    print(f"   - Client ID: {config.get('tiktok_client_id', 'Missing')}")
    print(f"   - Client Secret: {'✅ Set' if config.get('tiktok_client_secret') else '❌ Missing'}")
    print(f"   - Username: {config.get('tiktok_username', 'Not set')}")
    print(f"   - Privacy Level: {config.get('tiktok_privacy', 'PRIVATE')}")
    
    print("\n2️⃣ Title Generation Test:")
    title = integration._generate_tiktok_title(test_record)
    print(f"   - Generated title: {title}")
    print(f"   - Length: {len(title)}/150 characters")
    print(f"   - Contains #fyp: {'✅' if '#fyp' in title else '❌'}")
    print(f"   - Uses keywords: {'✅' if any(kw in title.lower() for kw in ['gaming', 'headsets', 'tech']) else '❌'}")
    
    print("\n3️⃣ Integration Components:")
    print(f"   - MCP Server: {'✅ Implemented' if integration.server else '❌ Missing'}")
    print(f"   - Upload method: {'✅ Ready' if hasattr(integration, 'upload_video_to_tiktok') else '❌ Missing'}")
    print(f"   - Status check: {'✅ Ready' if hasattr(integration, 'check_upload_status') else '❌ Missing'}")
    
    print("\n4️⃣ Workflow Integration:")
    # Check if workflow has TikTok section (commented out)
    with open('/home/claude-workflow/src/workflow_runner.py', 'r') as f:
        workflow_content = f.read()
    
    has_tiktok_section = 'TikTok Upload - TEMPORARILY DISABLED' in workflow_content
    has_commented_code = 'upload_to_tiktok' in workflow_content
    
    print(f"   - Workflow section: {'✅ Commented out' if has_tiktok_section else '❌ Missing'}")
    print(f"   - Upload code: {'✅ Ready to uncomment' if has_commented_code else '❌ Missing'}")
    
    print("\n5️⃣ Test Upload Simulation:")
    # Simulate upload (will show disabled status)
    result = await integration.upload_video_to_tiktok(test_record)
    print(f"   - Upload result: {result}")
    
    await integration.close()
    
    print("\n6️⃣ Activation Requirements:")
    requirements = []
    if not config.get('tiktok_client_id'):
        requirements.append("Set tiktok_client_id in config")
    if not config.get('tiktok_client_secret'):
        requirements.append("Set tiktok_client_secret in config")
    if not config.get('tiktok_access_token'):
        requirements.append("Obtain access token after API approval")
    
    if requirements:
        print("   ❌ Missing requirements:")
        for req in requirements:
            print(f"      - {req}")
    else:
        print("   ✅ All requirements ready!")
    
    print("\n7️⃣ Readiness Summary:")
    ready_components = [
        integration.server is not None,
        hasattr(integration, 'upload_video_to_tiktok'),
        has_tiktok_section,
        has_commented_code,
        bool(config.get('tiktok_client_id')),
        bool(config.get('tiktok_client_secret'))
    ]
    
    ready_count = sum(ready_components)
    total_count = len(ready_components)
    
    print(f"   - Ready components: {ready_count}/{total_count}")
    print(f"   - Implementation: {'✅ Complete' if ready_count == total_count else '⚠️ Partial'}")
    
    if ready_count == total_count:
        print("\n🎉 TikTok integration is fully ready!")
        print("   📋 Next steps:")
        print("   1. Wait for TikTok API approval")
        print("   2. Complete authentication flow")
        print("   3. Set tiktok_enabled: true in config")
        print("   4. Uncomment workflow code")
        print("   5. Test and go live!")
    else:
        print("\n⚠️ TikTok integration needs attention before activation")
    
    return {
        'ready': ready_count == total_count,
        'ready_components': ready_count,
        'total_components': total_count,
        'missing_requirements': requirements
    }

if __name__ == "__main__":
    result = asyncio.run(test_tiktok_readiness())
    print("\n" + "=" * 50)
    print("Test complete!")