#!/usr/bin/env python3
"""
Test JSON2Video Enhanced MCP Server v2
Uses Test_json2video_schema.json for hardcoded test responses
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
import os
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestJSON2VideoEnhancedMCPServerV2:
    """Test JSON2Video Enhanced MCP Server v2 - Uses Test schema with hardcoded responses"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.json2video.com/v2"
        logger.info("🧪 Test JSON2Video Enhanced Server V2 initialized")
        
        # Load the Test schema
        schema_path = '/home/claude-workflow/Test_json2video_schema.json'
        try:
            with open(schema_path, 'r') as f:
                self.test_schema = json.load(f)
            logger.info(f"✅ Loaded Test schema from {schema_path}")
        except Exception as e:
            logger.error(f"❌ Could not load Test schema: {e}")
            self.test_schema = None
    
    async def create_perfect_timing_video(self, record_data: Dict) -> Dict[str, Any]:
        """Create video using Test_json2video_schema.json - returns hardcoded success"""
        
        logger.info("🧪 Test: Creating video with Test schema (hardcoded response)")
        
        # Simulate a delay to mimic API call
        await asyncio.sleep(1)
        
        # Return hardcoded successful response
        project_id = f"test_project_{record_data.get('record_id', '123')}"
        
        return {
            'success': True,
            'project_id': project_id,
            'video_url': f"https://assets.json2video.com/test/renders/{project_id}.mp4",
            'status': 'done',
            'duration': 55,
            'resolution': '1080x1920',
            'format': 'MP4',
            'schema_used': 'Test_json2video_schema.json',
            'features': [
                'Test schema with proper component positioning',
                'Google Drive audio URLs integrated',
                'Unsplash photo URLs for test data',
                'Hardcoded successful response',
                'No API calls made'
            ],
            'test_mode': True
        }
    
    async def get_project_status(self, project_id: str) -> Dict[str, Any]:
        """Get project status - returns hardcoded success"""
        
        logger.info(f"🧪 Test: Getting status for project {project_id} (hardcoded)")
        
        # Return hardcoded status
        return {
            'success': True,
            'project': project_id,
            'status': 'done',
            'video_url': f"https://assets.json2video.com/test/renders/{project_id}.mp4",
            'progress': 100,
            'test_mode': True
        }
    
    async def close(self):
        """Close the test server"""
        logger.info("🧪 Test JSON2Video server closed")
        pass

# Export the test class with both names for compatibility
JSON2VideoEnhancedMCPServerV2 = TestJSON2VideoEnhancedMCPServerV2
__all__ = ['TestJSON2VideoEnhancedMCPServerV2', 'JSON2VideoEnhancedMCPServerV2']