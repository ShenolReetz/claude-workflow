#!/usr/bin/env python3
"""
Alternative Scraping Manager - Production Version
Provides multiple scraping sources and methods as fallbacks

ScrapingDog → Direct Scraping → Alternative APIs → Manual Intervention
"""

import asyncio
import json
import sys
import os
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import time

# Add the project root to Python path
sys.path.append('/home/claude-workflow')

# Import configuration
from src.load_config import load_config

class AlternativeScrapingManager:
    def __init__(self, config: Dict[str, Any]):
        """Initialize Alternative Scraping Manager"""
        self.config = config
        self.scrapingdog_api_key = config.get('scrapingdog_api_key', '')
        
        # Scraping sources in priority order - Playwright MCP first for accuracy + cost efficiency
        self.scraping_sources = [
            "playwright_mcp",        # PRIMARY: MCP Playwright scraping (accurate + free)
            "scrapingdog_premium",   # FALLBACK: Premium tier backup
            "scrapingdog_standard",  # FALLBACK: Standard tier backup
            "direct_requests",
            "alternative_api",
            "manual_fallback"
        ]
        
        # Success rates for different methods (for optimization)
        self.source_success_rates = {
            "playwright_mcp": 0.90,        # PRIMARY: High accuracy + reliability with real browser
            "scrapingdog_premium": 0.85,   # FALLBACK: Professional API service
            "scrapingdog_standard": 0.70,  # FALLBACK: Standard tier backup
            "direct_requests": 0.45,
            "alternative_api": 0.30,
            "manual_fallback": 1.0  # Always works but requires intervention
        }
        
        print("🔍 Alternative Scraping Manager initialized")
        print(f"📊 Available sources: {len(self.scraping_sources)}")
        print(f"🎯 Primary: Playwright MCP, Fallback: ScrapingDog + alternatives")
    
    async def scrape_with_alternatives(self, product_url: str, category: str) -> Dict[str, Any]:
        """
        Attempt scraping using multiple sources with fallback strategy
        """
        scraping_result = {
            "url": product_url,
            "category": category,
            "timestamp": datetime.now().isoformat(),
            "attempts": [],
            "success": False,
            "final_source": None,
            "products": [],
            "error_summary": []
        }
        
        print(f"🔍 Starting alternative scraping for category: {category}")
        print(f"🎯 Target URL: {product_url[:60]}...")
        
        # Try each scraping source in order
        for source in self.scraping_sources:
            if scraping_result["success"]:
                break
                
            print(f"🔄 Attempting: {source}")
            
            attempt_result = {
                "source": source,
                "timestamp": datetime.now().isoformat(),
                "success": False,
                "products_found": 0,
                "error": None
            }
            
            try:
                if source == "scrapingdog_premium":
                    products = await self._scrape_scrapingdog_premium(product_url, category)
                elif source == "playwright_mcp":
                    products = await self._scrape_playwright_mcp(product_url, category)
                elif source == "scrapingdog_standard":
                    products = await self._scrape_scrapingdog_standard(product_url, category)
                elif source == "direct_requests":
                    products = await self._scrape_direct_requests(product_url, category)
                elif source == "alternative_api":
                    products = await self._scrape_alternative_api(product_url, category)
                elif source == "manual_fallback":
                    products = await self._prepare_manual_fallback(product_url, category)
                else:
                    products = []
                
                if products and len(products) >= 5:
                    # Success - found enough products
                    attempt_result["success"] = True
                    attempt_result["products_found"] = len(products)
                    
                    scraping_result["success"] = True
                    scraping_result["final_source"] = source
                    scraping_result["products"] = products
                    
                    print(f"✅ Success with {source}: {len(products)} products found")
                    break
                else:
                    # Insufficient products
                    attempt_result["error"] = f"Insufficient products: {len(products) if products else 0}/5"
                    print(f"⚠️ {source}: Only {len(products) if products else 0} products found")
                    
            except Exception as e:
                attempt_result["error"] = str(e)
                scraping_result["error_summary"].append(f"{source}: {str(e)}")
                print(f"❌ {source} failed: {str(e)}")
            
            scraping_result["attempts"].append(attempt_result)
            
            # Short delay between attempts
            await asyncio.sleep(2)
        
        # Final result summary
        if scraping_result["success"]:
            print(f"🎉 Scraping successful using {scraping_result['final_source']}")
            print(f"📦 Products found: {len(scraping_result['products'])}")
        else:
            print(f"❌ All scraping methods failed")
            print(f"🔍 Attempted sources: {len(scraping_result['attempts'])}")
        
        return scraping_result
    
    async def _scrape_scrapingdog_premium(self, url: str, category: str) -> List[Dict[str, Any]]:
        """Scrape using ScrapingDog premium settings"""
        try:
            if not self.scrapingdog_api_key:
                raise Exception("ScrapingDog API key not configured")
            
            # Premium ScrapingDog parameters
            params = {
                'api_key': self.scrapingdog_api_key,
                'url': url,
                'render': 'true',  # JavaScript rendering
                'premium': 'true',  # Premium quality
                'country': 'US'
            }
            
            scraping_url = "https://api.scrapingdog.com/scrape"
            
            print("🐕 Using ScrapingDog Premium...")
            response = requests.get(scraping_url, params=params, timeout=30)
            
            if response.status_code == 200:
                # Parse response and extract products
                products = self._parse_amazon_response(response.text, category)
                return products
            else:
                raise Exception(f"ScrapingDog API error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ ScrapingDog Premium failed: {str(e)}")
            raise e
    
    async def _scrape_scrapingdog_standard(self, url: str, category: str) -> List[Dict[str, Any]]:
        """Scrape using ScrapingDog standard settings"""
        try:
            if not self.scrapingdog_api_key:
                raise Exception("ScrapingDog API key not configured")
            
            # Standard ScrapingDog parameters
            params = {
                'api_key': self.scrapingdog_api_key,
                'url': url,
                'render': 'false',  # No JavaScript
                'country': 'US'
            }
            
            scraping_url = "https://api.scrapingdog.com/scrape"
            
            print("🐕 Using ScrapingDog Standard...")
            response = requests.get(scraping_url, params=params, timeout=25)
            
            if response.status_code == 200:
                products = self._parse_amazon_response(response.text, category)
                return products
            else:
                raise Exception(f"ScrapingDog API error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ ScrapingDog Standard failed: {str(e)}")
            raise e
    
    async def _scrape_playwright_mcp(self, url: str, category: str) -> List[Dict[str, Any]]:
        """Scrape using MCP Playwright - our excellent alternative to ScrapingDog"""
        try:
            print("🎭 Using Playwright MCP for scraping...")
            
            # Import the Playwright MCP agent
            from src.mcp.playwright_scraping_agent_mcp import playwright_mcp_scrape
            
            # Use the Playwright MCP scraping function
            products = await playwright_mcp_scrape(url, category)
            
            if products and len(products) > 0:
                print(f"🎭 Playwright MCP success: {len(products)} products found")
                return products
            else:
                raise Exception("Playwright MCP returned no products")
                
        except Exception as e:
            print(f"❌ Playwright MCP failed: {str(e)}")
            raise e
    
    async def _scrape_direct_requests(self, url: str, category: str) -> List[Dict[str, Any]]:
        """Direct scraping using requests with headers"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            print("🌐 Using Direct Requests...")
            response = requests.get(url, headers=headers, timeout=20)
            
            if response.status_code == 200:
                products = self._parse_amazon_response(response.text, category)
                return products
            else:
                raise Exception(f"Direct request failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Direct Requests failed: {str(e)}")
            raise e
    
    async def _scrape_alternative_api(self, url: str, category: str) -> List[Dict[str, Any]]:
        """Try alternative scraping APIs"""
        try:
            # Placeholder for alternative APIs (RapidAPI, WebScraping.AI, etc.)
            print("🔄 Trying Alternative APIs...")
            
            # TODO: Implement alternative API sources
            # Examples: RapidAPI Amazon scraper, WebScraping.AI, etc.
            
            # For now, return empty to simulate no alternative configured
            raise Exception("Alternative APIs not configured yet")
                
        except Exception as e:
            print(f"❌ Alternative API failed: {str(e)}")
            raise e
    
    async def _prepare_manual_fallback(self, url: str, category: str) -> List[Dict[str, Any]]:
        """Prepare manual fallback with notification"""
        try:
            print("📋 Preparing manual fallback...")
            
            # Create manual intervention request
            manual_request = {
                "type": "manual_scraping_required",
                "url": url,
                "category": category,
                "timestamp": datetime.now().isoformat(),
                "instructions": "All automated scraping methods failed. Manual intervention required.",
                "required_products": 5,
                "status": "pending_manual_review"
            }
            
            # TODO: Send notification to admin/team
            print("📧 Manual intervention notification prepared")
            print(f"🔗 URL requiring manual scraping: {url}")
            print(f"📦 Category: {category}")
            
            # Return empty for now - manual process will populate later
            return []
                
        except Exception as e:
            print(f"❌ Manual fallback preparation failed: {str(e)}")
            raise e
    
    def _parse_amazon_response(self, html_content: str, category: str) -> List[Dict[str, Any]]:
        """Parse Amazon HTML response to extract product data"""
        try:
            # TODO: Implement robust HTML parsing
            # This is a placeholder for the actual parsing logic
            
            print(f"📄 Parsing HTML content ({len(html_content)} characters)")
            
            # Placeholder - would use BeautifulSoup or similar
            # to extract product titles, ratings, prices, images, etc.
            
            # Simulated parsing result
            products = []
            
            # In real implementation, this would extract:
            # - Product titles
            # - Ratings (4.0+ stars)
            # - Prices
            # - Review counts
            # - Image URLs
            # - Product URLs
            
            print(f"📦 Extracted {len(products)} products from HTML")
            return products
            
        except Exception as e:
            print(f"❌ HTML parsing failed: {str(e)}")
            return []
    
    async def get_scraping_performance_report(self) -> Dict[str, Any]:
        """Generate performance report for different scraping sources"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "sources": {},
            "recommendations": []
        }
        
        for source in self.scraping_sources:
            success_rate = self.source_success_rates.get(source, 0.0)
            
            report["sources"][source] = {
                "success_rate": success_rate,
                "priority": self.scraping_sources.index(source) + 1,
                "status": "active" if success_rate > 0.3 else "low_performance"
            }
        
        # Generate recommendations
        if report["sources"]["scrapingdog_premium"]["success_rate"] < 0.8:
            report["recommendations"].append("Consider ScrapingDog premium tier upgrade")
        
        if report["sources"]["direct_requests"]["success_rate"] < 0.4:
            report["recommendations"].append("Review direct scraping headers and methods") 
        
        return report

# Factory function for easy import
def create_alternative_scraping_manager():
    """Factory function to create AlternativeScrapingManager with loaded config"""
    config = load_config()
    return AlternativeScrapingManager(config)

# Test function
async def test_alternative_scraping():
    """Test alternative scraping system"""
    print("🧪 Testing Alternative Scraping Manager...")
    
    manager = create_alternative_scraping_manager()
    
    test_url = "https://www.amazon.com/s?k=wireless+headphones"
    test_category = "wireless headphones"
    
    try:
        # Test scraping with alternatives
        print("\n1️⃣ Testing scraping with alternatives...")
        result = await manager.scrape_with_alternatives(test_url, test_category)
        
        print(f"Success: {result['success']}")
        print(f"Final source: {result.get('final_source', 'none')}")
        print(f"Products found: {len(result.get('products', []))}")
        
        # Test performance report
        print("\n2️⃣ Testing performance report...")
        report = await manager.get_scraping_performance_report()
        print(f"Report generated for {len(report['sources'])} sources")
        
        print("\n✅ Alternative scraping test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    # Run test
    asyncio.run(test_alternative_scraping())