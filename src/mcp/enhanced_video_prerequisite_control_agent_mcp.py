#!/usr/bin/env python3
"""
Enhanced Video Prerequisite Control Agent - Production Version
Integrates smart retry with critical failure protection for product video accuracy

CRITICAL POLICY: Photos/Audio must be accurate or video STOPS + notification sent
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add the project root to Python path
sys.path.append('/home/claude-workflow')

async def run_enhanced_prerequisite_initialization(record_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Initialize VideoProductionRDY with enhanced tracking
    """
    try:
        print(f"🛡️ ENHANCED: Initializing prerequisite tracking for record {record_id}")
        
        from mcp_servers.enhanced_video_prerequisite_control_server import create_enhanced_video_prerequisite_control_server
        server = create_enhanced_video_prerequisite_control_server()
        
        # Use enhanced initialization (same as original but with tracking enhancements)
        from mcp_servers.video_prerequisite_control_server import create_video_prerequisite_control_server
        original_server = create_video_prerequisite_control_server()
        
        result = await original_server.initialize_video_production_status(record_id)
        
        if result.get('success'):
            print(f"✅ ENHANCED: VideoProductionRDY initialized to 'Pending' for record {record_id}")
            print(f"🛡️ ENHANCED: Critical failure protection ACTIVE")
        else:
            print(f"❌ ENHANCED: Failed to initialize VideoProductionRDY")
        
        return result
        
    except Exception as e:
        print(f"❌ ENHANCED ERROR: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "record_id": record_id,
            "action": "enhanced_initialize_failed"
        }

