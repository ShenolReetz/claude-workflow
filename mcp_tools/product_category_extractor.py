#!/usr/bin/env python3
"""
Wrapper script to invoke the MCP server's functionality
This allows subagents to use MCP server capabilities through Python execution
"""

import json
import sys
import os
import asyncio
from typing import Dict, List

# Add parent directory to path to import MCP server
sys.path.insert(0, '/home/claude-workflow')

async def extract_category(title: str, model: str = "gpt-4o") -> Dict:
    """Extract category for a single product title using the MCP server logic"""
    import openai
    
    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        # Try to read from config file
        try:
            with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
                config = json.load(f)
                api_key = config.get('openai_api_key')
        except:
            return {"error": "No OpenAI API key found"}
    
    client = openai.OpenAI(api_key=api_key)
    
    prompt = f"""Analyze this product title and determine its category: "{title}"
    
    Return ONLY a valid JSON object with:
    - category: Main product category (e.g., Electronics, Home & Kitchen, Beauty, etc.)
    - subcategory: Specific subcategory
    - keywords: 5 relevant category keywords
    
    Example response:
    {{"category": "Electronics", "subcategory": "Cameras", "keywords": ["camera", "photography", "video", "action", "recording"]}}
    """
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert at categorizing products. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_completion_tokens=150,
            temperature=0.3
        )
        
        result = json.loads(response.choices[0].message.content)
        
        return {
            'title': title,
            'category': result.get('category', 'General'),
            'subcategory': result.get('subcategory', ''),
            'keywords': result.get('keywords', []),
            'model_used': model
        }
        
    except Exception as e:
        return {
            'error': str(e),
            'title': title,
            'category': 'General',
            'subcategory': '',
            'keywords': [],
            'model_used': model
        }

async def batch_extract_categories(titles: List[str], model: str = "gpt-4o") -> Dict:
    """Extract categories for multiple product titles"""
    results = []
    
    for title in titles:
        result = await extract_category(title, model)
        results.append(result)
    
    return {
        'results': results,
        'total_processed': len(results),
        'model_used': model
    }

def main():
    """CLI entry point for the wrapper"""
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Usage: product_category_extractor.py <command> <args>"}))
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "extract_category":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "Title required"}))
            sys.exit(1)
        
        title = sys.argv[2]
        model = sys.argv[3] if len(sys.argv) > 3 else "gpt-4o"
        
        result = asyncio.run(extract_category(title, model))
        print(json.dumps(result, indent=2))
    
    elif command == "batch_extract_categories":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "Titles JSON array required"}))
            sys.exit(1)
        
        try:
            titles = json.loads(sys.argv[2])
            model = sys.argv[3] if len(sys.argv) > 3 else "gpt-4o"
            
            result = asyncio.run(batch_extract_categories(titles, model))
            print(json.dumps(result, indent=2))
        except json.JSONDecodeError:
            print(json.dumps({"error": "Invalid JSON for titles"}))
            sys.exit(1)
    
    else:
        print(json.dumps({"error": f"Unknown command: {command}"}))
        sys.exit(1)

if __name__ == "__main__":
    main()