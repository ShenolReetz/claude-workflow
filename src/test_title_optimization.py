#!/usr/bin/env python3
"""Test title optimization functionality"""
import asyncio
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_servers.content_generation_server import ContentGenerationMCPServer

async def test_title_optimization():
    """Test the title optimization with various titles"""
    
    # Load config
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    # Initialize server
    server = ContentGenerationMCPServer(config['anthropic_api_key'])
    
    # Test titles
    test_titles = [
        "Top 5 Best Marine Stereos for Boats 2025",
        "The Ultimate Guide to Satellite TV Systems for RVs",
        "Best Computer Vacuums for Your Workspace",
        "Top Rated Home Security Cameras Under $100",
        "Gaming Keyboards That Will Transform Your Setup"
    ]
    
    print("🎯 Testing Title Optimization\n")
    print("=" * 80)
    
    for title in test_titles:
        print(f"\n📝 Original Title: {title}")
        print(f"   Length: {len(title)} chars")
        
        # Generate keywords first
        print("\n   🔍 Generating SEO keywords...")
        keywords = await server.generate_seo_keywords(title, "Electronics")
        print(f"   Keywords: {', '.join(keywords[:5])}...")
        
        # Optimize title
        print("\n   ✨ Optimizing title...")
        optimized = await server.optimize_title(title, keywords)
        print(f"   Optimized: {optimized}")
        print(f"   Length: {len(optimized)} chars")
        
        # Check if under 60 chars
        if len(optimized) > 60:
            print(f"   ⚠️  WARNING: Title exceeds 60 character limit!")
        else:
            print(f"   ✅ Title is within YouTube Shorts limit")
        
        print("-" * 80)
    
    print("\n✅ Title optimization test completed!")

if __name__ == "__main__":
    asyncio.run(test_title_optimization())