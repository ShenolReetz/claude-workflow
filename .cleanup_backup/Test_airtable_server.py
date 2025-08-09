#!/usr/bin/env python3
"""
Test Airtable MCP Server - Hardcoded responses for testing
Purpose: Test Airtable operations without consuming API tokens
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime

class TestAirtableMCPServer:
    """Test Airtable MCP Server with hardcoded responses"""
    
    def __init__(self, api_key: str, base_id: str, table_name: str):
        self.api_key = api_key  # Not used in test mode
        self.base_id = base_id  # Not used in test mode  
        self.table_name = table_name  # Not used in test mode
        
        # Hardcoded test data
        self.test_records = [
            {
                'record_id': 'test_rec_001',
                'ID': 1,
                'Title': 'Top 5 Camera & Photo Cleaning Brushes Most Popular on Amazon 2025',
                'Status': 'Pending',
                'ProductCount': 15,
                'Category': 'Camera & Photo',
                'VideoTitle': '',
                'VideoDescription': '',
                'YouTubeTitle': '',
                'YouTubeDescription': '',
                'YouTubeTags': '',
                'InstagramCaption': '',
                'WordPressTitle': '',
                'WordPressContent': '',
                'TikTokCaption': '',
                'ProductNo1Title': '',
                'ProductNo1Description': '',
                'ProductNo1Price': '',
                'ProductNo1Rating': '',
                'ProductNo1Reviews': '',
                'ProductNo1Photo': '',
                'ProductNo1AffiliateLink': '',
                'ProductNo2Title': '',
                'ProductNo2Description': '',
                'ProductNo2Price': '',
                'ProductNo2Rating': '',
                'ProductNo2Reviews': '',
                'ProductNo2Photo': '',
                'ProductNo2AffiliateLink': '',
                'ProductNo3Title': '',
                'ProductNo3Description': '',
                'ProductNo3Price': '',
                'ProductNo3Rating': '',
                'ProductNo3Reviews': '',
                'ProductNo3Photo': '',
                'ProductNo3AffiliateLink': '',
                'ProductNo4Title': '',
                'ProductNo4Description': '',
                'ProductNo4Price': '',
                'ProductNo4Rating': '',
                'ProductNo4Reviews': '',
                'ProductNo4Photo': '',
                'ProductNo4AffiliateLink': '',
                'ProductNo5Title': '',
                'ProductNo5Description': '',
                'ProductNo5Price': '',
                'ProductNo5Rating': '',
                'ProductNo5Reviews': '',
                'ProductNo5Photo': '',
                'ProductNo5AffiliateLink': ''
            }
        ]
        
        print("🧪 Test Airtable Server initialized with hardcoded data")
    
    async def get_pending_title(self) -> Optional[Dict[str, Any]]:
        """Return hardcoded pending title for testing"""
        print("📋 Returning hardcoded test title (no API call)")
        
        # Return the first pending record
        for record in self.test_records:
            if record.get('Status') == 'Pending':
                return record
        
        return None
    
    async def update_record(self, record_id: str, updates: Dict[str, Any]) -> bool:
        """Update test record with hardcoded success response"""
        print(f"📝 Test update for record {record_id}: {len(updates)} fields (no API call)")
        
        # Find and update the test record
        for record in self.test_records:
            if record['record_id'] == record_id:
                record.update(updates)
                break
        
        return True
    
    async def update_title_status(self, record_id: str, status: str, reason: str = None) -> bool:
        """Update title status with hardcoded success"""
        print(f"📊 Test status update: {status} - {reason or 'No reason'} (no API call)")
        
        updates = {
            'Status': status,
            'LastUpdated': datetime.now().isoformat()
        }
        
        if reason:
            updates['StatusReason'] = reason
        
        return await self.update_record(record_id, updates)
    
    async def get_record_by_id(self, record_id: str) -> Optional[Dict[str, Any]]:
        """Get test record by ID"""
        print(f"🔍 Getting test record {record_id} (no API call)")
        
        for record in self.test_records:
            if record['record_id'] == record_id:
                return record
        
        return None
    
    async def mark_video_generated(self, record_id: str, video_url: str, project_id: str = None) -> bool:
        """Mark video as generated with test data"""
        print(f"🎥 Test video generation marked: {video_url[:50]}... (no API call)")
        
        updates = {
            'VideoURL': video_url,
            'VideoStatus': 'Generated',
            'VideoGeneratedAt': datetime.now().isoformat()
        }
        
        if project_id:
            updates['JSON2VideoProjectID'] = project_id
        
        return await self.update_record(record_id, updates)
    
    async def close(self):
        """Close test server (no cleanup needed)"""
        print("🧪 Test Airtable Server closed")
        pass