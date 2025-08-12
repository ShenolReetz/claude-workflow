#!/usr/bin/env python3
"""
Example: How to Use Subagents with MCP Tools
This demonstrates how a subagent can discover and use MCP tools dynamically
"""

import asyncio
import json
from typing import Dict, List, Any

class ProductAnalyzerAgent:
    """
    Subagent that can discover and use MCP tools for product analysis
    """
    
    def __init__(self):
        self.name = "product-analyzer"
        self.available_tools = []
        
    async def discover_tools(self) -> List[str]:
        """
        Discover available MCP tools at runtime
        In a real implementation, this would query the MCP server registry
        """
        # When properly integrated with Claude Code, these tools are discovered automatically
        # They appear as mcp__servername__toolname
        discovered_tools = [
            "mcp__product-category-extractor__extract_category",
            "mcp__product-category-extractor__batch_extract_categories"
        ]
        
        self.available_tools = discovered_tools
        print(f"🔍 Discovered {len(discovered_tools)} MCP tools:")
        for tool in discovered_tools:
            print(f"  - {tool}")
        
        return discovered_tools
    
    async def analyze_single_product(self, title: str) -> Dict:
        """
        Analyze a single product using MCP tools
        """
        print(f"\n📦 Analyzing product: {title}")
        
        # In Claude Code, this would be a direct tool call like:
        # result = await use_tool("mcp__product-category-extractor__extract_category", {"title": title})
        
        # Simulated MCP tool call
        tool_name = "mcp__product-category-extractor__extract_category"
        
        if tool_name in self.available_tools:
            print(f"  Using tool: {tool_name}")
            
            # This simulates what the MCP tool would return
            result = {
                "title": title,
                "category": "Electronics",
                "subcategory": "Cameras",
                "keywords": ["camera", "photography", "Sony", "mirrorless", "lens"],
                "confidence": 0.95
            }
            
            print(f"  ✅ Category: {result['category']} > {result['subcategory']}")
            print(f"  🏷️ Keywords: {', '.join(result['keywords'])}")
            
            return result
        else:
            print(f"  ⚠️ Tool {tool_name} not available")
            return {"error": "Tool not available"}
    
    async def analyze_batch_products(self, titles: List[str]) -> List[Dict]:
        """
        Analyze multiple products using batch MCP tools
        """
        print(f"\n📦 Batch analyzing {len(titles)} products")
        
        tool_name = "mcp__product-category-extractor__batch_extract_categories"
        
        if tool_name in self.available_tools:
            print(f"  Using tool: {tool_name}")
            
            # In real implementation:
            # results = await use_tool(tool_name, {"titles": titles})
            
            # Simulated batch results
            results = []
            categories = ["Electronics", "Home & Kitchen", "Sports & Outdoors"]
            subcategories = ["Audio", "Kitchen Appliances", "Fitness Equipment"]
            
            for i, title in enumerate(titles):
                results.append({
                    "title": title,
                    "category": categories[i % len(categories)],
                    "subcategory": subcategories[i % len(subcategories)],
                    "keywords": ["keyword1", "keyword2", "keyword3"]
                })
            
            print(f"  ✅ Processed {len(results)} products")
            for r in results:
                print(f"    - {r['title'][:30]}... → {r['category']}")
            
            return results
        else:
            print(f"  ⚠️ Tool {tool_name} not available")
            return []
    
    async def generate_product_content(self, product_data: Dict) -> Dict:
        """
        Generate marketing content based on product category
        """
        print(f"\n✍️ Generating content for {product_data.get('category', 'Unknown')} product")
        
        # This demonstrates how agents can chain MCP tools and other operations
        content = {
            "title": f"Premium {product_data.get('subcategory', 'Product')} - {product_data.get('title', '')}",
            "description": f"Discover the amazing features of this {product_data.get('category', '')} product. "
                          f"Perfect for {', '.join(product_data.get('keywords', [])[:3])} enthusiasts.",
            "seo_keywords": product_data.get('keywords', []),
            "category_specific_features": self._get_category_features(product_data.get('category', ''))
        }
        
        print(f"  ✅ Generated content with {len(content['seo_keywords'])} SEO keywords")
        
        return content
    
    def _get_category_features(self, category: str) -> List[str]:
        """
        Get category-specific features for content generation
        """
        features_map = {
            "Electronics": ["High Performance", "Energy Efficient", "Smart Connectivity"],
            "Home & Kitchen": ["Durable Design", "Easy to Clean", "Space Saving"],
            "Sports & Outdoors": ["Weather Resistant", "Lightweight", "Professional Grade"]
        }
        
        return features_map.get(category, ["Quality Construction", "Reliable", "Great Value"])

async def demonstrate_subagent_usage():
    """
    Demonstrate how subagents work with MCP tools
    """
    print("=" * 60)
    print("SUBAGENT + MCP TOOLS DEMONSTRATION")
    print("=" * 60)
    
    # Create the subagent
    agent = ProductAnalyzerAgent()
    
    # Step 1: Discover available tools
    await agent.discover_tools()
    
    # Step 2: Analyze a single product
    single_result = await agent.analyze_single_product(
        "Sony Alpha A7 III Mirrorless Camera with 28-70mm Lens"
    )
    
    # Step 3: Batch analyze products
    batch_titles = [
        "Apple AirPods Pro Wireless Earbuds",
        "Instant Pot Duo 7-in-1 Electric Pressure Cooker",
        "Garmin Forerunner 245 GPS Running Smartwatch"
    ]
    batch_results = await agent.analyze_batch_products(batch_titles)
    
    # Step 4: Generate content based on analysis
    if batch_results:
        content = await agent.generate_product_content(batch_results[0])
        print(f"\n📄 Generated Content Preview:")
        print(f"  Title: {content['title']}")
        print(f"  Description: {content['description'][:100]}...")
    
    # Summary
    print("\n" + "=" * 60)
    print("KEY CONCEPTS DEMONSTRATED:")
    print("=" * 60)
    print("""
1. TOOL DISCOVERY: Subagent discovers MCP tools at runtime
   - No hardcoded imports needed
   - Tools appear as mcp__servername__toolname
   
2. DYNAMIC USAGE: Subagent selects appropriate tools based on task
   - Single item processing vs batch processing
   - Automatic tool selection
   
3. COMPOSITION: Subagent chains multiple operations
   - Extract category → Generate content
   - Combine MCP tools with other logic
   
4. SCALABILITY: Easy to add new capabilities
   - Add new MCP server → Instantly available to all subagents
   - No code changes needed in subagents
    """)

async def show_integration_with_claude_code():
    """
    Show how this integrates with Claude Code's Task tool
    """
    print("\n" + "=" * 60)
    print("INTEGRATION WITH CLAUDE CODE")
    print("=" * 60)
    print("""
In Claude Code, you would invoke this subagent using the Task tool:

```python
# From the main Claude Code conversation:
result = await Task(
    subagent_type="product-analyzer",
    description="Analyze product categories",
    prompt="Analyze these products and generate marketing content:
            1. Sony Camera
            2. Apple AirPods
            3. Instant Pot"
)
```

The subagent would then:
1. Automatically discover available MCP tools
2. Use mcp__product-category-extractor__batch_extract_categories
3. Generate content for each product
4. Return structured results

Benefits:
✅ No imports needed
✅ Subagent discovers tools dynamically
✅ Can use any MCP server configured in mcp-servers.json
✅ Parallel processing for efficiency
✅ Error handling built-in
    """)

if __name__ == "__main__":
    # Run the demonstration
    asyncio.run(demonstrate_subagent_usage())
    asyncio.run(show_integration_with_claude_code())