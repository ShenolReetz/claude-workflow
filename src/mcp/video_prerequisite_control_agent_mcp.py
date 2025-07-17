import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from mcp_servers.video_prerequisite_control_server import VideoPrerequisiteControlMCPServer
from mcp_servers.airtable_server import AirtableMCPServer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoPrerequisiteControlAgentMCP:
    """
    Video Prerequisite Control Agent MCP
    Orchestrates prerequisite validation and Airtable updates
    """
    
    def __init__(self, api_keys: Dict[str, str]):
        self.api_keys = api_keys
        self.control_server = VideoPrerequisiteControlMCPServer()
        
        # Initialize Airtable server
        self.airtable_server = AirtableMCPServer(
            api_key=api_keys.get('airtable_api_key'),
            base_id=api_keys.get('airtable_base_id'),
            table_name=api_keys.get('airtable_table_name')
        )
        
    async def validate_and_update_video_production_status(self, record_id: str) -> Dict[str, Any]:
        """
        Main function to validate prerequisites and update VideoProductionRDY status
        """
        logger.info(f"🎬 Starting video production prerequisite validation for record: {record_id}")
        
        try:
            # Get current record data from Airtable (FRESH fetch to see latest platform content)
            logger.info(f"📡 Fetching FRESH record data from Airtable to see latest platform content...")
            current_record = await self.get_airtable_record(record_id)
            if not current_record:
                return {
                    'success': False,
                    'error': 'Failed to retrieve record from Airtable',
                    'record_id': record_id
                }
            
            # Debug: Log what platform fields we see
            platform_fields = ['YouTubeTitle', 'YouTubeDescription', 'TikTokTitle', 'TikTokDescription', 
                             'InstagramTitle', 'InstagramCaption', 'WordPressTitle', 'WordPressContent']
            found_platform_fields = [field for field in platform_fields if current_record['fields'].get(field)]
            logger.info(f"🔍 Platform fields found in fresh record: {found_platform_fields}")
            
            # Run prerequisite validation on fresh data
            validation_report = await self.control_server.check_video_production_ready(current_record['fields'])
            
            # Update Airtable with VideoProductionRDY status
            update_success = False
            if validation_report.get('airtable_update_required'):
                update_success = await self.update_airtable_status(
                    record_id, 
                    validation_report['airtable_update_required']
                )
            
            # Prepare final response
            response = {
                'success': True,
                'record_id': record_id,
                'video_production_ready': validation_report['video_production_ready'],
                'video_production_status': validation_report['video_production_status'],
                'airtable_updated': update_success,
                'validation_summary': {
                    'checks_passed': validation_report['checks_passed'],
                    'total_checks': validation_report['total_checks'],
                    'success_rate': validation_report['success_rate'],
                    'errors': validation_report['errors'],
                    'warnings': validation_report['warnings']
                },
                'detailed_results': validation_report['validation_results'],
                'timestamp': validation_report['timestamp']
            }
            
            # Log final status
            if validation_report['video_production_ready']:
                logger.info("✅ Video production prerequisites satisfied - VideoProductionRDY: Ready")
            else:
                logger.warning("❌ Video production prerequisites NOT satisfied - VideoProductionRDY: Pending")
                logger.warning(f"Errors: {validation_report['errors']}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error in video prerequisite validation: {e}")
            return {
                'success': False,
                'error': str(e),
                'record_id': record_id
            }
    
    async def get_airtable_record(self, record_id: str) -> Optional[Dict[str, Any]]:
        """Get record from Airtable"""
        try:
            record = await self.airtable_server.get_record(record_id)
            return record
        except Exception as e:
            logger.error(f"Error fetching record from Airtable: {e}")
            return None
    
    async def update_airtable_status(self, record_id: str, updates: Dict[str, Any]) -> bool:
        """Update Airtable record with status updates"""
        try:
            logger.info(f"📝 Updating Airtable record {record_id} with: {updates}")
            result = await self.airtable_server.update_record(record_id, updates)
            return bool(result)
        except Exception as e:
            logger.error(f"Error updating Airtable record: {e}")
            return False

# Main entry point function
async def validate_video_production_prerequisites(api_keys: Dict[str, str], record_id: str) -> Dict[str, Any]:
    """
    Main entry point for video production prerequisite validation
    """
    agent = VideoPrerequisiteControlAgentMCP(api_keys)
    return await agent.validate_and_update_video_production_status(record_id)

# Test function
async def test_video_prerequisite_validation():
    """Test the video prerequisite validation"""
    
    # Load API keys
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        api_keys = json.load(f)
    
    # Test validation
    test_record_id = "test_record_id"
    result = await validate_video_production_prerequisites(api_keys, test_record_id)
    
    print(f"Test result: {result}")
    
    return result

if __name__ == "__main__":
    asyncio.run(test_video_prerequisite_validation())