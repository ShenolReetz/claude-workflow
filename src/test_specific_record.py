#!/usr/bin/env python3
"""
Test workflow with a specific record that should work
"""

import asyncio
import json
import sys
sys.path.append('/home/claude-workflow')

from src.workflow_runner import ContentPipelineOrchestrator

async def test_specific_record():
    """Test workflow with a specific record"""
    
    # Try first few records to find one that might work
    test_records = [
        "rec00Yb60qB6jOXSE",  # Car Amps
        "rec02oN1OOci9KYlx",  # Marine Subs
        "rec06cijwjDHrgJ0f",  # Monitors
        "rec0AGYBGUAZGxu62",  # Power Strips
        "rec0CUkALU4Uxk27Y"   # Camera Stabilizers
    ]
    
    orchestrator = ContentPipelineOrchestrator()
    
    for record_id in test_records:
        print(f"\n🧪 Testing record: {record_id}")
        try:
            # Get the record first
            record = await orchestrator.airtable_server.get_record_by_id(record_id)
            if record:
                title = record.get('fields', {}).get('VideoTitle', 'No title')
                print(f"   Title: {title}")
                
                # Simple test: try to extract a basic category
                category = title.lower().replace('🔥', '').replace('insane', '').replace('5', '').strip()
                category_words = category.split()[:3]  # Take first 3 words
                test_category = ' '.join(category_words)
                
                print(f"   Test category: {test_category}")
                
                # If it looks like a reasonable category, try it
                if len(test_category) > 5 and any(word in test_category for word in ['car', 'marine', 'monitor', 'power', 'camera']):
                    print(f"   ✅ This looks promising, testing...")
                    
                    # Update the record to Pending to test
                    await orchestrator.airtable_server.update_record(record_id, {'Status': 'Pending'})
                    
                    # Try to run the workflow
                    result = await orchestrator.process_single_title(record)
                    print(f"   Result: {result}")
                    return result
                    
        except Exception as e:
            print(f"   ❌ Error: {e}")
            continue
    
    print("❌ No suitable records found for testing")
    return None

if __name__ == "__main__":
    result = asyncio.run(test_specific_record())
    if result:
        print("\n✅ Test completed successfully!")
    else:
        print("\n❌ Test failed")