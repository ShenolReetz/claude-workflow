#!/usr/bin/env python3
"""
Test Production Flow with Dummy Data
=====================================
Testing version that uses hardcoded data to avoid API costs.
Perfect for testing Remotion and workflow without using tokens.
"""

import asyncio
import sys
import os

# Add path for imports
sys.path.append('/home/claude-workflow')

async def main():
    print("=" * 60)
    print("🧪 TEST PRODUCTION FLOW - NO API CALLS")
    print("=" * 60)
    print("\n📌 This test version uses:")
    print("  • Hardcoded product data (no Amazon scraping)")
    print("  • Mock content (no OpenAI calls)")
    print("  • Dummy audio files (no ElevenLabs)")
    print("  • Test images (no DALL-E)")
    print("  • Real Remotion rendering (to test video creation)")
    print("\n💰 Cost: $0.00 (no API tokens used)\n")
    
    # Import and run the test workflow
    from src.test_workflow_runner import main as test_main
    await test_main()

if __name__ == "__main__":
    asyncio.run(main())