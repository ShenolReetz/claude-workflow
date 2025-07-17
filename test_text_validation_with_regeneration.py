#!/usr/bin/env python3
"""
Test script for Text Length Validation with Regeneration functionality
"""

import asyncio
import sys
sys.path.append('/home/claude-workflow')

from src.mcp.text_length_validation_with_regeneration_agent_mcp import run_text_validation_with_regeneration

async def test_validation_with_regeneration():
    """Test the text validation with regeneration for a single record"""
    
    print("="*80)
    print("🧪 Testing Text Length Validation with Regeneration")
    print("="*80)
    
    # Test with a single record
    print("\n📋 Testing validation with regeneration (1 record)...")
    try:
        results = await run_text_validation_with_regeneration(limit=1)
        
        print("\n" + "="*80)
        print("✅ Test Complete")
        print("="*80)
        
        # Summary
        if results.get('total_processed', 0) > 0:
            print(f"\n📊 Test Results:")
            print(f"   - Processed: {results['total_processed']} records")
            print(f"   - Successful: {results['successful']}")
            print(f"   - Fully Approved: {results['fully_approved']}")
            print(f"   - Partially Approved: {results['partially_approved']}")
            print(f"   - Failed: {results['failed']}")
        
        return results
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    asyncio.run(test_validation_with_regeneration())