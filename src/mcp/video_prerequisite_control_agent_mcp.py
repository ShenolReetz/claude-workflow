#!/usr/bin/env python3
"""
Video Prerequisite Control Agent - Production Version
Integrates prerequisite validation into the main workflow

This agent manages the VideoProductionRDY security system to ensure
video generation only happens when all prerequisites are validated.
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add the project root to Python path
sys.path.append('/home/claude-workflow')

async def initialize_video_production_status(record_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Initialize VideoProductionRDY to 'Pending' when title is first selected
    This should be called in Step 1 of the workflow
    """
    try:
        print(f"🛡️ Initializing video production status for record {record_id}")
        
        # Import and use the prerequisite control server
        from mcp_servers.video_prerequisite_control_server import create_video_prerequisite_control_server
        server = create_video_prerequisite_control_server()
        
        result = await server.initialize_video_production_status(record_id)
        
        if result.get('success'):
            print(f"✅ VideoProductionRDY initialized to 'Pending' for record {record_id}")
        else:
            print(f"❌ Failed to initialize VideoProductionRDY: {result.get('error', 'Unknown error')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error in initialize_video_production_status: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "record_id": record_id,
            "action": "initialize_failed"
        }

async def validate_and_update_prerequisites(record_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate all prerequisites and update VideoProductionRDY status
    This should be called after each content generation step
    """
    try:
        print(f"🔍 Validating prerequisites for record {record_id}")
        
        # Import and use the prerequisite control server
        from mcp_servers.video_prerequisite_control_server import create_video_prerequisite_control_server
        server = create_video_prerequisite_control_server()
        
        # Run comprehensive validation and update status
        result = await server.update_video_production_status(record_id)
        
        if result.get('success'):
            ready_for_video = result.get('ready_for_video', False)
            completion_pct = result.get('prerequisite_summary', {}).get('completion_percentage', 0)
            
            if ready_for_video:
                print(f"🎬 APPROVED: Record {record_id} is ready for video production!")
                print(f"📊 Completion: {completion_pct}% - All prerequisites met")
            else:
                missing_count = result.get('prerequisite_summary', {}).get('missing_count', 0)
                print(f"⏳ PENDING: Record {record_id} needs {missing_count} more prerequisites")
                print(f"📊 Completion: {completion_pct}% - Continue workflow")
        else:
            print(f"❌ Failed to validate prerequisites: {result.get('error', 'Unknown error')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error in validate_and_update_prerequisites: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "record_id": record_id,
            "action": "validation_failed"
        }

async def check_video_production_eligibility(record_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check if record is eligible for video production
    This should be called BEFORE starting video generation
    """
    try:
        print(f"🎯 Checking video production eligibility for record {record_id}")
        
        # Import and use the prerequisite control server
        from mcp_servers.video_prerequisite_control_server import create_video_prerequisite_control_server
        server = create_video_prerequisite_control_server()
        
        result = await server.check_video_production_eligibility(record_id)
        
        if result.get('success'):
            eligible = result.get('eligible', False)
            status = result.get('status', 'Unknown')
            
            if eligible:
                print(f"🎬 CLEARED: Record {record_id} is APPROVED for video production")
                print(f"✅ Status: {status} - Proceed with video generation")
            else:
                print(f"🚫 BLOCKED: Record {record_id} is NOT ready for video production")
                print(f"⚠️ Status: {status} - Complete prerequisites first")
                print(f"📋 Action: {result.get('action_required', 'Unknown')}")
        else:
            print(f"❌ Failed to check eligibility: {result.get('error', 'Unknown error')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error in check_video_production_eligibility: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "record_id": record_id,
            "eligible": False,
            "action_required": "fix_error_and_retry"
        }

async def get_prerequisite_status_report(record_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate comprehensive prerequisite status report
    Useful for debugging and monitoring workflow progress
    """
    try:
        print(f"📊 Generating prerequisite status report for record {record_id}")
        
        # Import and use the prerequisite control server
        from mcp_servers.video_prerequisite_control_server import create_video_prerequisite_control_server
        server = create_video_prerequisite_control_server()
        
        result = await server.get_prerequisite_status_report(record_id)
        
        if result.get('success', True):  # Assume success if not explicitly false
            summary = result.get('summary', {})
            completion_pct = summary.get('completion_percentage', 0)
            ready_for_video = summary.get('ready_for_video', False)
            
            print(f"📈 Report generated for record {record_id}")
            print(f"🎯 Progress: {completion_pct}% complete")
            print(f"🎬 Video Ready: {'Yes' if ready_for_video else 'No'}")
            print(f"💡 Recommendation: {result.get('recommendation', 'No recommendation')}")
            
            # Show missing items if any
            missing_items = result.get('missing_items', [])
            if missing_items:
                print(f"⚠️ Missing Prerequisites ({len(missing_items)}):")
                for item in missing_items[:5]:  # Show first 5
                    print(f"   - {item['field']}: needs '{item['required']}' (current: '{item['current']}')")
                if len(missing_items) > 5:
                    print(f"   ... and {len(missing_items) - 5} more")
        else:
            print(f"❌ Failed to generate report: {result.get('error', 'Unknown error')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error in get_prerequisite_status_report: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "record_id": record_id
        }

async def run_prerequisite_security_check(record_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Complete security check before video generation
    This is the final gate before video production
    
    Returns: Dict with 'approved' boolean and detailed status
    """
    try:
        print(f"🛡️ SECURITY CHECK: Running prerequisite validation for record {record_id}")
        
        # Step 1: Check eligibility
        eligibility = await check_video_production_eligibility(record_id, config)
        
        if not eligibility.get('success', False):
            return {
                "approved": False,
                "reason": "eligibility_check_failed",
                "error": eligibility.get('error', 'Unknown error'),
                "action": "fix_error_and_retry"
            }
        
        if not eligibility.get('eligible', False):
            # Step 2: Get detailed report for debugging
            report = await get_prerequisite_status_report(record_id, config)
            
            return {
                "approved": False,
                "reason": "prerequisites_incomplete",
                "status": eligibility.get('status', 'Unknown'),
                "message": eligibility.get('message', 'Prerequisites not complete'),
                "action": eligibility.get('action_required', 'complete_prerequisites_first'),
                "detailed_report": report
            }
        
        # Step 3: Final validation before approval
        validation = await validate_and_update_prerequisites(record_id, config)
        
        if validation.get('ready_for_video', False):
            print(f"🎬 SECURITY APPROVED: Record {record_id} cleared for video production")
            return {
                "approved": True,
                "reason": "all_prerequisites_met",
                "status": "Ready",
                "message": "All prerequisites validated - video production approved",
                "action": "proceed_with_video_generation",
                "validation_details": validation
            }
        else:
            print(f"🚫 SECURITY DENIED: Record {record_id} not ready for video production")
            return {
                "approved": False,
                "reason": "final_validation_failed",
                "status": "Pending",
                "message": "Prerequisites validation failed at final check",
                "action": "complete_prerequisites_first",
                "validation_details": validation
            }
        
    except Exception as e:
        print(f"❌ SECURITY CHECK FAILED: {str(e)}")
        return {
            "approved": False,
            "reason": "security_check_error",
            "error": str(e),
            "action": "fix_error_and_retry"
        }

# Factory functions for easy import in workflow
async def run_prerequisite_initialization(record_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Initialize prerequisites for new record - use in Step 1"""
    return await initialize_video_production_status(record_id, config)

async def run_prerequisite_validation(record_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and update prerequisites - use after each content step"""
    return await validate_and_update_prerequisites(record_id, config)

async def run_video_security_gate(record_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Final security check before video - use before video generation"""
    return await run_prerequisite_security_check(record_id, config)

# Integration helper for workflow_runner.py
class VideoPrerequisiteController:
    """Helper class for easy integration into workflow"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    async def initialize_for_new_title(self, record_id: str) -> bool:
        """Initialize prerequisites when title is selected"""
        result = await run_prerequisite_initialization(record_id, self.config)
        return result.get('success', False)
    
    async def update_after_content_step(self, record_id: str) -> Dict[str, Any]:
        """Update prerequisites after any content generation step"""
        return await run_prerequisite_validation(record_id, self.config)
    
    async def check_video_approval(self, record_id: str) -> bool:
        """Check if video generation is approved"""
        result = await run_video_security_gate(record_id, self.config)
        return result.get('approved', False)
    
    async def get_progress_report(self, record_id: str) -> Dict[str, Any]:
        """Get detailed progress report"""
        return await get_prerequisite_status_report(record_id, self.config)

# Test function
async def test_prerequisite_workflow():
    """Test the complete prerequisite workflow"""
    print("🧪 Testing Video Prerequisite Control Workflow...")
    
    # Mock config
    test_config = {
        'airtable_api_key': 'test_key',
        'airtable_base_id': 'test_base',
        'airtable_table_name': 'Video Titles'
    }
    
    test_record_id = "rec_test_workflow"
    
    try:
        # Test complete workflow
        print("\n1️⃣ Initializing prerequisites...")
        init_result = await run_prerequisite_initialization(test_record_id, test_config)
        print(f"Result: {init_result.get('message', 'No message')}")
        
        print("\n2️⃣ Validating prerequisites...")
        validation_result = await run_prerequisite_validation(test_record_id, test_config)
        print(f"Ready for video: {validation_result.get('ready_for_video', False)}")
        
        print("\n3️⃣ Running security check...")
        security_result = await run_video_security_gate(test_record_id, test_config)
        print(f"Approved: {security_result.get('approved', False)}")
        print(f"Reason: {security_result.get('reason', 'Unknown')}")
        
        print("\n4️⃣ Generating status report...")
        report_result = await get_prerequisite_status_report(test_record_id, test_config)
        if 'summary' in report_result:
            summary = report_result['summary']
            print(f"Progress: {summary.get('completion_percentage', 0)}%")
            print(f"Ready: {summary.get('ready_for_video', False)}")
        
        print("\n✅ Prerequisite workflow test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    # Run test
    asyncio.run(test_prerequisite_workflow())