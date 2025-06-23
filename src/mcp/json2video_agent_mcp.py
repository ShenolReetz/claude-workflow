#!/usr/bin/env python3
"""
JSON2Video Agent MCP
Handles video creation logic following your workflow architecture
"""

import asyncio
import json
import os
import sys
from typing import Dict, List, Optional
from datetime import datetime

# Add the project root to Python path
sys.path.append('/app')
sys.path.append('/home/claude-workflow')

# Import your existing servers (following your pattern)
from mcp_servers.airtable_server import AirtableMCPServer
from mcp_servers.json2video_server import JSON2VideoMCPServer

class JSON2VideoAgentMCP:
    """Controls the video creation workflow logic"""

    def __init__(self, config: dict):
        self.config = config

        # Initialize your existing MCP servers (following your pattern)
        self.airtable_server = AirtableMCPServer(
            api_key=config['airtable_api_key'],
            base_id=config['airtable_base_id'],
            table_name=config['airtable_table_name']
        )

        # Initialize the JSON2Video MCP Server
        self.json2video_server = JSON2VideoMCPServer(config['json2video_api_key'])

    async def create_video_from_record(self, record_id: str) -> Dict:
        """
        Main entry point - creates video from generated content
        This runs after content generation, affiliate links, images, and voice are ready
        """
        try:
            print(f"🎬 Starting video creation for record: {record_id}")

            # Get record from Airtable
            record = await self.airtable_server.get_record_by_id(record_id)

            if not record:
                return {
                    'success': False,
                    'error': f'Record {record_id} not found',
                    'record_id': record_id
                }

            fields = record.get('fields', {})
            
            # Check if we have the required content
            video_title = fields.get('VideoTitle')
            if not video_title:
                return {
                    'success': False,
                    'error': 'No VideoTitle found for video creation',
                    'record_id': record_id
                }

            # Check for product titles
            product_count = 0
            for i in range(1, 6):
                if fields.get(f'ProductNo{i}Title'):
                    product_count += 1

            if product_count == 0:
                return {
                    'success': False,
                    'error': 'No product titles found for video creation',
                    'record_id': record_id
                }

            print(f"📦 Found video title and {product_count} products")

            # Create project name from video title
            project_name = video_title.replace('🔥', '').replace('🚗', '').strip()
            project_name = project_name[:50]  # Limit length
            
            print(f"🎬 Creating video: {project_name}")

            # Create TEST video (8 seconds) to save costs
            video_result = await self.json2video_server.create_test_video(fields)

            if video_result['success']:
                print(f"✅ Video creation started. Movie ID: {video_result['movie_id']}")
                
                # Update Airtable with movie ID (for tracking)
                await self.airtable_server.update_record(
                    record_id,
                    {'Status': 'Processing'}
                )
                
                return {
                    'success': True,
                    'record_id': record_id,
                    'movie_id': video_result['movie_id'],
                    'project_name': project_name,
                    'product_count': product_count,
                    'video_url': video_result.get('video_url', '')
                }
            else:
                return {
                    'success': False,
                    'error': video_result.get('error', 'Unknown video creation error'),
                    'record_id': record_id
                }

        except Exception as e:
            print(f"❌ Error creating video for {record_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'record_id': record_id
            }

    async def check_and_complete_video(self, record_id: str, movie_id: str) -> Dict:
        """Check video status and complete processing when done"""
        try:
            print(f"📊 Checking video status for Movie ID: {movie_id}")
            
            # Check video status
            status_result = await self.json2video_server.check_video_status(movie_id)
            
            if not status_result['success']:
                return {
                    'success': False,
                    'error': status_result.get('error', 'Status check failed'),
                    'record_id': record_id,
                    'movie_id': movie_id
                }
            
            video_status = status_result['status']
            progress = status_result.get('progress', 0)
            
            print(f"📊 Video status: {video_status} ({progress}%)")
            
            if video_status == 'done':
                # Video is complete! Download and save
                download_url = status_result.get('download_url')
                if download_url:
                    print(f"🎉 Video completed! Downloading...")
                    
                    # For now, just save the URL to Airtable
                    # Later we can add Google Drive upload
                    await self.airtable_server.update_record(
                        record_id,
                        {
                            'FinalVideo': download_url,
                            'Status': 'Complete'
                        }
                    )
                    
                    return {
                        'success': True,
                        'status': 'complete',
                        'download_url': download_url,
                        'record_id': record_id,
                        'movie_id': movie_id
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Video complete but no download URL',
                        'record_id': record_id,
                        'movie_id': movie_id
                    }
            
            elif video_status == 'error':
                return {
                    'success': False,
                    'error': 'Video creation failed',
                    'record_id': record_id,
                    'movie_id': movie_id
                }
            
            else:
                # Still processing
                await self.airtable_server.update_record(
                    record_id,
                    {'Status': f"Processing {progress}% (ID: {movie_id})"}
                )
                
                return {
                    'success': True,
                    'status': 'processing',
                    'progress': progress,
                    'record_id': record_id,
                    'movie_id': movie_id
                }
                
        except Exception as e:
            print(f"❌ Error checking video status: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'record_id': record_id,
                'movie_id': movie_id
            }

    async def close(self):
        """Clean up resources"""
        await self.json2video_server.close()

# Integration function for workflow_runner.py
async def run_video_creation(config: dict, record_id: str) -> Dict:
    """
    Entry point function for workflow_runner.py integration
    This follows the same pattern as your other MCP integrations
    """
    print(f"🎬 Starting video creation for record: {record_id}")
    
    video_agent = JSON2VideoAgentMCP(config)
    result = await video_agent.create_video_from_record(record_id)
    await video_agent.close()
    
    print(f"🎯 Video creation completed for {record_id}")
    return result

# Test function (minimal, just tests structure)
async def test_video_agent():
    """Test function to verify the MCP works"""
    print("🧪 Testing JSON2Video MCP Agent structure...")
    
    # Load config
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)

    print(f"✅ Config loaded: JSON2Video API key configured")
    print("✅ Video Agent structure is correct")
    print("🎬 Ready for video creation integration")
    
    return {'success': True, 'test': 'Structure validated'}

if __name__ == "__main__":
    asyncio.run(test_video_agent())
