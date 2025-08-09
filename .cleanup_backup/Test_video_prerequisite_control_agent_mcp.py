#!/usr/bin/env python3
"""
Test Video Prerequisite Control Agent - Test Version
Uses hardcoded test data for rapid testing without API calls
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add the project root to Python path
sys.path.append('/home/claude-workflow')

async def test_initialize_video_production_status(record_id: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
    """Test version: Initialize VideoProductionRDY to 'Pending'"""
    try:
        print(f"🧪 TEST: Initializing video production status for record {record_id}")
        
        # Use test server
        from mcp_servers.Test_video_prerequisite_control_server import create_test_video_prerequisite_control_server
        server = create_test_video_prerequisite_control_server()
        
        result = await server.initialize_video_production_status(record_id)
        
        if result.get('success'):
            print(f"✅ TEST: VideoProductionRDY initialized to 'Pending' for record {record_id}")
        else:
            print(f"❌ TEST: Failed to initialize VideoProductionRDY")
        
        return result
        
    except Exception as e:
        print(f"❌ TEST ERROR: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "record_id": record_id,
            "action": "initialize_failed"
        }

async def test_validate_and_update_prerequisites(record_id: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
    """Test version: Validate prerequisites using test scenarios"""
    try:
        print(f"🧪 TEST: Validating prerequisites for record {record_id}")
        
        # Use test server
        from mcp_servers.Test_video_prerequisite_control_server import create_test_video_prerequisite_control_server
        server = create_test_video_prerequisite_control_server()
        
        result = await server.update_video_production_status(record_id)
        
        if result.get('success'):
            ready_for_video = result.get('ready_for_video', False)
            completion_pct = result.get('prerequisite_summary', {}).get('completion_percentage', 0)
            scenario = result.get('test_scenario', 'unknown')
            
            if ready_for_video:
                print(f"🧪🎬 TEST: APPROVED - Record {record_id} ready for video! (scenario: {scenario})")
                print(f"📊 TEST: Completion: {completion_pct}% - All prerequisites met")
            else:
                missing_count = result.get('prerequisite_summary', {}).get('missing_count', 0)
                print(f"🧪⏳ TEST: PENDING - Record {record_id} needs {missing_count} more prerequisites (scenario: {scenario})")
                print(f"📊 TEST: Completion: {completion_pct}% - Continue workflow")
        else:
            print(f"❌ TEST: Failed to validate prerequisites")
        
        return result
        
    except Exception as e:
        print(f"❌ TEST ERROR: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "record_id": record_id,
            "action": "validation_failed"
        }

async def test_check_video_production_eligibility(record_id: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
    """Test version: Check eligibility using test scenarios"""
    try:
        print(f"🧪 TEST: Checking video production eligibility for record {record_id}")
        
        # Use test server
        from mcp_servers.Test_video_prerequisite_control_server import create_test_video_prerequisite_control_server
        server = create_test_video_prerequisite_control_server()
        
        result = await server.check_video_production_eligibility(record_id)
        
        if result.get('success'):
            eligible = result.get('eligible', False)
            status = result.get('status', 'Unknown')
            scenario = result.get('test_scenario', 'unknown')
            
            if eligible:
                print(f"🧪🎬 TEST: CLEARED - Record {record_id} APPROVED for video (scenario: {scenario})")
                print(f"✅ TEST: Status: {status} - Proceed with video generation")
            else:
                print(f"🧪🚫 TEST: BLOCKED - Record {record_id} NOT ready for video (scenario: {scenario})")
                print(f"⚠️ TEST: Status: {status} - Complete prerequisites first")
        else:
            print(f"❌ TEST: Failed to check eligibility")
        
        return result
        
    except Exception as e:
        print(f"❌ TEST ERROR: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "record_id": record_id,
            "eligible": False,
            "action_required": "fix_error_and_retry"
        }

async def test_get_prerequisite_status_report(record_id: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
    """Test version: Generate test status report"""
    try:
        print(f"🧪 TEST: Generating prerequisite status report for record {record_id}")
        
        # Use test server
        from mcp_servers.Test_video_prerequisite_control_server import create_test_video_prerequisite_control_server
        server = create_test_video_prerequisite_control_server()
        
        result = await server.get_prerequisite_status_report(record_id)
        
        if result.get('success', True):
            summary = result.get('summary', {})
            completion_pct = summary.get('completion_percentage', 0)
            ready_for_video = summary.get('ready_for_video', False)
            scenario = result.get('test_scenario', 'unknown')
            
            print(f"🧪📈 TEST: Report generated for record {record_id} (scenario: {scenario})")
            print(f"🎯 TEST: Progress: {completion_pct}% complete")
            print(f"🎬 TEST: Video Ready: {'Yes' if ready_for_video else 'No'}")
            print(f"💡 TEST: Recommendation: {result.get('recommendation', 'No recommendation')}")
            
            # Show missing items if any
            missing_items = result.get('missing_items', [])
            if missing_items:
                print(f"⚠️ TEST: Missing Prerequisites ({len(missing_items)}):")
                for item in missing_items[:3]:  # Show first 3 in test
                    print(f"   - {item['field']}: needs '{item['required']}'")
                if len(missing_items) > 3:
                    print(f"   ... and {len(missing_items) - 3} more")
        else:
            print(f"❌ TEST: Failed to generate report")
        
        return result
        
    except Exception as e:
        print(f"❌ TEST ERROR: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "record_id": record_id
        }

async def test_run_prerequisite_security_check(record_id: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
    """Test version: Complete security check with test scenarios"""
    try:
        print(f"🧪🛡️ TEST: Running prerequisite security check for record {record_id}")
        
        # Step 1: Check eligibility
        eligibility = await test_check_video_production_eligibility(record_id, config)
        
        if not eligibility.get('success', False):
            return {
                "approved": False,
                "reason": "eligibility_check_failed",
                "error": eligibility.get('error', 'Unknown error'),
                "action": "fix_error_and_retry"
            }
        
        scenario = eligibility.get('test_scenario', 'unknown')
        
        if not eligibility.get('eligible', False):
            # Get detailed report for debugging
            report = await test_get_prerequisite_status_report(record_id, config)
            
            print(f"🧪🚫 TEST: SECURITY DENIED - Prerequisites incomplete (scenario: {scenario})")
            return {
                "approved": False,
                "reason": "prerequisites_incomplete",
                "status": eligibility.get('status', 'Unknown'),
                "message": eligibility.get('message', 'Prerequisites not complete'),
                "action": eligibility.get('action_required', 'complete_prerequisites_first'),
                "test_scenario": scenario,
                "detailed_report": report
            }
        
        # Step 2: Final validation
        validation = await test_validate_and_update_prerequisites(record_id, config)
        
        if validation.get('ready_for_video', False):
            print(f"🧪🎬 TEST: SECURITY APPROVED - Record {record_id} cleared for video (scenario: {scenario})")
            return {
                "approved": True,
                "reason": "all_prerequisites_met",
                "status": "Ready",
                "message": f"TEST: All prerequisites validated - video approved (scenario: {scenario})",
                "action": "proceed_with_video_generation",
                "test_scenario": scenario,
                "validation_details": validation
            }
        else:
            print(f"🧪🚫 TEST: SECURITY DENIED - Final validation failed (scenario: {scenario})")
            return {
                "approved": False,
                "reason": "final_validation_failed",
                "status": "Pending",
                "message": f"TEST: Prerequisites validation failed (scenario: {scenario})",
                "action": "complete_prerequisites_first",
                "test_scenario": scenario,
                "validation_details": validation
            }
        
    except Exception as e:
        print(f"❌ TEST SECURITY CHECK FAILED: {str(e)}")
        return {
            "approved": False,
            "reason": "security_check_error",
            "error": str(e),
            "action": "fix_error_and_retry"
        }

# Factory functions for test workflow
async def test_run_prerequisite_initialization(record_id: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
    """Test: Initialize prerequisites for new record"""
    return await test_initialize_video_production_status(record_id, config)

async def test_run_prerequisite_validation(record_id: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
    """Test: Validate and update prerequisites"""
    return await test_validate_and_update_prerequisites(record_id, config)

async def test_run_video_security_gate(record_id: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
    """Test: Final security check before video"""
    return await test_run_prerequisite_security_check(record_id, config)

# Test integration helper
class TestVideoPrerequisiteController:
    """Test helper class for easy integration into test workflow"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
    
    async def initialize_for_new_title(self, record_id: str) -> bool:
        """Test: Initialize prerequisites when title is selected"""
        result = await test_run_prerequisite_initialization(record_id, self.config)
        return result.get('success', False)
    
    async def update_after_content_step(self, record_id: str) -> Dict[str, Any]:
        """Test: Update prerequisites after content generation"""
        return await test_run_prerequisite_validation(record_id, self.config)
    
    async def check_video_approval(self, record_id: str) -> bool:
        """Test: Check if video generation is approved"""
        result = await test_run_video_security_gate(record_id, self.config)
        return result.get('approved', False)
    
    async def get_progress_report(self, record_id: str) -> Dict[str, Any]:
        """Test: Get detailed progress report"""
        return await test_get_prerequisite_status_report(record_id, self.config)

