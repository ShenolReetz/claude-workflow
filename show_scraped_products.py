#!/usr/bin/env python3
"""
Show all scraped products in detail
"""
import asyncio
import aiohttp
import json
import time

async def show_all_products():
    """Show all scraped products with details"""
    
    scrapingdog_api_key = "685b2b45ce0d20b7a6a43a6f"
    base_url = "https://api.scrapingdog.com/amazon/search"
    search_query = "New Laptop Sleeves Releases"
    
    params = {
        'api_key': scrapingdog_api_key,
        'domain': 'com', 
        'query': search_query,
        'page': '1',
        'country': 'us'
    }
    
    print(f"🔍 Scraping Amazon for: {search_query}")
    print("=" * 80)
    
    start_time = time.time()
    
    async with aiohttp.ClientSession() as session:
        async with session.get(base_url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                products = data.get('results', [])
                
                request_time = time.time() - start_time
                print(f"⏰ Scraped {len(products)} products in {request_time:.2f} seconds")
                print("=" * 80)
                
                for i, product in enumerate(products, 1):
                    title = product.get('title', 'N/A')
                    price = product.get('price', 'N/A')
                    stars = product.get('stars', 'N/A')
                    reviews = product.get('total_reviews', 'N/A')
                    prime = "✓" if product.get('has_prime', False) else "✗"
                    best_seller = "🏆" if product.get('is_best_seller', False) else ""
                    amazon_choice = "🎖️" if product.get('is_amazon_choice', False) else ""
                    
                    print(f"{i:2}. {title[:60]}...")
                    print(f"    💰 {price} | ⭐ {stars}/5 ({reviews} reviews) | Prime: {prime} {best_seller} {amazon_choice}")
                    print()
                    
                # Filter by reviews (10+)
                qualified = [p for p in products if p.get('total_reviews', '0').replace(',', '').isdigit() and int(p.get('total_reviews', '0').replace(',', '')) >= 10]
                print(f"✅ Products with 10+ reviews: {len(qualified)}")
                
                # Show top 5 by rating and reviews
                def score_product(p):
                    try:
                        stars = float(p.get('stars', 0))
                        reviews = int(p.get('total_reviews', '0').replace(',', ''))
                        return stars * 100 + (reviews / 1000)
                    except:
                        return 0
                
                top5 = sorted(qualified, key=score_product, reverse=True)[:5]
                print("\n🏆 TOP 5 RANKING (by rating + review count):")
                print("=" * 60)
                
                for i, product in enumerate(top5, 1):
                    title = product.get('title', 'N/A')
                    price = product.get('price', 'N/A')
                    stars = product.get('stars', 'N/A')
                    reviews = product.get('total_reviews', 'N/A')
                    score = score_product(product)
                    
                    print(f"🥇 No{i}: {title[:50]}...")
                    print(f"   ⭐ {stars}/5.0 stars | 📊 {reviews} reviews | 💰 {price} | Score: {score:.1f}")
                    print()

if __name__ == "__main__":
    asyncio.run(show_all_products())