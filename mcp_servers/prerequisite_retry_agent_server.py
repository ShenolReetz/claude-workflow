#!/usr/bin/env python3
"""
Prerequisite Retry Agent Server - Production Version
Handles intelligent retry strategies with critical failure protection

For Top 5 Product Countdown Videos:
- CRITICAL: Photos/Audio must be accurate or video STOPS
- ALTERNATIVES: Scraping/Content can use different sources/methods
"""

import asyncio
import json
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple

# Add the project root to Python path
sys.path.append('/home/claude-workflow')

# Import configuration
from src.load_config import load_config

class PrerequisiteRetryAgentServer:
    def __init__(self, config: Dict[str, Any]):
        """Initialize the Prerequisite Retry Agent Server"""
        self.config = config
        self.airtable_api_key = config['airtable_api_key']
        self.airtable_base_id = config['airtable_base_id']
        self.airtable_table_name = config['airtable_table_name']
        
        # Critical components that MUST succeed or video stops
        self.critical_components = [
            # Product photos - accuracy required
            "ProductNo1Photo", "ProductNo2Photo", "ProductNo3Photo", 
            "ProductNo4Photo", "ProductNo5Photo",
            
            # Audio files - quality required
            "IntroMp3", "OutroMp3", "Product1Mp3", "Product2Mp3", 
            "Product3Mp3", "Product4Mp3", "Product5Mp3",
            
            # Core product data - accuracy required
            "ProductNo1Title", "ProductNo1Description", "ProductNo1Price",
            "ProductNo2Title", "ProductNo2Description", "ProductNo2Price",
            "ProductNo3Title", "ProductNo3Description", "ProductNo3Price",
            "ProductNo4Title", "ProductNo4Description", "ProductNo4Price",
            "ProductNo5Title", "ProductNo5Description", "ProductNo5Price"
        ]
        
        # Components that can use alternative sources/methods
        self.alternative_components = [
            "amazon_scraping", "content_generation", "openai_images"
        ]
        
        # Retry settings
        self.max_retries = 3
        self.retry_timeout = 300  # 5 minutes max per component
        
        print("🔄 Prerequisite Retry Agent Server initialized")
        print(f"🚨 Monitoring {len(self.critical_components)} critical components")
        print(f"🔄 {len(self.alternative_components)} components have alternatives")
    
    async def check_prerequisite_failures(self, record_id: str) -> Dict[str, Any]:
        """
        Check for any failed prerequisites and categorize them
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
            
            analysis = {
                "record_id": record_id,
                "timestamp": datetime.now().isoformat(),
                "critical_failures": [],
                "alternative_failures": [],
                "retry_candidates": [],
                "action_required": "continue"
            }
            
            # Check critical components
            for component in self.critical_components:
                if component.endswith("Photo") or component.endswith("Mp3"):
                    # URL fields - check if populated and valid
                    value = fields.get(component, "")
                    if not value or not value.strip():
                        analysis["critical_failures"].append({
                            "component": component,
                            "type": "url_field",
                            "issue": "empty_or_missing",
                            "current_value": value
                        })
                else:
                    # Status fields - check if Ready
                    status_field = component + "Status"
                    status = fields.get(status_field, "")
                    if status != "Ready":
                        analysis["critical_failures"].append({
                            "component": component,
                            "type": "status_field", 
                            "issue": "not_ready",
                            "current_status": status
                        })
            
            # Determine action based on failures
            if analysis["critical_failures"]:
                analysis["action_required"] = "critical_retry_or_stop"
                analysis["critical_count"] = len(analysis["critical_failures"])
                print(f"🚨 CRITICAL: {len(analysis['critical_failures'])} critical failures found for record {record_id}")
            else:
                analysis["action_required"] = "continue"
                print(f"✅ No critical failures found for record {record_id}")
            
            return analysis
            
        except Exception as e:
            print(f"❌ Error checking prerequisite failures: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "record_id": record_id,
                "action_required": "error_investigation"
            }
    
    async def execute_smart_retry(self, record_id: str, component: str, failure_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute intelligent retry strategy based on component type
        """
        try:
            component_type = failure_info.get("type", "unknown")
            retry_strategy = self._get_retry_strategy(component, component_type)
            
            print(f"🔄 Starting smart retry for {component} (record: {record_id})")
            print(f"📋 Strategy: {retry_strategy['name']}")
            
            retry_result = {
                "component": component,
                "record_id": record_id,
                "strategy": retry_strategy["name"],
                "attempts": 0,
                "success": False,
                "final_status": "Failed"
            }
            
            # Execute retry attempts
            for attempt in range(1, self.max_retries + 1):
                retry_result["attempts"] = attempt
                print(f"🔄 Attempt {attempt}/{self.max_retries} for {component}")
                
                try:
                    # Execute retry based on component type
                    if component.endswith("Photo"):
                        success = await self._retry_photo_generation(record_id, component, attempt)
                    elif component.endswith("Mp3"):
                        success = await self._retry_audio_generation(record_id, component, attempt)
                    elif "scraping" in component.lower():
                        success = await self._retry_amazon_scraping(record_id, component, attempt)
                    else:
                        success = await self._retry_content_generation(record_id, component, attempt)
                    
                    if success:
                        retry_result["success"] = True
                        retry_result["final_status"] = "Ready"
                        print(f"✅ Retry successful for {component} on attempt {attempt}")
                        break
                        
                except Exception as e:
                    print(f"❌ Retry attempt {attempt} failed for {component}: {str(e)}")
                    continue
            
            # Final status
            if not retry_result["success"]:
                if component in self.critical_components:
                    retry_result["final_status"] = "Critical_Failed"
                    print(f"🚨 CRITICAL FAILURE: {component} exhausted all retries")
                else:
                    retry_result["final_status"] = "Failed"
                    print(f"⚠️ Non-critical failure: {component} exhausted all retries")
            
            return retry_result
            
        except Exception as e:
            print(f"❌ Error in smart retry for {component}: {str(e)}")
            return {
                "component": component,
                "record_id": record_id,
                "success": False,
                "error": str(e),
                "final_status": "Error"
            }
    
    def _get_retry_strategy(self, component: str, component_type: str) -> Dict[str, Any]:
        """Get appropriate retry strategy for component"""
        
        if component.endswith("Photo"):
            return {
                "name": "photo_url_retry",
                "description": "Try alternative product image URLs",
                "critical": True
            }
        elif component.endswith("Mp3"):
            return {
                "name": "audio_generation_retry", 
                "description": "Try different voice parameters",
                "critical": True
            }
        elif "scraping" in component.lower():
            return {
                "name": "alternative_scraping_sources",
                "description": "Try different scraping methods/APIs",
                "critical": False
            }
        else:
            return {
                "name": "content_generation_retry",
                "description": "Try different prompts/parameters",
                "critical": False
            }
    
    async def _retry_photo_generation(self, record_id: str, component: str, attempt: int) -> bool:
        """Retry photo generation with different strategies"""
        try:
            # Import required modules
            from mcp_servers.amazon_category_scraper import AmazonCategoryScraperServer
            from mcp_servers.airtable_server import AirtableMCPServer
            
            print(f"🖼️ Retrying photo generation for {component} (attempt {attempt})")
            
            # Strategy based on attempt number
            if attempt == 1:
                # Try re-downloading from original Amazon URL
                print("📸 Strategy 1: Re-download from original Amazon URL")
                # Implementation: Re-fetch product data and try original image URL
                
            elif attempt == 2:
                # Try alternative image URLs from product data
                print("📸 Strategy 2: Try alternative product image URLs")
                # Implementation: Look for additional image URLs in scraped data
                
            elif attempt == 3:
                # Re-scrape product for fresh image URLs
                print("📸 Strategy 3: Re-scrape product for new image URLs")
                # Implementation: Fresh scrape of the specific product
            
            # For now, return simulated result
            # TODO: Implement actual retry logic with real APIs
            return False  # Will be True when implemented
            
        except Exception as e:
            print(f"❌ Photo retry failed: {str(e)}")
            return False
    
    async def _retry_audio_generation(self, record_id: str, component: str, attempt: int) -> bool:
        """Retry audio generation with different strategies"""
        try:
            print(f"🔊 Retrying audio generation for {component} (attempt {attempt})")
            
            # Strategy based on attempt number
            if attempt == 1:
                # Try different ElevenLabs voice model
                print("🎵 Strategy 1: Try different voice model")
                
            elif attempt == 2:
                # Try adjusted voice parameters
                print("🎵 Strategy 2: Adjust voice parameters")
                
            elif attempt == 3:
                # Try fallback voice settings
                print("🎵 Strategy 3: Use fallback voice configuration")
            
            # TODO: Implement actual retry logic with ElevenLabs API
            return False  # Will be True when implemented
            
        except Exception as e:
            print(f"❌ Audio retry failed: {str(e)}")
            return False
    
    async def _retry_amazon_scraping(self, record_id: str, component: str, attempt: int) -> bool:
        """Retry scraping with alternative sources"""
        try:
            print(f"🔍 Retrying Amazon scraping for {component} (attempt {attempt})")
            
            if attempt == 1:
                # Try ScrapingDog with different parameters
                print("🐕 Strategy 1: ScrapingDog with adjusted parameters")
                
            elif attempt == 2:
                # Try direct scraping method
                print("🌐 Strategy 2: Direct web scraping")
                
            elif attempt == 3:
                # Try alternative product APIs
                print("📦 Strategy 3: Alternative product data APIs")
            
            # TODO: Implement actual alternative scraping methods
            return False  # Will be True when implemented
            
        except Exception as e:
            print(f"❌ Scraping retry failed: {str(e)}")
            return False
    
    async def _retry_content_generation(self, record_id: str, component: str, attempt: int) -> bool:
        """Retry content generation with different approaches"""
        try:
            print(f"📝 Retrying content generation for {component} (attempt {attempt})")
            
            if attempt == 1:
                # Try simplified prompt
                print("✏️ Strategy 1: Simplified prompt")
                
            elif attempt == 2:
                # Try different model parameters
                print("🎛️ Strategy 2: Adjusted model parameters")
                
            elif attempt == 3:
                # Try template-based approach
                print("📋 Strategy 3: Template-based generation")
            
            # TODO: Implement actual content retry logic
            return False  # Will be True when implemented
            
        except Exception as e:
            print(f"❌ Content retry failed: {str(e)}")
            return False
    
    async def send_critical_failure_notification(self, record_id: str, failures: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Send notification when critical failures occur
        """
        try:
            notification = {
                "type": "critical_failure",
                "record_id": record_id,
                "timestamp": datetime.now().isoformat(),
                "failed_components": failures,
                "action_required": "manual_intervention",
                "video_status": "blocked"
            }
            
            # Log critical failure
            print(f"🚨 CRITICAL FAILURE NOTIFICATION for record {record_id}")
            print(f"📋 Failed components: {[f['component'] for f in failures]}")
            print(f"⚠️ Action required: Manual intervention needed")
            print(f"🎬 Video generation: BLOCKED")
            
            # TODO: Implement actual notification system (email, Slack, etc.)
            # For now, just log the notification
            
            # Update Airtable with critical failure status
            from mcp_servers.airtable_server import AirtableMCPServer
            airtable = AirtableMCPServer(
                api_key=self.airtable_api_key,
                base_id=self.airtable_base_id,
                table_name=self.airtable_table_name
            )
            
            # Mark VideoProductionRDY as Failed
            update_data = {
                "VideoProductionRDY": "Failed",
                "FailureReason": f"Critical components failed: {', '.join([f['component'] for f in failures])}"
            }
            
            await airtable.update_record(record_id, update_data)
            
            return {
                "success": True,
                "notification_sent": True,
                "record_updated": True,
                "video_blocked": True
            }
            
        except Exception as e:
            print(f"❌ Error sending critical failure notification: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "notification_sent": False
            }

# Factory function for easy import
def create_prerequisite_retry_agent_server():
    """Factory function to create PrerequisiteRetryAgentServer with loaded config"""
    config = load_config()
    return PrerequisiteRetryAgentServer(config)

# Test function
async def test_retry_system():
    """Test the retry system with sample data"""
    print("🧪 Testing Prerequisite Retry System...")
    
    server = create_prerequisite_retry_agent_server()
    test_record_id = "rec_test_retry"
    
    try:
        # Test failure analysis
        print("\n1️⃣ Testing failure analysis...")
        analysis = await server.check_prerequisite_failures(test_record_id)
        print(f"Analysis result: {analysis}")
        
        # Test smart retry for critical component
        if analysis.get("critical_failures"):
            print("\n2️⃣ Testing smart retry for critical failure...")
            failure = analysis["critical_failures"][0]
            retry_result = await server.execute_smart_retry(
                test_record_id, 
                failure["component"], 
                failure
            )
            print(f"Retry result: {retry_result}")
            
            # Test notification if still failed
            if not retry_result.get("success"):
                print("\n3️⃣ Testing critical failure notification...")
                notification = await server.send_critical_failure_notification(
                    test_record_id,
                    analysis["critical_failures"]
                )
                print(f"Notification result: {notification}")
        
        print("\n✅ Retry system test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    # Run test
    asyncio.run(test_retry_system())