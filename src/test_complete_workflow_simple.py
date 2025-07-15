#!/usr/bin/env python3
"""
Simple test of the complete workflow
"""

import asyncio
import sys
sys.path.append('/home/claude-workflow')

from src.workflow_runner import ContentPipelineOrchestrator

async def test_complete_workflow():
    """Test the complete workflow"""
    
    print("🚀 Starting complete workflow test...")
    
    orchestrator = ContentPipelineOrchestrator()
    
    try:
        # Run the complete workflow
        await orchestrator.run_complete_workflow()
        print("✅ Complete workflow test finished successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Complete workflow test failed: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_complete_workflow())
    if result:
        print("\n🎉 Test completed successfully!")
    else:
        print("\n💥 Test failed")