# Complete test workflow
async def test_complete_prerequisite_workflow():
    """Test all prerequisite scenarios comprehensively"""
    print("🧪 Testing Complete Video Prerequisite Control Workflow...")
    
    # Test different scenarios
    test_cases = [
        ("test_all_ready_1", "Should approve video production"),
        ("test_partial_2", "Should require more prerequisites"),
        ("test_none_ready_3", "Should block video production")
    ]
    
    controller = TestVideoPrerequisiteController()
    
    for record_id, description in test_cases:
        print(f"\n🎭 Testing Scenario: {record_id} - {description}")
        print("=" * 60)
        
        try:
            # Complete workflow test
            print("1️⃣ Initializing...")
            init_success = await controller.initialize_for_new_title(record_id)
            print(f"   Init Success: {init_success}")
            
            print("2️⃣ Updating prerequisites...")
            update_result = await controller.update_after_content_step(record_id)
            completion = update_result.get('prerequisite_summary', {}).get('completion_percentage', 0)
            print(f"   Completion: {completion}%")
            
            print("3️⃣ Checking video approval...")
            approved = await controller.check_video_approval(record_id)
            print(f"   Video Approved: {approved}")
            
            print("4️⃣ Getting progress report...")
            report = await controller.get_progress_report(record_id)
            scenario = report.get('test_scenario', 'unknown')
            ready = report.get('summary', {}).get('ready_for_video', False)
            print(f"   Scenario: {scenario}, Ready: {ready}")
            
            print(f"✅ Scenario {record_id} completed successfully")
            
        except Exception as e:
            print(f"❌ Scenario {record_id} failed: {str(e)}")
    
    print("\n🧪 All prerequisite workflow tests completed!")

