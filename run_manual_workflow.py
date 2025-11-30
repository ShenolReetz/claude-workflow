#!/usr/bin/env python3
"""
TEMPORARY: Manual Workflow Runner (No Airtable API)
====================================================
Use this while Airtable API is blocked (until Dec 1st reset)

Usage:
    python3 run_manual_workflow.py "Product Title Here" "ASIN12345" "https://amazon.com/dp/ASIN12345"

After completion, manually update Airtable web interface with results.
"""

import asyncio
import json
import sys
from datetime import datetime

sys.path.append('/home/claude-workflow')

from src.mcp.production_remotion_video_generator_strict import production_run_video_creation
from src.mcp.production_wow_video_generator import production_generate_wow_video
from mcp_servers.production_progressive_amazon_scraper_async import ProductionProgressiveAmazonScraper
from src.mcp.production_wordpress_local_media import production_publish_to_wordpress_local

def load_config():
    """Load configuration"""
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        return json.load(f)

async def run_manual_workflow(title: str, asin: str, product_url: str):
    """
    Run workflow manually without Airtable API

    Args:
        title: Product title from Airtable
        asin: Amazon ASIN
        product_url: Full Amazon product URL
    """

    config = load_config()
    start_time = datetime.now()

    print("\n" + "="*80)
    print("🎬 MANUAL WORKFLOW RUNNER (No Airtable API)")
    print("="*80)
    print(f"Title: {title}")
    print(f"ASIN: {asin}")
    print(f"URL: {product_url}")
    print(f"Started: {start_time}")
    print("="*80 + "\n")

    results = {
        'title': title,
        'asin': asin,
        'product_url': product_url,
        'started_at': start_time.isoformat()
    }

    try:
        # Phase 1: Scrape Amazon Product
        print("\n📦 Phase 1: Scraping Amazon Product...")
        scraper = ProductionProgressiveAmazonScraper(config)
        product_data = await scraper.scrape_product_async(product_url)

        if not product_data or 'error' in product_data:
            raise Exception(f"Amazon scraping failed: {product_data.get('error', 'Unknown error')}")

        print(f"✅ Product scraped: {product_data.get('Title', 'N/A')[:50]}...")
        results['product_data'] = product_data

        # Phase 2: Generate Video (Standard or WOW)
        print("\n🎥 Phase 2: Generating Video...")
        video_type = input("Generate (1) Standard or (2) WOW video? [1/2]: ").strip()

        if video_type == "2":
            print("Generating WOW video...")
            video_result = await production_generate_wow_video(
                product_data=product_data,
                config=config
            )
        else:
            print("Generating Standard video...")
            video_result = await production_run_video_creation(
                product_data=product_data,
                config=config
            )

        if not video_result or video_result.get('error'):
            raise Exception(f"Video generation failed: {video_result.get('error', 'Unknown error')}")

        video_path = video_result.get('video_path')
        print(f"✅ Video created: {video_path}")
        results['video_path'] = video_path
        results['video_url'] = f"file://{video_path}"

        # Phase 3: Upload to YouTube
        print("\n📺 Phase 3: Uploading to YouTube...")
        upload_youtube = input("Upload to YouTube? [y/n]: ").strip().lower()

        if upload_youtube == 'y':
            from src.mcp.production_youtube_upload import production_upload_to_youtube

            youtube_result = await production_upload_to_youtube(
                video_path=video_path,
                title=title,
                description=product_data.get('Description', ''),
                config=config
            )

            if youtube_result and not youtube_result.get('error'):
                youtube_url = youtube_result.get('video_url')
                print(f"✅ YouTube: {youtube_url}")
                results['youtube_url'] = youtube_url
            else:
                print(f"⚠️ YouTube upload failed: {youtube_result.get('error', 'Unknown')}")
                results['youtube_error'] = youtube_result.get('error')

        # Phase 4: Publish to WordPress
        print("\n📝 Phase 4: Publishing to WordPress...")
        publish_wp = input("Publish to WordPress? [y/n]: ").strip().lower()

        if publish_wp == 'y':
            wp_result = await production_publish_to_wordpress_local(
                product_data=product_data,
                video_path=video_path,
                config=config
            )

            if wp_result and not wp_result.get('error'):
                wp_url = wp_result.get('post_url')
                print(f"✅ WordPress: {wp_url}")
                results['wordpress_url'] = wp_url
            else:
                print(f"⚠️ WordPress publish failed: {wp_result.get('error', 'Unknown')}")
                results['wordpress_error'] = wp_result.get('error')

        # Phase 5: Instagram (if implemented)
        print("\n📱 Phase 5: Instagram Reels...")
        print("⚠️ Instagram upload not yet implemented")
        results['instagram_url'] = None

        # Completion
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        results['completed_at'] = end_time.isoformat()
        results['duration_seconds'] = duration
        results['status'] = 'success'

        print("\n" + "="*80)
        print("🎉 WORKFLOW COMPLETED SUCCESSFULLY!")
        print("="*80)
        print(f"Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
        print(f"\n📹 Video: {video_path}")
        if results.get('youtube_url'):
            print(f"📺 YouTube: {results['youtube_url']}")
        if results.get('wordpress_url'):
            print(f"📝 WordPress: {results['wordpress_url']}")
        print("\n" + "="*80)

        # Save results to file
        results_file = f"/home/claude-workflow/manual_workflow_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\n💾 Results saved to: {results_file}")

        # Instructions for manual Airtable update
        print("\n" + "="*80)
        print("📋 MANUAL AIRTABLE UPDATE REQUIRED")
        print("="*80)
        print("\nGo to: https://airtable.com/appTtNBJ8dAnjvkPP/tblhGDEW6eUbmaYZx")
        print(f"\nFind record with Title: {title}")
        print("\nUpdate these fields:")
        print(f"  - Status: Completed")
        print(f"  - FinalVideo: {results.get('video_url', 'N/A')}")
        if results.get('youtube_url'):
            print(f"  - YouTubeURL: {results['youtube_url']}")
        if results.get('wordpress_url'):
            print(f"  - WordPressURL: {results['wordpress_url']}")
        print(f"  - CompletedAt: {end_time.isoformat()}")
        print(f"  - ProcessingTime: {duration:.1f} seconds")
        print("="*80 + "\n")

        return results

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

        results['status'] = 'failed'
        results['error'] = str(e)
        return results

def main():
    """Main entry point"""

    if len(sys.argv) < 4:
        print("\n" + "="*80)
        print("🎬 MANUAL WORKFLOW RUNNER")
        print("="*80)
        print("\nUsage:")
        print('  python3 run_manual_workflow.py "Title" "ASIN" "https://amazon.com/dp/ASIN"')
        print("\nExample:")
        print('  python3 run_manual_workflow.py \\')
        print('    "Wireless Gaming Mouse RGB" \\')
        print('    "B0CXJ1XYZZ" \\')
        print('    "https://www.amazon.com/dp/B0CXJ1XYZZ"')
        print("\nSteps:")
        print("  1. Go to Airtable: https://airtable.com/appTtNBJ8dAnjvkPP/tblhGDEW6eUbmaYZx")
        print("  2. Copy a Pending title's: Title, ASIN, and ProductURL")
        print("  3. Run this script with those values")
        print("  4. After completion, manually update Airtable with results")
        print("\n" + "="*80 + "\n")
        sys.exit(1)

    title = sys.argv[1]
    asin = sys.argv[2]
    product_url = sys.argv[3]

    # Run workflow
    asyncio.run(run_manual_workflow(title, asin, product_url))

if __name__ == "__main__":
    main()
