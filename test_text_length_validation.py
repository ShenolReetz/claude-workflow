#!/usr/bin/env python3
"""
Test script for Text Length Validation functionality
"""

import asyncio
import sys
sys.path.append('/home/claude-workflow')

from src.mcp.Test_text_length_validation_agent_mcp import run_text_length_validation

async def test_validation():
    """Test the text length validation with a small batch"""
    
    print("="*80)
    print("🧪 Testing Text Length Validation MCP")
    print("="*80)
    
    # Test with a small batch of records
    print("\n📋 Testing batch validation (3 records)...")
    results = await run_text_length_validation(limit=3)
    
    print("\n" + "="*80)
    print("✅ Test Complete")
    print("="*80)
    
    # Summary
    if results.get('total_processed', 0) > 0:
        print(f"\n📊 Test Results:")
        print(f"   - Processed: {results['total_processed']} records")
        print(f"   - Successful: {results['successful']}")
        print(f"   - All Approved: {results['all_approved']}")
        print(f"   - Has Rejections: {results['has_rejections']}")
    
    return results

if __name__ == "__main__":
    asyncio.run(test_validation())