# Demo function showing different test scenarios
def show_test_scenarios():
    """Show available test scenarios and their expected results"""
    print("""
🎭 Available Test Scenarios:

1. ALL READY SCENARIO (record_id ending in '1' or containing 'all_ready'):
   Example: "test_all_ready_1", "record_ready_1", "sample_1"
   - All 17 status columns set to "Ready"
   - All 9 URL fields populated with test URLs
   - Result: VideoProductionRDY = "Ready" (100% complete)
   - Security Check: APPROVED for video production

2. PARTIALLY READY SCENARIO (record_id ending in '2' or containing 'partial'):
   Example: "test_partial_2", "record_partial_2", "sample_2"
   - Half of status columns "Ready", half "Pending"
   - Half of URL fields populated, half empty
   - Result: VideoProductionRDY = "Pending" (~50% complete)
   - Security Check: BLOCKED - prerequisites incomplete

3. NONE READY SCENARIO (all other record_ids):
   Example: "test_none_3", "record_sample", "any_other_id"
   - All status columns set to "Pending"
   - All URL fields empty
   - Result: VideoProductionRDY = "Pending" (0% complete)
   - Security Check: BLOCKED - no prerequisites complete

Usage in workflow:
- Use "test_ready_1" to test successful video generation path
- Use "test_partial_2" to test partial completion handling
- Use "test_blocked_3" to test prerequisite blocking
    """)

if __name__ == "__main__":
    # Show available scenarios
    show_test_scenarios()
    
    # Run complete workflow test
    asyncio.run(test_complete_prerequisite_workflow())