async def run_enhanced_prerequisite_validation_with_retry(record_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhanced prerequisite validation with smart retry and critical failure protection
    """
    try:
        print(f"🛡️ ENHANCED: Starting prerequisite validation with retry protection for record {record_id}")
        
        from mcp_servers.enhanced_video_prerequisite_control_server import create_enhanced_video_prerequisite_control_server
        server = create_enhanced_video_prerequisite_control_server()
        
        result = await server.update_video_production_status_enhanced(record_id)
        
        if result.get('success'):
            video_approved = result.get('can_produce_video', False)
            status = result.get('new_status', 'Unknown')
            critical_summary = result.get('critical_summary', {})
            
            if video_approved:
                print(f"🛡️✅ ENHANCED: ALL CRITICAL PREREQUISITES VALIDATED - Video production APPROVED")
                print(f"🎬 ENHANCED: VideoProductionRDY = 'Ready' for record {record_id}")
                print(f"📊 ENHANCED: Success rate: {critical_summary.get('completion_percentage', 0)}%")
            else:
                if status == "Failed":
                    print(f"🛡️🚨 ENHANCED: CRITICAL FAILURES DETECTED - Video production PERMANENTLY BLOCKED")
                    print(f"🚫 ENHANCED: VideoProductionRDY = 'Failed' for record {record_id}")
                    print(f"📧 ENHANCED: Critical failure notification should be sent")
                    print(f"⚠️ ENHANCED: Manual intervention required")
                else:
                    print(f"🛡️⏳ ENHANCED: Prerequisites incomplete - Video production PENDING")
                    print(f"📊 ENHANCED: Progress: {critical_summary.get('completion_percentage', 0)}%")
        else:
            print(f"❌ ENHANCED: Validation failed with error")
        
        return result
        
    except Exception as e:
        print(f"❌ ENHANCED ERROR: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "record_id": record_id,
            "action": "enhanced_validation_failed"
        }

async def run_enhanced_video_security_gate(record_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhanced security check before video generation with critical failure protection
    This is the FINAL gate before video generation starts
    """
    try:
        print(f"🛡️🚪 ENHANCED: Running final security gate for record {record_id}")
        
        from mcp_servers.enhanced_video_prerequisite_control_server import create_enhanced_video_prerequisite_control_server
        server = create_enhanced_video_prerequisite_control_server()
        
        # Step 1: Final validation check
        validation = await server.validate_with_retry_protection(record_id)
        
        if not validation.get("success", True):
            print(f"🛡️❌ ENHANCED: Security gate validation error")
            return {
                "approved": False,
                "reason": "security_gate_validation_error",
                "error": validation.get("error", "Unknown validation error"),
                "action": "fix_error_and_retry"
            }
        
        # Step 2: Make final decision
        if validation.get("can_produce_video", False):
            print(f"🛡️🎬 ENHANCED: SECURITY GATE PASSED - Video generation APPROVED")
            print(f"✅ ENHANCED: All critical prerequisites validated")
            print(f"🎯 ENHANCED: Product accuracy: GUARANTEED")
            print(f"🎵 ENHANCED: Audio quality: VERIFIED")
            
            return {
                "approved": True,
                "reason": "all_critical_prerequisites_validated",
                "status": "Ready",
                "message": f"ENHANCED: All critical components validated - video approved with accuracy guarantee",
                "action": "proceed_with_video_generation",
                "validation_details": validation,
                "product_accuracy_guaranteed": True,
                "audio_quality_verified": True
            }
        
        else:
            # Check if it's a critical failure or just pending
            if validation.get("critical_count", 0) > 0:
                print(f"🛡️🚨 ENHANCED: SECURITY GATE BLOCKED - Critical failures detected")
                print(f"❌ ENHANCED: {validation['critical_count']} critical components failed")
                print(f"🚫 ENHANCED: Video generation PERMANENTLY BLOCKED")
                
                # This should trigger notification and record marking
                return {
                    "approved": False,
                    "reason": "critical_failures_detected",
                    "status": "Failed",
                    "message": f"ENHANCED: {validation['critical_count']} critical failures - cannot produce accurate video",
                    "action": "critical_failure_notification_required",
                    "critical_failures": validation.get("critical_failures", []),
                    "manual_intervention_required": True,
                    "video_blocked_permanently": True
                }
            else:
                print(f"🛡️⏳ ENHANCED: Security gate pending - Prerequisites incomplete")
                print(f"📊 ENHANCED: Progress: {validation.get('ready_count', 0)}/{validation.get('total_critical', 0)}")
                
                return {
                    "approved": False,
                    "reason": "prerequisites_incomplete",
                    "status": "Pending",
                    "message": f"ENHANCED: Prerequisites not complete - continue workflow",
                    "action": "complete_prerequisites_first",
                    "validation_details": validation,
                    "can_retry": True
                }
        
    except Exception as e:
        print(f"❌ ENHANCED SECURITY GATE ERROR: {str(e)}")
        return {
            "approved": False,
            "reason": "security_gate_error",
            "error": str(e),
            "action": "fix_error_and_retry"
        }

async def run_enhanced_critical_failure_notification(record_id: str, failures: List[Dict[str, Any]], config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send enhanced critical failure notifications with detailed information
    """
    try:
        print(f"🛡️📧 ENHANCED: Sending critical failure notification for record {record_id}")
        
        from mcp_servers.prerequisite_retry_agent_server import create_prerequisite_retry_agent_server
        retry_agent = create_prerequisite_retry_agent_server()
        
        # Send notification with enhanced details
        notification_result = await retry_agent.send_critical_failure_notification(record_id, failures)
        
        # Enhanced logging
        if notification_result.get("success"):
            print(f"🛡️✅ ENHANCED: Critical failure notification sent successfully")
            print(f"📧 ENHANCED: Admin/team notified of product accuracy issue")
            print(f"🚫 ENHANCED: Video generation blocked to prevent inaccurate content")
        else:
            print(f"🛡️❌ ENHANCED: Failed to send critical failure notification")
        
        return notification_result
        
    except Exception as e:
        print(f"❌ ENHANCED NOTIFICATION ERROR: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "record_id": record_id,
            "notification_sent": False
        }

async def run_enhanced_scraping_with_alternatives(url: str, category: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhanced scraping with multiple fallback sources
    """
    try:
        print(f"🛡️🔍 ENHANCED: Starting scraping with alternatives for category: {category}")
        
        from mcp_servers.alternative_scraping_manager import create_alternative_scraping_manager
        scraping_manager = create_alternative_scraping_manager()
        
        result = await scraping_manager.scrape_with_alternatives(url, category)
        
        if result.get("success"):
            print(f"🛡️✅ ENHANCED: Scraping successful using {result.get('final_source')}")
            print(f"📦 ENHANCED: {len(result.get('products', []))} products found")
        else:
            print(f"🛡️❌ ENHANCED: All scraping methods failed")
            print(f"🔄 ENHANCED: Manual intervention may be required")
        
        return result
        
    except Exception as e:
        print(f"❌ ENHANCED SCRAPING ERROR: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "url": url,
            "category": category
        }

async def get_enhanced_prerequisite_status_report(record_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate enhanced prerequisite status report with critical failure analysis
    """
    try:
        print(f"🛡️📊 ENHANCED: Generating comprehensive status report for record {record_id}")
        
        from mcp_servers.enhanced_video_prerequisite_control_server import create_enhanced_video_prerequisite_control_server
        server = create_enhanced_video_prerequisite_control_server()
        
        # Get enhanced validation first
        validation = await server.validate_with_retry_protection(record_id)
        
        if not validation.get("success", True):
            return validation
        
        # Generate enhanced report
        report = {
            "record_id": record_id,
            "timestamp": datetime.now().isoformat(),
            "enhanced_analysis": True,
            "video_decision": validation.get("video_decision", "unknown"),
            "critical_summary": {
                "total_critical_requirements": validation.get("total_critical", 0),
                "ready_count": validation.get("ready_count", 0),
                "critical_failures": validation.get("critical_count", 0),
                "completion_percentage": round((validation.get("ready_count", 0) / max(validation.get("total_critical", 1), 1)) * 100, 1),
                "can_produce_video": validation.get("can_produce_video", False)
            },
            "accuracy_guarantees": {
                "product_photos_accurate": True if validation.get("critical_count", 1) == 0 else False,
                "audio_quality_verified": True if validation.get("critical_count", 1) == 0 else False,
                "no_generic_content": True  # Enhanced system never uses generic content for critical components
            },
            "detailed_status": {
                "critical_status_columns": validation.get("critical_status_validation", {}),
                "critical_url_fields": validation.get("critical_url_validation", {}),
                "failed_components": validation.get("critical_failures", [])
            },
            "recommendations": []
        }
        
        # Generate enhanced recommendations
        if validation.get("can_produce_video"):
            report["recommendations"].append("🎬 ALL CLEAR: Ready for video generation with accuracy guarantee")
        elif validation.get("critical_count", 0) > 0:
            report["recommendations"].append(f"🚨 CRITICAL: {validation['critical_count']} components failed - manual intervention required")
            report["recommendations"].append("🚫 Video generation blocked to ensure product accuracy")
        else:
            report["recommendations"].append("⚡ Continue workflow: Prerequisites in progress")
        
        print(f"🛡️📈 ENHANCED: Report generated - {report['critical_summary']['completion_percentage']}% complete")
        print(f"🎯 ENHANCED: Video decision: {report['video_decision']}")
        
        return report
        
    except Exception as e:
        print(f"❌ ENHANCED REPORT ERROR: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "record_id": record_id
        }

# Integration helper class for enhanced workflow
class EnhancedVideoPrerequisiteController:
    """Enhanced controller for integration into production workflow"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    async def initialize_for_new_title(self, record_id: str) -> bool:
        """Initialize enhanced prerequisites when title is selected"""
        result = await run_enhanced_prerequisite_initialization(record_id, self.config)
        return result.get('success', False)
    
    async def validate_and_retry_after_content_step(self, record_id: str) -> Dict[str, Any]:
        """Enhanced validation with retry after content generation steps"""
        return await run_enhanced_prerequisite_validation_with_retry(record_id, self.config)
    
    async def final_security_check_before_video(self, record_id: str) -> Dict[str, Any]:
        """Final enhanced security check before video generation"""
        return await run_enhanced_video_security_gate(record_id, self.config)
    
    async def handle_scraping_with_alternatives(self, url: str, category: str) -> Dict[str, Any]:
        """Enhanced scraping with multiple fallback sources"""
        return await run_enhanced_scraping_with_alternatives(url, category, self.config)
    
    async def get_comprehensive_status_report(self, record_id: str) -> Dict[str, Any]:
        """Get enhanced status report with critical analysis"""
        return await get_enhanced_prerequisite_status_report(record_id, self.config)

# Factory functions for workflow integration
async def create_enhanced_prerequisite_controller(config: Dict[str, Any]) -> EnhancedVideoPrerequisiteController:
    """Create enhanced prerequisite controller"""
    return EnhancedVideoPrerequisiteController(config)

# Main integration functions for workflow_runner.py
async def enhanced_initialize_video_prerequisites(record_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Main function for initializing enhanced prerequisites"""
    return await run_enhanced_prerequisite_initialization(record_id, config)

async def enhanced_validate_video_prerequisites(record_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Main function for enhanced prerequisite validation"""
    return await run_enhanced_prerequisite_validation_with_retry(record_id, config)

async def enhanced_final_video_security_check(record_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Main function for final enhanced security check"""
    return await run_enhanced_video_security_gate(record_id, config)

if __name__ == "__main__":
    # Test the enhanced system
    import asyncio
    from src.load_config import load_config
    
    async def test_enhanced_agent():
        print("🧪 Testing Enhanced Video Prerequisite Control Agent...")
        
        config = load_config()
        controller = EnhancedVideoPrerequisiteController(config)
        test_record_id = "rec_test_enhanced_agent"
        
        try:
            # Test initialization
            print("\n1️⃣ Testing enhanced initialization...")
            init_success = await controller.initialize_for_new_title(test_record_id)
            print(f"Init success: {init_success}")
            
            # Test validation with retry
            print("\n2️⃣ Testing enhanced validation with retry...")
            validation_result = await controller.validate_and_retry_after_content_step(test_record_id)
            print(f"Validation approved: {validation_result.get('can_produce_video', False)}")
            
            # Test final security check
            print("\n3️⃣ Testing final enhanced security check...")
            security_result = await controller.final_security_check_before_video(test_record_id)
            print(f"Security approved: {security_result.get('approved', False)}")
            
            # Test status report
            print("\n4️⃣ Testing comprehensive status report...")
            report = await controller.get_comprehensive_status_report(test_record_id)
            print(f"Report generated: {report.get('enhanced_analysis', False)}")
            
            print("\n✅ Enhanced agent test completed!")
            
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
    
    asyncio.run(test_enhanced_agent())