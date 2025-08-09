#!/usr/bin/env python3
"""
Test WordPress Tag Conversion
==============================

This script tests the WordPress tag name to ID conversion.
"""

import asyncio
import json
import sys
sys.path.append('/home/claude-workflow')

from src.mcp.Production_wordpress_mcp_v2 import ProductionWordPressMCPV2

async def test_tag_conversion():
    """Test converting tag names to IDs"""
    
    # Load config
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    # Initialize WordPress service
    wordpress = ProductionWordPressMCPV2(config)
    
    print("\n🧪 Testing WordPress Tag Conversion")
    print("=" * 60)
    
    # Test tags
    test_tags = ['amazon', 'product review', 'best products', 'technology']
    
    print(f"\nInput tags: {test_tags}")
    
    try:
        # Convert tags to IDs
        tag_ids = await wordpress._get_or_create_tag_ids(test_tags)
        
        print(f"\n✅ Converted tag IDs: {tag_ids}")
        
        # Display mapping
        print("\nTag Mapping:")
        for tag_name, tag_id in zip(test_tags, tag_ids):
            print(f"  '{tag_name}' -> {tag_id}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_simple_post():
    """Test creating a simple post with tags"""
    
    # Load config
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    # Initialize WordPress service
    wordpress = ProductionWordPressMCPV2(config)
    
    print("\n📝 Testing WordPress Post Creation")
    print("=" * 60)
    
    # Test post data
    title = "Test Post - Tag Conversion Fix"
    content = "<p>This is a test post to verify tag conversion is working properly.</p>"
    excerpt = "Testing tag conversion functionality"
    tags = ['test', 'automated', 'workflow']
    
    try:
        result = await wordpress.create_post(
            title=title,
            content=content,
            excerpt=excerpt,
            tags=tags
        )
        
        if result.get('success'):
            print(f"\n✅ Post created successfully!")
            print(f"   URL: {result.get('post_url')}")
            print(f"   ID: {result.get('post_id')}")
        else:
            print(f"\n❌ Failed to create post: {result.get('error')}")
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n🔧 WordPress Tag Conversion Test")
    print("=" * 60)
    
    # Run tests
    loop = asyncio.get_event_loop()
    
    # Test 1: Tag conversion
    print("\nTest 1: Tag Name to ID Conversion")
    success1 = loop.run_until_complete(test_tag_conversion())
    
    if success1:
        # Test 2: Create post with tags
        print("\nTest 2: Create Post with Tags")
        print("Do you want to create a test post? (y/n): ", end='')
        response = input().strip().lower()
        
        if response == 'y':
            success2 = loop.run_until_complete(test_simple_post())
            
            if success2:
                print("\n✅ All tests passed!")
            else:
                print("\n⚠️ Post creation failed but tag conversion works")
        else:
            print("\nSkipping post creation test")
    else:
        print("\n❌ Tag conversion failed - check WordPress credentials")