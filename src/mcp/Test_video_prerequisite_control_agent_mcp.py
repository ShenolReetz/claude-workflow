import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from mcp_servers.Test_video_prerequisite_control_server import VideoPrerequisiteControlMCPServer
from mcp_servers.Test_airtable_server import AirtableMCPServer

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
                'record_id': record_id,
                'video_production_ready': False,
                'video_production_status': 'Pending'
            }
    
    async def get_airtable_record(self, record_id: str) -> Optional[Dict[str, Any]]:
        """Get complete record data from Airtable"""
        try:
            # Use Airtable API to get specific record
            record = self.airtable_server.airtable.get(record_id)
            if record:
                logger.info(f"✅ Retrieved record {record_id} from Airtable")
                return record
            else:
                logger.error(f"❌ Record {record_id} not found in Airtable")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving record {record_id}: {e}")
            return None
    
    async def update_airtable_status(self, record_id: str, update_fields: Dict[str, str]) -> bool:
        """Update VideoProductionRDY status in Airtable"""
        try:
            logger.info(f"🔄 Updating Airtable record {record_id} with: {update_fields}")
            
            # Update the record
            self.airtable_server.airtable.update(record_id, update_fields)
            
            logger.info(f"✅ Successfully updated VideoProductionRDY status to: {update_fields.get('VideoProductionRDY')}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update Airtable record {record_id}: {e}")
            return False
    
    async def check_video_production_readiness(self, record_id: str) -> bool:
        """
        Quick check function to determine if video production can start
        Returns True if VideoProductionRDY is 'Ready', False otherwise
        """
        try:
            current_record = await self.get_airtable_record(record_id)
            if not current_record:
                return False
            
            video_production_status = current_record['fields'].get('VideoProductionRDY', 'Pending')
            
            if video_production_status == 'Ready':
                logger.info("✅ Video production is READY to start")
                return True
            else:
                logger.info(f"⏸️ Video production is NOT ready - Status: {video_production_status}")
                return False
                
        except Exception as e:
            logger.error(f"Error checking video production readiness: {e}")
            return False
    
    async def force_validate_prerequisites(self, record_id: str) -> Dict[str, Any]:
        """
        Force validation of prerequisites regardless of current status
        Useful for re-checking after fixes
        """
        logger.info(f"🔄 Force validating prerequisites for record: {record_id}")
        return await self.validate_and_update_video_production_status(record_id)

# Test function
if __name__ == "__main__":
    async def test_video_prerequisite_agent():
        # Test API keys (use test values)
        test_api_keys = {
            'airtable_api_key': 'test_key',
            'airtable_base_id': 'test_base', 
            'airtable_table_name': 'test_table'
        }
        
        agent = VideoPrerequisiteControlAgentMCP(test_api_keys)
        
        print("🧪 Testing Video Prerequisite Control Agent MCP")
        print("=" * 50)
        
        # Test validation logic with mock data
        test_record_data = {
            'fields': {
                'YouTubeTitle': 'Test Title',
                'InstagramTitle': 'Test Title',
                'TikTokTitle': 'Test Title', 
                'WordPressTitle': 'Test Title',
                'YouTubeDescription': 'Test Description',
                'InstagramCaption': 'Test Caption',
                'TikTokDescription': 'Test Description',
                'WordPressContent': 'Test Content',
                'YouTubeKeywords': 'test keywords',
                'InstagramHashtags': '#test',
                'TikTokKeywords': 'test',
                'WordPressSEO': 'test seo',
                'UniversalKeywords': 'test',
                'IntroMp3': 'https://test.com/intro.mp3',
                'OutroMp3': 'https://test.com/outro.mp3'
            }
        }
        
        # Add test product data
        for i in range(1, 6):
            test_record_data['fields'].update({
                f'ProductNo{i}Title': f'Test Product {i}',
                f'ProductNo{i}Price': f'$99.99',
                f'ProductNo{i}Rating': '4.5',
                f'ProductNo{i}Reviews': '1000',
                f'ProductNo{i}Photo': f'https://test.com/product{i}.jpg',
                f'ProductNo{i}AffiliateLink': f'https://amzn.to/test{i}',
                f'Product{i}Mp3': f'https://test.com/product{i}.mp3'
            })
        
        # Test validation with complete data
        validation_report = await agent.control_server.check_video_production_ready(test_record_data['fields'])
        
        print(f"\n📊 Validation Result: {'✅ READY' if validation_report['video_production_ready'] else '❌ NOT READY'}")
        print(f"📈 Success Rate: {validation_report['success_rate']:.1f}%")
        print(f"🎬 VideoProductionRDY Status: {validation_report['video_production_status']}")
        
        if validation_report['errors']:
            print(f"❌ Errors: {validation_report['errors']}")
        
        if validation_report['warnings']:
            print(f"⚠️ Warnings: {validation_report['warnings']}")
    
    asyncio.run(test_video_prerequisite_agent())