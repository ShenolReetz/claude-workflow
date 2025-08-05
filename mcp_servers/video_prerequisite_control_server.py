#!/usr/bin/env python3
"""
Video Prerequisite Control Server - Production Version
Manages VideoProductionRDY column based on all prerequisite validation

Security System: Only allows video generation when ALL prerequisites are validated
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

class VideoPrerequisiteControlServer:
    def __init__(self, config: Dict[str, Any]):
        """Initialize the Video Prerequisite Control Server with configuration"""
        self.config = config
        self.airtable_api_key = config['airtable_api_key']
        self.airtable_base_id = config['airtable_base_id']
        self.airtable_table_name = config['airtable_table_name']
        
        # Status columns that MUST be "Ready" for video production
        self.required_status_columns = [
            # Video content validation
            "VideoTitleStatus",
            "VideoDescriptionStatus", 
            
            # Product 1 validation
            "ProductNo1TitleStatus",
            "ProductNo1DescriptionStatus", 
            "ProductNo1PhotoStatus",
            
            # Product 2 validation
            "ProductNo2TitleStatus",
            "ProductNo2DescriptionStatus",
            "ProductNo2PhotoStatus",
            
            # Product 3 validation  
            "ProductNo3TitleStatus",
            "ProductNo3DescriptionStatus",
            "ProductNo3PhotoStatus",
            
            # Product 4 validation
            "ProductNo4TitleStatus", 
            "ProductNo4DescriptionStatus",
            "ProductNo4PhotoStatus",
            
            # Product 5 validation
            "ProductNo5TitleStatus",
            "ProductNo5DescriptionStatus", 
            "ProductNo5PhotoStatus"
        ]
        
        # URL fields that MUST have values for video production
        self.required_url_fields = [
            # Audio files
            "IntroMp3",
            "OutroMp3", 
            "Product1Mp3",
            "Product2Mp3",
            "Product3Mp3",
            "Product4Mp3",
            "Product5Mp3",
            
            # Photo files (intro/outro)
            "IntroPhoto",
            "OutroPhoto",
            
            # Product photo reference links (OpenAI generated)
            "ProductNo1Photo",
            "ProductNo2Photo", 
            "ProductNo3Photo",
            "ProductNo4Photo",
            "ProductNo5Photo"
        ]
        
        print("🛡️ Video Prerequisite Control Server initialized")
        print(f"📋 Monitoring {len(self.required_status_columns)} status columns")
        print(f"🔗 Monitoring {len(self.required_url_fields)} URL fields")
    
    async def initialize_video_production_status(self, record_id: str) -> Dict[str, Any]:
        """
        Set VideoProductionRDY to 'Pending' when title is first selected
        This is Step 1 of the workflow - marks the record as "in process"
        """
        try:
            # Import Airtable server
            from mcp_servers.airtable_server import AirtableMCPServer
            airtable = AirtableMCPServer(
                api_key=self.airtable_api_key,
                base_id=self.airtable_base_id,
                table_name=self.airtable_table_name
            )
            
            # Set VideoProductionRDY to Pending
            update_data = {
                "VideoProductionRDY": "Pending"
            }
            
            result = await airtable.update_record(record_id, update_data)
            
            print(f"✅ Initialized VideoProductionRDY to 'Pending' for record {record_id}")
            return {
                "success": True,
                "record_id": record_id,
                "action": "initialized_to_pending",
                "status": "Pending",
                "message": "Video production status set to Pending - prerequisites validation required"
            }
            
        except Exception as e:
            print(f"❌ Error initializing VideoProductionRDY: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "record_id": record_id,
                "action": "initialize_failed"
            }
    
    async def validate_all_prerequisites(self, record_id: str) -> Dict[str, Any]:
        """
        Comprehensive validation of all prerequisites for video production
        Returns detailed status of each requirement
        """
        try:
            # Import Airtable server
            from mcp_servers.airtable_server import AirtableMCPServer
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
                "status_columns": {},
                "url_fields": {},
                "overall_status": "checking",
                "missing_prerequisites": [],
                "ready_count": 0,
                "total_requirements": len(self.required_status_columns) + len(self.required_url_fields)
            }
            
            # Validate status columns (must be "Ready")
            for column in self.required_status_columns:
                current_value = fields.get(column, "")
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
            
            # Validate URL fields (must have valid URLs)
            for field in self.required_url_fields:
                current_value = fields.get(field, "")
                has_url = bool(current_value and current_value.strip())
                
                validation_results["url_fields"][field] = {
                    "current_value": current_value[:100] + "..." if len(str(current_value)) > 100 else current_value,
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
                print(f"✅ ALL PREREQUISITES MET for record {record_id}")
                print(f"📊 {validation_results['ready_count']}/{validation_results['total_requirements']} requirements satisfied")
            else:
                validation_results["overall_status"] = "pending_prerequisites"
                validation_results["can_produce_video"] = False
                missing_count = len(validation_results["missing_prerequisites"])
                print(f"⚠️ {missing_count} prerequisites missing for record {record_id}")
                print(f"📊 {validation_results['ready_count']}/{validation_results['total_requirements']} requirements satisfied")
            
            return validation_results
            
        except Exception as e:
            print(f"❌ Error validating prerequisites: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "record_id": record_id,
                "overall_status": "validation_error"
            }
    
    async def update_video_production_status(self, record_id: str) -> Dict[str, Any]:
        """
        Update VideoProductionRDY status based on prerequisite validation
        Sets to 'Ready' only if ALL prerequisites are met
        """
        try:
            # Validate all prerequisites first
            validation = await self.validate_all_prerequisites(record_id)
            
            if not validation.get("success", True):
                return validation
            
            # Import Airtable server for updates
            from mcp_servers.airtable_server import AirtableMCPServer
            airtable = AirtableMCPServer(
                api_key=self.airtable_api_key,
                base_id=self.airtable_base_id,
                table_name=self.airtable_table_name
            )
            
            # Determine new status
            if validation["can_produce_video"]:
                new_status = "Ready"
                action = "approved_for_video_production"
                message = "🎬 ALL PREREQUISITES MET - Video production APPROVED"
                
                # Update VideoProductionRDY to Ready
                update_data = {"VideoProductionRDY": "Ready"}
                await airtable.update_record(record_id, update_data)
                
                print(f"🎬 VideoProductionRDY set to 'Ready' for record {record_id}")
                
            else:
                new_status = "Pending"
                action = "waiting_for_prerequisites"
                missing_count = len(validation["missing_prerequisites"])
                message = f"⏳ {missing_count} prerequisites still missing - keeping status as Pending"
                
                # Ensure VideoProductionRDY remains Pending
                update_data = {"VideoProductionRDY": "Pending"}
                await airtable.update_record(record_id, update_data)
                
                print(f"⏳ VideoProductionRDY kept as 'Pending' for record {record_id}")
            
            return {
                "success": True,
                "record_id": record_id,
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
            print(f"❌ Error updating VideoProductionRDY status: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "record_id": record_id,
                "action": "update_failed"
            }
    
    async def check_video_production_eligibility(self, record_id: str) -> Dict[str, Any]:
        """
        Quick check if record is eligible for video production
        Used before starting video generation process
        """
        try:
            # Import Airtable server
            from mcp_servers.airtable_server import AirtableMCPServer
            airtable = AirtableMCPServer(
                api_key=self.airtable_api_key,
                base_id=self.airtable_base_id,
                table_name=self.airtable_table_name
            )
            
            # Get current record data
            record = await airtable.get_record(record_id)
            fields = record.get('fields', {})
            
            # Check VideoProductionRDY status
            video_production_status = fields.get('VideoProductionRDY', '')
            
            if video_production_status == "Ready":
                print(f"✅ Record {record_id} is APPROVED for video production")
                return {
                    "success": True,
                    "record_id": record_id,
                    "eligible": True,
                    "status": "Ready",
                    "message": "🎬 APPROVED: Record is ready for video production",
                    "action_required": "proceed_with_video_generation"
                }
            elif video_production_status == "Pending":
                print(f"⚠️ Record {record_id} is NOT ready for video production")
                return {
                    "success": True,
                    "record_id": record_id,
                    "eligible": False,
                    "status": "Pending",
                    "message": "⏳ BLOCKED: Prerequisites not yet complete",
                    "action_required": "complete_prerequisites_first"
                }
            else:
                print(f"❓ Record {record_id} has unknown VideoProductionRDY status: {video_production_status}")
                return {
                    "success": True,
                    "record_id": record_id,
                    "eligible": False,
                    "status": video_production_status,
                    "message": f"❓ UNKNOWN: VideoProductionRDY status is '{video_production_status}'",
                    "action_required": "initialize_prerequisite_system"
                }
                
        except Exception as e:
            print(f"❌ Error checking video production eligibility: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "record_id": record_id,
                "eligible": False,
                "action_required": "fix_error_and_retry"
            }
    
    async def get_prerequisite_status_report(self, record_id: str) -> Dict[str, Any]:
        """
        Generate comprehensive prerequisite status report
        Useful for debugging and monitoring workflow progress
        """
        try:
            validation = await self.validate_all_prerequisites(record_id)
            
            if not validation.get("success", True):
                return validation
            
            # Generate human-readable report
            report = {
                "record_id": record_id,
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
            
            # Generate recommendation
            if validation["can_produce_video"]:
                report["recommendation"] = "🎬 ALL CLEAR: Ready to proceed with video generation"
            elif validation["ready_count"] == 0:
                report["recommendation"] = "🚨 START HERE: No prerequisites completed yet - begin with content generation"
            elif validation["ready_count"] < validation["total_requirements"] / 2:
                report["recommendation"] = "⚡ IN PROGRESS: Continue with content and media generation"
            else:
                report["recommendation"] = "🔥 ALMOST READY: Complete remaining prerequisites to unlock video production"
            
            print(f"📊 Generated prerequisite report for record {record_id}")
            print(f"🎯 Status: {report['summary']['completion_percentage']}% complete")
            
            return report
            
        except Exception as e:
            print(f"❌ Error generating prerequisite report: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "record_id": record_id
            }

# Factory function for easy import
def create_video_prerequisite_control_server():
    """Factory function to create VideoPrerequisiteControlServer with loaded config"""
    config = load_config()
    return VideoPrerequisiteControlServer(config)

# Test functions for development
async def test_prerequisite_system():
    """Test the prerequisite validation system"""
    print("🧪 Testing Video Prerequisite Control System...")
    
    server = create_video_prerequisite_control_server()
    
    # Test with a sample record ID (replace with actual ID)
    test_record_id = "rec123sample"  # Replace with real record ID
    
    try:
        # Test 1: Initialize status
        print("\n1️⃣ Testing initialization...")
        init_result = await server.initialize_video_production_status(test_record_id)
        print(f"Init Result: {init_result}")
        
        # Test 2: Validate prerequisites
        print("\n2️⃣ Testing prerequisite validation...")
        validation_result = await server.validate_all_prerequisites(test_record_id)
        print(f"Validation Result: {json.dumps(validation_result, indent=2)}")
        
        # Test 3: Update status
        print("\n3️⃣ Testing status update...")
        update_result = await server.update_video_production_status(test_record_id)
        print(f"Update Result: {update_result}")
        
        # Test 4: Check eligibility
        print("\n4️⃣ Testing eligibility check...")
        eligibility_result = await server.check_video_production_eligibility(test_record_id)
        print(f"Eligibility Result: {eligibility_result}")
        
        # Test 5: Generate report
        print("\n5️⃣ Testing status report...")
        report_result = await server.get_prerequisite_status_report(test_record_id)
        print(f"Report Result: {json.dumps(report_result, indent=2)}")
        
        print("\n✅ All tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    # Run tests
    asyncio.run(test_prerequisite_system())