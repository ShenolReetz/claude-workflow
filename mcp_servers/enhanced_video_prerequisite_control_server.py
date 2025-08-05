#!/usr/bin/env python3
"""
Enhanced Video Prerequisite Control Server - Production Version
Handles prerequisite validation with critical failure protection and smart retry

CRITICAL RULE: Photos and Audio must be accurate or video STOPS
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Add the project root to Python path
sys.path.append('/home/claude-workflow')

# Import configuration
from src.load_config import load_config

class EnhancedVideoPrerequisiteControlServer:
    def __init__(self, config: Dict[str, Any]):
        """Initialize Enhanced Video Prerequisite Control Server"""
        self.config = config
        self.airtable_api_key = config['airtable_api_key']
        self.airtable_base_id = config['airtable_base_id']
        self.airtable_table_name = config['airtable_table_name']
        
        # CRITICAL components - Must succeed or video STOPS
        self.critical_status_columns = [
            "VideoTitleStatus", "VideoDescriptionStatus",
            "ProductNo1TitleStatus", "ProductNo1DescriptionStatus", "ProductNo1PhotoStatus",
            "ProductNo2TitleStatus", "ProductNo2DescriptionStatus", "ProductNo2PhotoStatus",
            "ProductNo3TitleStatus", "ProductNo3DescriptionStatus", "ProductNo3PhotoStatus",
            "ProductNo4TitleStatus", "ProductNo4DescriptionStatus", "ProductNo4PhotoStatus",
            "ProductNo5TitleStatus", "ProductNo5DescriptionStatus", "ProductNo5PhotoStatus"
        ]
        
        # CRITICAL URL fields - Must be populated with accurate content
        self.critical_url_fields = [
            # Audio files - quality/accuracy required
            "IntroMp3", "OutroMp3", "Product1Mp3", "Product2Mp3", "Product3Mp3", "Product4Mp3", "Product5Mp3",
            # Photo files - accuracy CRUCIAL for product reviews
            "IntroPhoto", "OutroPhoto",
            # Product photo reference links - MUST be accurate for product countdown
            "ProductNo1Photo", "ProductNo2Photo", "ProductNo3Photo", "ProductNo4Photo", "ProductNo5Photo"
        ]
        
        print("🛡️ Enhanced Video Prerequisite Control Server initialized")
        print(f"🚨 Critical status columns: {len(self.critical_status_columns)}")
        print(f"🚨 Critical URL fields: {len(self.critical_url_fields)}")
        print(f"📋 Total critical prerequisites: {len(self.critical_status_columns) + len(self.critical_url_fields)}")
        print("⚠️  POLICY: Any critical failure = Video generation STOPS")
    
    async def validate_with_retry_protection(self, record_id: str) -> Dict[str, Any]:
        """
        Enhanced validation with retry protection and critical failure detection
        """
        try:
            # Import required servers
            from mcp_servers.airtable_server import AirtableMCPServer
            from mcp_servers.prerequisite_retry_agent_server import create_prerequisite_retry_agent_server
            
            airtable = AirtableMCPServer(
                api_key=self.airtable_api_key,
                base_id=self.airtable_base_id,
                table_name=self.airtable_table_name
            )
            
            # Get current record data
            record = await airtable.get_record(record_id)
            fields = record.get('fields', {})
            
            validation_results = {
                "record_id": record_id,
                "validation_timestamp": datetime.now().isoformat(),
                "critical_status_validation": {},
                "critical_url_validation": {},
                "critical_failures": [],
                "retry_candidates": [],
                "overall_status": "checking",
                "video_decision": "pending",
                "critical_count": 0,
                "ready_count": 0,
                "total_critical": len(self.critical_status_columns) + len(self.critical_url_fields)
            }
            
            # Validate critical status columns
            for column in self.critical_status_columns:
                current_value = fields.get(column, "")
                is_ready = current_value == "Ready"
                
                validation_results["critical_status_validation"][column] = {
                    "current_value": current_value,
                    "required_value": "Ready",
                    "is_valid": is_ready,
                    "component_type": "status_column"
                }
                
                if is_ready:
                    validation_results["ready_count"] += 1
                else:
                    # Critical status not ready
                    validation_results["critical_failures"].append({
                        "field": column,
                        "type": "critical_status",
                        "current": current_value,
                        "required": "Ready",
                        "severity": "critical"
                    })
            
            # Validate critical URL fields
            for field in self.critical_url_fields:
                current_value = fields.get(field, "")
                has_valid_url = bool(current_value and current_value.strip() and 
                                   (current_value.startswith('http') or current_value.startswith('https')))
                
                validation_results["critical_url_validation"][field] = {
                    "current_value": current_value[:100] + "..." if len(str(current_value)) > 100 else current_value,
                    "has_valid_url": has_valid_url,
                    "is_valid": has_valid_url,
                    "component_type": "url_field"
                }
                
                if has_valid_url:
                    validation_results["ready_count"] += 1
                else:
                    # Critical URL missing or invalid
                    validation_results["critical_failures"].append({
                        "field": field,
                        "type": "critical_url",
                        "current": "empty" if not current_value else "invalid_url",
                        "required": "valid_https_url",
                        "severity": "critical"
                    })
            
            # Count critical failures
            validation_results["critical_count"] = len(validation_results["critical_failures"])
            
            # Make video generation decision
            if validation_results["critical_count"] == 0:
                # ALL critical prerequisites met
                validation_results["overall_status"] = "all_critical_ready"
                validation_results["video_decision"] = "approved"
                validation_results["can_produce_video"] = True
                
                print(f"✅ ALL CRITICAL PREREQUISITES MET for record {record_id}")
                print(f"🎬 VIDEO GENERATION: APPROVED")
                print(f"📊 Success: {validation_results['ready_count']}/{validation_results['total_critical']} prerequisites ready")
                
            else:
                # Critical failures detected
                validation_results["overall_status"] = "critical_failures_detected"
                validation_results["video_decision"] = "blocked_critical_failures"
                validation_results["can_produce_video"] = False
                
                print(f"🚨 CRITICAL FAILURES DETECTED for record {record_id}")
                print(f"🚫 VIDEO GENERATION: BLOCKED")
                print(f"❌ Critical failures: {validation_results['critical_count']}")
                print(f"📊 Status: {validation_results['ready_count']}/{validation_results['total_critical']} prerequisites ready")
                
                # Log specific critical failures
                for failure in validation_results["critical_failures"]:
                    print(f"   🔴 {failure['field']}: {failure['current']} (needs: {failure['required']})")
            
            return validation_results
            
        except Exception as e:
            print(f"❌ Error in enhanced validation: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "record_id": record_id,
                "overall_status": "validation_error",
                "video_decision": "blocked_error"
            }
    
    async def handle_critical_failures(self, record_id: str, validation_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle critical failures with retry attempts and notifications
        """
        try:
            from mcp_servers.prerequisite_retry_agent_server import create_prerequisite_retry_agent_server
            
            retry_agent = create_prerequisite_retry_agent_server()
            
            print(f"🔄 Handling {len(validation_results['critical_failures'])} critical failures for record {record_id}")
            
            retry_results = {
                "record_id": record_id,
                "timestamp": datetime.now().isoformat(),
                "retry_attempts": [],
                "successful_retries": 0,
                "failed_retries": 0,
                "final_decision": "pending"
            }
            
            # Attempt retry for each critical failure
            for failure in validation_results["critical_failures"]:
                component = failure["field"]
                
                print(f"🔄 Attempting retry for critical component: {component}")
                
                retry_result = await retry_agent.execute_smart_retry(
                    record_id, 
                    component, 
                    failure
                )
                
                retry_results["retry_attempts"].append(retry_result)
                
                if retry_result.get("success"):
                    retry_results["successful_retries"] += 1
                    print(f"✅ Retry successful for {component}")
                else:
                    retry_results["failed_retries"] += 1
                    print(f"❌ Retry failed for {component}")
            
            # Final decision after retries
            if retry_results["failed_retries"] > 0:
                # Still have critical failures after retry
                retry_results["final_decision"] = "critical_failure_stop_video"
                
                # Send critical failure notification
                failed_components = [
                    attempt for attempt in retry_results["retry_attempts"] 
                    if not attempt.get("success")
                ]
                
                notification_result = await retry_agent.send_critical_failure_notification(
                    record_id, 
                    failed_components
                )
                
                retry_results["notification_sent"] = notification_result.get("success", False)
                
                print(f"🚨 FINAL DECISION: VIDEO GENERATION STOPPED")
                print(f"📧 Notification sent: {retry_results['notification_sent']}")
                
            else:
                # All retries successful
                retry_results["final_decision"] = "retries_successful_proceed"
                print(f"✅ All retries successful - video can proceed")
            
            return retry_results
            
        except Exception as e:
            print(f"❌ Error handling critical failures: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "record_id": record_id,
                "final_decision": "error_stop_video"
            }
    
    async def update_video_production_status_enhanced(self, record_id: str) -> Dict[str, Any]:
        """
        Enhanced VideoProductionRDY update with critical failure protection
        """
        try:
            # Step 1: Validate with retry protection
            validation = await self.validate_with_retry_protection(record_id)
            
            if not validation.get("success", True):
                return validation
            
            # Step 2: Handle critical failures if they exist
            if validation["critical_count"] > 0:
                retry_results = await self.handle_critical_failures(record_id, validation)
                
                if retry_results["final_decision"] == "critical_failure_stop_video":
                    # Critical failures persist - STOP video generation
                    return await self._set_video_production_failed(record_id, validation, retry_results)
                elif retry_results["final_decision"] == "retries_successful_proceed":
                    # Retries successful - re-validate and proceed
                    validation = await self.validate_with_retry_protection(record_id)
            
            # Step 3: Update VideoProductionRDY based on final validation
            from mcp_servers.airtable_server import AirtableMCPServer
            airtable = AirtableMCPServer(
                api_key=self.airtable_api_key,
                base_id=self.airtable_base_id,
                table_name=self.airtable_table_name
            )
            
            if validation["can_produce_video"]:
                # All critical prerequisites met - APPROVE video
                new_status = "Ready"
                action = "approved_all_critical_met"
                message = "🎬 ALL CRITICAL PREREQUISITES VALIDATED - Video production APPROVED"
                
                update_data = {"VideoProductionRDY": "Ready"}
                await airtable.update_record(record_id, update_data)
                
                print(f"🎬 VideoProductionRDY set to 'Ready' for record {record_id}")
                
            else:
                # Critical failures remain - BLOCK video
                new_status = "Failed"
                action = "blocked_critical_failures"
                message = f"🚫 CRITICAL FAILURES - Video production BLOCKED ({validation['critical_count']} failures)"
                
                update_data = {
                    "VideoProductionRDY": "Failed",
                    "FailureReason": f"Critical prerequisites failed: {validation['critical_count']} failures"
                }
                await airtable.update_record(record_id, update_data)
                
                print(f"🚫 VideoProductionRDY set to 'Failed' for record {record_id}")
            
            return {
                "success": True,
                "record_id": record_id,
                "action": action,
                "new_status": new_status,
                "message": message,
                "validation_details": validation,
                "can_produce_video": validation["can_produce_video"],
                "critical_summary": {
                    "total_critical": validation["total_critical"],
                    "ready_count": validation["ready_count"],
                    "critical_failures": validation["critical_count"],
                    "completion_percentage": round((validation["ready_count"] / validation["total_critical"]) * 100, 1)
                }
            }
            
        except Exception as e:
            print(f"❌ Error in enhanced status update: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "record_id": record_id,
                "action": "update_failed"
            }
    
    async def _set_video_production_failed(self, record_id: str, validation: Dict[str, Any], retry_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Set VideoProductionRDY to Failed with detailed failure information
        """
        try:
            from mcp_servers.airtable_server import AirtableMCPServer
            airtable = AirtableMCPServer(
                api_key=self.airtable_api_key,
                base_id=self.airtable_base_id,
                table_name=self.airtable_table_name
            )
            
            # Compile failure details
            failed_components = [f["field"] for f in validation["critical_failures"]]
            failure_summary = f"Critical components failed after retry: {', '.join(failed_components)}"
            
            # Update Airtable
            update_data = {
                "VideoProductionRDY": "Failed",
                "FailureReason": failure_summary,
                "Status": "Critical_Failure"  # Mark as special failure type
            }
            
            await airtable.update_record(record_id, update_data)
            
            print(f"🚨 CRITICAL FAILURE: Record {record_id} marked as Failed")
            print(f"📋 Failed components: {', '.join(failed_components)}")
            
            return {
                "success": True,
                "record_id": record_id,
                "action": "critical_failure_video_blocked",
                "new_status": "Failed",
                "message": "🚨 CRITICAL FAILURE: Video generation permanently blocked",
                "failed_components": failed_components,
                "can_produce_video": False,
                "notification_sent": retry_results.get("notification_sent", False),
                "manual_intervention_required": True
            }
            
        except Exception as e:
            print(f"❌ Error setting failure status: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "record_id": record_id
            }

# Factory function for easy import
def create_enhanced_video_prerequisite_control_server():
    """Factory function to create EnhancedVideoPrerequisiteControlServer with loaded config"""
    config = load_config()
    return EnhancedVideoPrerequisiteControlServer(config)

# Test function
async def test_enhanced_system():
    """Test the enhanced prerequisite system"""
    print("🧪 Testing Enhanced Video Prerequisite Control System...")
    
    server = create_enhanced_video_prerequisite_control_server()
    test_record_id = "rec_test_enhanced"
    
    try:
        # Test enhanced validation
        print("\n1️⃣ Testing enhanced validation...")
        validation = await server.validate_with_retry_protection(test_record_id)
        print(f"Validation result: {validation.get('video_decision', 'unknown')}")
        
        # Test status update
        print("\n2️⃣ Testing enhanced status update...")
        update_result = await server.update_video_production_status_enhanced(test_record_id)
        print(f"Update result: {update_result.get('new_status', 'unknown')}")
        
        print("\n✅ Enhanced system test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    # Run test
    asyncio.run(test_enhanced_system())