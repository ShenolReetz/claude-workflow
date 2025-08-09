#!/usr/bin/env python3
"""
Test Video Prerequisite Control Server - Test Version
Provides hardcoded responses for testing without API calls

This mirrors the production server but uses test data for speed
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Add the project root to Python path
sys.path.append('/home/claude-workflow')

class TestVideoPrerequisiteControlServer:
    def __init__(self):
        """Initialize the Test Video Prerequisite Control Server"""
        
        # Same status columns as production
        self.required_status_columns = [
            "VideoTitleStatus", "VideoDescriptionStatus", 
            "ProductNo1TitleStatus", "ProductNo1DescriptionStatus", "ProductNo1PhotoStatus",
            "ProductNo2TitleStatus", "ProductNo2DescriptionStatus", "ProductNo2PhotoStatus",
            "ProductNo3TitleStatus", "ProductNo3DescriptionStatus", "ProductNo3PhotoStatus",
            "ProductNo4TitleStatus", "ProductNo4DescriptionStatus", "ProductNo4PhotoStatus",
            "ProductNo5TitleStatus", "ProductNo5DescriptionStatus", "ProductNo5PhotoStatus"
        ]
        
        self.required_url_fields = [
            "IntroMp3", "OutroMp3", "Product1Mp3", "Product2Mp3", "Product3Mp3", "Product4Mp3", "Product5Mp3",
            "IntroPhoto", "OutroPhoto",
            "ProductNo1Photo", "ProductNo2Photo", "ProductNo3Photo", "ProductNo4Photo", "ProductNo5Photo"
        ]
        
        # Test data simulating different prerequisite states
        self.test_scenarios = {
            "all_ready": {
                # All status columns are "Ready"
                **{col: "Ready" for col in self.required_status_columns},
                # All URLs are populated
                **{field: f"https://drive.google.com/test_{field.lower()}.mp3" for field in self.required_url_fields}
            },
            "partially_ready": {
                # Only half of status columns are ready
                **{col: "Ready" if i < len(self.required_status_columns)//2 else "Pending" 
                   for i, col in enumerate(self.required_status_columns)},
                # Only half of URLs are populated
                **{field: f"https://drive.google.com/test_{field.lower()}.mp3" if i < len(self.required_url_fields)//2 else ""
                   for i, field in enumerate(self.required_url_fields)}
            },
            "none_ready": {
                # All status columns are "Pending"
                **{col: "Pending" for col in self.required_status_columns},
                # No URLs populated
                **{field: "" for field in self.required_url_fields}
            }
        }
        
        print("🧪 Test Video Prerequisite Control Server initialized")
        print(f"📋 Monitoring {len(self.required_status_columns)} status columns")
        print(f"🔗 Monitoring {len(self.required_url_fields)} URL fields")
        print("🎭 Test scenarios: all_ready, partially_ready, none_ready")
    
    def _get_test_scenario(self, record_id: str) -> str:
        """Determine test scenario based on record ID"""
        if "all_ready" in record_id.lower() or record_id.endswith("1"):
            return "all_ready"
        elif "partial" in record_id.lower() or record_id.endswith("2"):
            return "partially_ready"
        else:
            return "none_ready"
    
    async def initialize_video_production_status(self, record_id: str) -> Dict[str, Any]:
        """Test version: Always succeeds with mock data"""
        try:
            print(f"🧪 TEST: Initializing VideoProductionRDY to 'Pending' for record {record_id}")
            
            return {
                "success": True,
                "record_id": record_id,
                "action": "initialized_to_pending",
                "status": "Pending",
                "message": "TEST: Video production status set to Pending - prerequisites validation required"
            }
            
        except Exception as e:
            print(f"❌ TEST ERROR: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "record_id": record_id,
                "action": "initialize_failed"
            }
    
    async def validate_all_prerequisites(self, record_id: str) -> Dict[str, Any]:
        """Test version: Uses hardcoded test scenarios"""
        try:
            scenario = self._get_test_scenario(record_id)
            test_fields = self.test_scenarios[scenario]
            
            validation_results = {
                "record_id": record_id,
                "test_scenario": scenario,
                "validation_timestamp": datetime.now().isoformat(),
                "status_columns": {},
                "url_fields": {},
                "overall_status": "checking",
                "missing_prerequisites": [],
                "ready_count": 0,
                "total_requirements": len(self.required_status_columns) + len(self.required_url_fields)
            }
            
            # Validate status columns using test data
            for column in self.required_status_columns:
                current_value = test_fields.get(column, "Pending")
                is_ready = current_value == "Ready"
                
                validation_results["status_columns"][column] = {
                    "current_value": current_value,
                    "required_value": "Ready", 
                    "is_valid": is_ready
                }
                
                if is_ready:
                    validation_results["ready_count"] += 1
                else:
                    validation_results["missing_prerequisites"].append({
                        "field": column,
                        "type": "status_column",
                        "current": current_value,
                        "required": "Ready"
                    })
            
            # Validate URL fields using test data
            for field in self.required_url_fields:
                current_value = test_fields.get(field, "")
                has_url = bool(current_value and current_value.strip())
                
                validation_results["url_fields"][field] = {
                    "current_value": current_value,
                    "has_url": has_url,
                    "is_valid": has_url
                }
                
                if has_url:
                    validation_results["ready_count"] += 1
                else:
                    validation_results["missing_prerequisites"].append({
                        "field": field,
                        "type": "url_field",
                        "current": "empty" if not current_value else current_value,
                        "required": "valid_url"
                    })
            
            # Determine overall status
            all_prerequisites_met = len(validation_results["missing_prerequisites"]) == 0
            
            if all_prerequisites_met:
                validation_results["overall_status"] = "all_ready"
                validation_results["can_produce_video"] = True
                print(f"🧪✅ TEST: ALL PREREQUISITES MET for record {record_id} (scenario: {scenario})")
            else:
                validation_results["overall_status"] = "pending_prerequisites"
                validation_results["can_produce_video"] = False
                missing_count = len(validation_results["missing_prerequisites"])
                print(f"🧪⚠️ TEST: {missing_count} prerequisites missing for record {record_id} (scenario: {scenario})")
            
            print(f"📊 TEST: {validation_results['ready_count']}/{validation_results['total_requirements']} requirements satisfied")
            
            return validation_results
            
        except Exception as e:
            print(f"❌ TEST ERROR: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "record_id": record_id,
                "overall_status": "validation_error"
            }
    
    async def update_video_production_status(self, record_id: str) -> Dict[str, Any]:
        """Test version: Simulates status updates based on test scenario"""
        try:
            validation = await self.validate_all_prerequisites(record_id)
            scenario = self._get_test_scenario(record_id)
            
            if not validation.get("success", True):
                return validation
            
            # Determine new status based on test scenario
            if validation["can_produce_video"]:
                new_status = "Ready"
                action = "approved_for_video_production"
                message = f"🎬 TEST: ALL PREREQUISITES MET - Video production APPROVED (scenario: {scenario})"
                print(f"🧪🎬 TEST: VideoProductionRDY set to 'Ready' for record {record_id}")
            else:
                new_status = "Pending"
                action = "waiting_for_prerequisites"
                missing_count = len(validation["missing_prerequisites"])
                message = f"⏳ TEST: {missing_count} prerequisites missing - keeping status as Pending (scenario: {scenario})"
                print(f"🧪⏳ TEST: VideoProductionRDY kept as 'Pending' for record {record_id}")
            
            return {
                "success": True,
                "record_id": record_id,
                "test_scenario": scenario,
                "action": action,
                "new_status": new_status,
                "message": message,
                "validation_details": validation,
                "ready_for_video": validation["can_produce_video"],
                "prerequisite_summary": {
                    "ready_count": validation["ready_count"],
                    "total_requirements": validation["total_requirements"],
                    "missing_count": len(validation["missing_prerequisites"]),
                    "completion_percentage": round((validation["ready_count"] / validation["total_requirements"]) * 100, 1)
                }
            }
            
        except Exception as e:
            print(f"❌ TEST ERROR: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "record_id": record_id,
                "action": "update_failed"
            }
    
    async def check_video_production_eligibility(self, record_id: str) -> Dict[str, Any]:
        """Test version: Simulates eligibility check"""
        try:
            scenario = self._get_test_scenario(record_id)
            
            # Determine eligibility based on test scenario
            if scenario == "all_ready":
                eligible = True
                status = "Ready"
                message = "🎬 TEST: APPROVED: Record is ready for video production"
                action_required = "proceed_with_video_generation"
                print(f"🧪✅ TEST: Record {record_id} is APPROVED for video production")
            else:
                eligible = False
                status = "Pending"
                message = f"⏳ TEST: BLOCKED: Prerequisites not complete (scenario: {scenario})"
                action_required = "complete_prerequisites_first"
                print(f"🧪⚠️ TEST: Record {record_id} is NOT ready for video production")
            
            return {
                "success": True,
                "record_id": record_id,
                "test_scenario": scenario,
                "eligible": eligible,
                "status": status,
                "message": message,
                "action_required": action_required
            }
                
        except Exception as e:
            print(f"❌ TEST ERROR: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "record_id": record_id,
                "eligible": False,
                "action_required": "fix_error_and_retry"
            }
    
    async def get_prerequisite_status_report(self, record_id: str) -> Dict[str, Any]:
        """Test version: Generates mock status report"""
        try:
            validation = await self.validate_all_prerequisites(record_id)
            scenario = self._get_test_scenario(record_id)
            
            if not validation.get("success", True):
                return validation
            
            # Generate test report
            report = {
                "record_id": record_id,
                "test_scenario": scenario,
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total_requirements": validation["total_requirements"],
                    "completed": validation["ready_count"],
                    "pending": len(validation["missing_prerequisites"]),
                    "completion_percentage": round((validation["ready_count"] / validation["total_requirements"]) * 100, 1),
                    "ready_for_video": validation["can_produce_video"]
                },
                "status_breakdown": {
                    "content_status": {},
                    "product_status": {},
                    "media_files": {}
                },
                "missing_items": validation["missing_prerequisites"],
                "recommendation": ""
            }
            
            # Categorize status columns
            for column, status in validation["status_columns"].items():
                if "Video" in column:
                    report["status_breakdown"]["content_status"][column] = status
                else:
                    report["status_breakdown"]["product_status"][column] = status
            
            # Add URL field status
            report["status_breakdown"]["media_files"] = validation["url_fields"]
            
            # Generate test recommendation
            if validation["can_produce_video"]:
                report["recommendation"] = f"🎬 TEST: ALL CLEAR - Ready for video (scenario: {scenario})"
            elif validation["ready_count"] == 0:
                report["recommendation"] = f"🚨 TEST: No prerequisites completed (scenario: {scenario})"
            else:
                report["recommendation"] = f"⚡ TEST: Partial completion (scenario: {scenario})"
            
            print(f"🧪📊 TEST: Generated prerequisite report for record {record_id}")
            print(f"🎯 TEST Status: {report['summary']['completion_percentage']}% complete (scenario: {scenario})")
            
            return report
            
        except Exception as e:
            print(f"❌ TEST ERROR: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "record_id": record_id
            }

# Factory function for easy import
def create_test_video_prerequisite_control_server():
    """Factory function to create TestVideoPrerequisiteControlServer"""
    return TestVideoPrerequisiteControlServer()

# Test functions
async def test_all_scenarios():
    """Test all prerequisite scenarios"""
    print("🧪 Testing All Video Prerequisite Scenarios...")
    
    server = create_test_video_prerequisite_control_server()
    
    # Test different scenarios
    test_cases = [
        ("rec_all_ready_1", "Should be approved for video"),
        ("rec_partial_2", "Should be partially ready"),
        ("rec_none_ready_3", "Should need all prerequisites")
    ]
    
    for record_id, description in test_cases:
        print(f"\n🎭 Testing: {record_id} - {description}")
        
        try:
            # Test full workflow
            init_result = await server.initialize_video_production_status(record_id)
            validation_result = await server.validate_all_prerequisites(record_id)
            update_result = await server.update_video_production_status(record_id)
            eligibility_result = await server.check_video_production_eligibility(record_id)
            
            print(f"✅ Scenario completed: {record_id}")
            print(f"   - Ready for video: {eligibility_result.get('eligible', False)}")
            print(f"   - Completion: {update_result.get('prerequisite_summary', {}).get('completion_percentage', 0)}%")
            
        except Exception as e:
            print(f"❌ Scenario failed: {record_id} - {str(e)}")
    
    print("\n🧪 All scenario tests completed!")

# Helper function to demonstrate usage
def demonstrate_test_scenarios():
    """Show how to use different test scenarios"""
    print("""
🎭 Test Scenario Usage Guide:

1. ALL READY (record IDs ending in '1' or containing 'all_ready'):
   - All status columns: "Ready" 
   - All URLs: populated
   - Result: VideoProductionRDY = "Ready"
   
2. PARTIALLY READY (record IDs ending in '2' or containing 'partial'):
   - Half status columns: "Ready", half "Pending"
   - Half URLs: populated, half empty
   - Result: VideoProductionRDY = "Pending"
   
3. NONE READY (all other record IDs):
   - All status columns: "Pending"
   - All URLs: empty
   - Result: VideoProductionRDY = "Pending"

Example usage:
- test_record_all_ready_1 → 100% complete, approved for video
- test_record_partial_2 → ~50% complete, not ready
- test_record_none → 0% complete, not ready
    """)

if __name__ == "__main__":
    # Show demonstration
    demonstrate_test_scenarios()
    
    # Run scenario tests
    asyncio.run(test_all_scenarios())