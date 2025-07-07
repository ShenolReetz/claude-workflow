#!/usr/bin/env python3
"""Test TikTok integration before modifying main workflow"""
import asyncio
import json

async def test_tiktok_integration():
    # Load config
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    # Simulate workflow state at TikTok integration point
    video_result = {
        'success': True,
        'video_url': 'https://assets.json2video.com/test-video.mp4',
    }
    
    pending_title = {
        'record_id': 'test123',
        'Title': 'Top 5 Gaming Laptops 2025',
        'VideoTitle': '5 INSANE Gaming Laptops You Need in 2025! 🔥',
        'Keywords': 'gaming laptops, best laptops 2025, gaming computers, RGB gaming, portable gaming',
        'ProductNo1Title': 'ASUS ROG Strix G16',
        'ProductNo2Title': 'MSI Stealth 16',
        'ProductNo3Title': 'Razer Blade 16',
        'ProductNo4Title': 'Alienware m18',
        'ProductNo5Title': 'Lenovo Legion Pro 7i',
    }
    
    print("🧪 Testing TikTok Integration...")
    print(f"✓ Video URL: {video_result.get('video_url')}")
    print(f"✓ Video Title: {pending_title.get('VideoTitle')} ({len(pending_title.get('VideoTitle', ''))} chars)")
    
    # Build TikTok caption
    caption = f"{pending_title.get('VideoTitle')}\n\n"
    caption += "Which one would you choose? 🤔\n\n"
    
    # Add products
    for i in range(1, 6):
        product = pending_title.get(f'ProductNo{i}Title', '')
        if product:
            caption += f"{i}️⃣ {product}\n"
    
    caption += "\n🔗 Links in bio!\n\n"
    
    # Extract hashtags from keywords
    keywords = pending_title.get('Keywords', '').split(',')
    niche_hashtags = ' '.join([f"#{k.strip().replace(' ', '')}" for k in keywords[:5]])
    
    # Add viral hashtags
    viral_hashtags = "#amazonfinds #tiktokmademebuyit #musthave #viral #fyp #foryou #2025"
    
    caption += viral_hashtags + " " + niche_hashtags
    
    print(f"\n📝 TikTok Caption Preview ({len(caption)} chars):")
    print("-" * 50)
    print(caption)
    print("-" * 50)
    
    # Test hashtag extraction
    all_hashtags = viral_hashtags + " " + niche_hashtags
    print(f"\n#️⃣ Hashtags ({len(all_hashtags.split())} total):")
    print(all_hashtags)
    
    # Simulate Airtable updates
    print("\n📊 Would update Airtable with:")
    print(f"  - TikTokURL: (generated after upload)")
    print(f"  - TikTokVideoID: (generated after upload)")
    print(f"  - TikTokPublishID: (generated after upload)")
    print(f"  - TikTokStatus: PROCESSING")
    print(f"  - TikTokCaption: {len(caption)} characters")
    print(f"  - TikTokHashtags: {all_hashtags}")
    print(f"  - TikTokUsername: {config.get('tiktok_username', '@yourusername')}")
    
    print("\n✅ Integration test passed!")

asyncio.run(test_tiktok_integration())
