#!/usr/bin/env python3
"""
JSON2Video Status Monitor Agent
Monitors video generation status with server-friendly timing (5min delay + 1min intervals)
Uses official JSON2Video API endpoint: GET https://api.json2video.com/v2/movies?project={projectId}
"""

import asyncio
import json
import sys
import httpx
from datetime import datetime, timedelta
from typing import Dict, Optional

# Add project root to path
sys.path.append('/home/claude-workflow')
from mcp_servers.airtable_server import AirtableMCPServer

class JSON2VideoStatusMonitor:
    """Monitors JSON2Video project status with server-friendly timing"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.json2video_api_key = config['json2video_api_key']
        self.headers = {
            'x-api-key': self.json2video_api_key,
            'Content-Type': 'application/json'
        }
        
        # Initialize Airtable for status updates
        self.airtable_server = AirtableMCPServer(
            api_key=config['airtable_api_key'],
            base_id=config['airtable_base_id'],
            table_name=config['airtable_table_name']
        )
        
        print("🎬 JSON2Video Status Monitor initialized")
        print("⏰ Timing: 5-minute initial delay + 1-minute check intervals")
    
    async def monitor_video_status(self, record_id: str, project_id: str, max_wait_minutes: int = 30) -> Dict:
        """
        Monitor video generation status with server-friendly timing
        
        Args:
            record_id: Airtable record ID
            project_id: JSON2Video project ID  
            max_wait_minutes: Maximum time to wait (default 30 min)
        """
        try:
            print(f"🎯 Starting status monitoring for Project ID: {project_id}")
            print(f"📋 Record ID: {record_id}")
            print(f"⏱️ Max wait time: {max_wait_minutes} minutes")
            
            # Initial 5-minute delay (server-friendly)
            print("⏳ Initial 5-minute delay to allow video processing...")
            await asyncio.sleep(300)  # 5 minutes = 300 seconds
            
            start_time = datetime.now()
            max_wait_time = start_time + timedelta(minutes=max_wait_minutes)
            check_count = 0
            
            while datetime.now() < max_wait_time:
                check_count += 1
                current_time = datetime.now().strftime("%H:%M:%S")
                elapsed = (datetime.now() - start_time).total_seconds() / 60
                
                print(f"🔍 Status check #{check_count} at {current_time} (elapsed: {elapsed:.1f}min)")
                
                # Check video status using official endpoint
                status_result = await self._check_project_status(project_id)
                
                if not status_result['success']:
                    print(f"❌ API error: {status_result.get('error', 'Unknown error')}")
                    await self._update_airtable_status(record_id, 'API Error', status_result.get('error'))
                    return status_result
                
                video_status = status_result['status']
                progress = status_result.get('progress', 0)
                
                print(f"📊 Status: {video_status} | Progress: {progress}%")
                
                if video_status == 'done':
                    # Video completed successfully
                    video_url = status_result.get('url')
                    duration = status_result.get('duration', 0)
                    rendering_time = status_result.get('rendering_time', 'unknown')
                    
                    print(f"🎉 Video generation completed!")
                    print(f"📺 Video URL: {video_url}")
                    print(f"⏱️ Duration: {duration}s | Rendering time: {rendering_time}")
                    
                    # Update Airtable with success
                    await self._update_airtable_success(record_id, video_url, {
                        'duration': duration,
                        'rendering_time': rendering_time,
                        'checks_performed': check_count,
                        'total_wait_time': f"{elapsed:.1f} minutes"
                    })
                    
                    return {
                        'success': True,
                        'status': 'completed',
                        'video_url': video_url,
                        'duration': duration,
                        'rendering_time': rendering_time,
                        'checks_performed': check_count,
                        'total_wait_time': elapsed
                    }
                
                elif video_status == 'error':
                    # Video generation failed
                    error_message = status_result.get('message', 'Unknown error during video generation')
                    
                    print(f"💥 Video generation FAILED!")
                    print(f"❌ Error: {error_message}")
                    
                    # Update Airtable with error
                    await self._update_airtable_error(record_id, error_message)
                    
                    return {
                        'success': False,
                        'status': 'error',
                        'error': error_message,
                        'checks_performed': check_count,
                        'total_wait_time': elapsed
                    }
                
                else:
                    # Still processing - update Airtable with progress
                    await self._update_airtable_progress(record_id, video_status, progress, check_count)
                    
                    # Wait 1 minute before next check (server-friendly)
                    print("⏳ Waiting 1 minute before next status check...")
                    await asyncio.sleep(60)  # 1 minute = 60 seconds
            
            # Timeout reached
            print(f"⏰ Timeout reached after {max_wait_minutes} minutes")
            await self._update_airtable_timeout(record_id, check_count)
            
            return {
                'success': False,
                'status': 'timeout',
                'error': f'Video generation timeout after {max_wait_minutes} minutes',
                'checks_performed': check_count,
                'total_wait_time': max_wait_minutes
            }
            
        except Exception as e:
            error_msg = f"Status monitoring error: {str(e)}"
            print(f"❌ {error_msg}")
            await self._update_airtable_status(record_id, 'Monitor Error', error_msg)
            
            return {
                'success': False,
                'status': 'monitor_error', 
                'error': error_msg
            }
    
    async def _check_project_status(self, project_id: str) -> Dict:
        """Check project status using official JSON2Video API endpoint"""
        try:
            url = f"https://api.json2video.com/v2/movies?project={project_id}"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=self.headers)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Parse response based on JSON2Video API format
                    if isinstance(data, list) and len(data) > 0:
                        movie_data = data[0]  # Get first movie data
                        
                        # Determine status from response
                        if movie_data.get('url'):
                            # Video is completed
                            return {
                                'success': True,
                                'status': 'done',
                                'url': movie_data.get('url'),
                                'duration': movie_data.get('duration', 0),
                                'rendering_time': movie_data.get('rendering_time', 'unknown'),
                                'size': movie_data.get('size', 0),
                                'created_at': movie_data.get('created_at'),
                                'ended_at': movie_data.get('ended_at')
                            }
                        elif movie_data.get('status') == 'error':
                            # Error occurred
                            return {
                                'success': True,
                                'status': 'error',
                                'message': movie_data.get('message', 'Unknown error')
                            }
                        else:
                            # Still processing
                            return {
                                'success': True,
                                'status': 'processing',
                                'progress': movie_data.get('progress', 0)
                            }
                    else:
                        return {
                            'success': False,
                            'error': 'No movie data found in response'
                        }
                else:
                    return {
                        'success': False,
                        'error': f'API request failed: {response.status_code} - {response.text}'
                    }
                    
        except Exception as e:
            return {
                'success': False,
                'error': f'Request error: {str(e)}'
            }
    
    async def _update_airtable_success(self, record_id: str, video_url: str, metadata: Dict):
        """Update Airtable with successful completion"""
        try:
            update_data = {
                'Status': 'Completed',
                'FinalVideo': video_url,
                'ValidationIssues': f"✅ Video completed in {metadata['total_wait_time']} after {metadata['checks_performed']} checks"
            }
            
            await self.airtable_server.update_record(record_id, update_data)
            print(f"💾 Updated Airtable with success status")
            
        except Exception as e:
            print(f"⚠️ Error updating Airtable success: {e}")
    
    async def _update_airtable_error(self, record_id: str, error_message: str):
        """Update Airtable with error status"""
        try:
            update_data = {
                'Status': 'Failed',
                'ValidationIssues': f"❌ Video generation failed: {error_message}"
            }
            
            await self.airtable_server.update_record(record_id, update_data)
            print(f"💾 Updated Airtable with error status")
            
        except Exception as e:
            print(f"⚠️ Error updating Airtable error: {e}")
    
    async def _update_airtable_progress(self, record_id: str, status: str, progress: int, check_count: int):
        """Update Airtable with progress status"""
        try:
            update_data = {
                'Status': f'Processing ({progress}%)',
                'ValidationIssues': f"🎬 Video generation in progress: {status} | Check #{check_count}"
            }
            
            await self.airtable_server.update_record(record_id, update_data)
            
        except Exception as e:
            print(f"⚠️ Error updating Airtable progress: {e}")
    
    async def _update_airtable_timeout(self, record_id: str, check_count: int):
        """Update Airtable with timeout status"""
        try:
            update_data = {
                'Status': 'Timeout',
                'ValidationIssues': f"⏰ Video generation timeout after {check_count} status checks"
            }
            
            await self.airtable_server.update_record(record_id, update_data)
            print(f"💾 Updated Airtable with timeout status")
            
        except Exception as e:
            print(f"⚠️ Error updating Airtable timeout: {e}")
    
    async def _update_airtable_status(self, record_id: str, status: str, message: str):
        """Update Airtable with general status"""
        try:
            update_data = {
                'Status': status,
                'ValidationIssues': message
            }
            
            await self.airtable_server.update_record(record_id, update_data)
            
        except Exception as e:
            print(f"⚠️ Error updating Airtable status: {e}")

# Integration function for workflow
async def monitor_json2video_status(config: Dict, record_id: str, project_id: str) -> Dict:
    """
    Monitor JSON2Video status for workflow integration
    
    Args:
        config: API configuration
        record_id: Airtable record ID
        project_id: JSON2Video project ID
    """
    monitor = JSON2VideoStatusMonitor(config)
    return await monitor.monitor_video_status(record_id, project_id)

# Test function
async def test_status_monitor():
    """Test the status monitoring with a sample project"""
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    # Test with sample project ID (replace with actual project ID for testing)
    test_project_id = "sample_project_id_123"
    test_record_id = "test_record_456"
    
    print("🧪 Testing JSON2Video Status Monitor...")
    
    result = await monitor_json2video_status(config, test_record_id, test_project_id)
    
    print(f"\n📊 Test Result:")
    print(f"Success: {result['success']}")
    print(f"Status: {result['status']}")
    if result.get('video_url'):
        print(f"Video URL: {result['video_url']}")
    if result.get('error'):
        print(f"Error: {result['error']}")

if __name__ == "__main__":
    asyncio.run(test_status_monitor())