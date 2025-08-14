#!/usr/bin/env python3
"""
Production JSON2Video Video Downloader
======================================
Polls JSON2Video API to check rendering status and downloads the completed video

Polling Strategy:
- Checks every 30 seconds to avoid overloading the server
- Maximum wait time: 5 minutes (300 seconds = 10 checks)
- Respects API rate limits and prevents spam/blocking
"""

import aiohttp
import asyncio
import json
from typing import Dict, Optional
import time

async def wait_for_video_and_download(project_id: str, config: Dict, max_wait: int = 600) -> Dict:
    """
    Wait for JSON2Video to finish rendering and return the video URL
    
    Args:
        project_id: The JSON2Video project ID
        config: Configuration with API key
        max_wait: Maximum seconds to wait (default 600 seconds = 10 minutes)
    
    Returns:
        Dict with success status and video URL
    """
    api_key = config.get('json2video_api_key')
    if not api_key:
        return {'success': False, 'error': 'Missing API key'}
    
    start_time = time.time()
    initial_wait = 300  # Wait 5 minutes before first check
    poll_interval = 30  # Then check every 30 seconds
    
    print(f"⏳ Waiting 5 minutes before checking video {project_id} status...")
    print(f"   (Videos typically take 3-7 minutes to render)")
    
    # Initial wait of 5 minutes to avoid unnecessary API calls
    await asyncio.sleep(initial_wait)
    
    print(f"🔍 Starting to check video status (every 30 seconds)...")
    
    async with aiohttp.ClientSession() as session:
        headers = {"x-api-key": api_key}
        
        while (time.time() - start_time) < max_wait:
            try:
                # Check project status using correct endpoint format
                url = f"https://api.json2video.com/v2/movies?project={project_id}"
                
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Get status from the response
                        status = data.get('status', 'unknown')
                        message = data.get('message', '')
                        
                        elapsed = int(time.time() - start_time)
                        print(f"   📊 Status: {status} | Elapsed: {elapsed}s | {message}")
                        
                        if status == 'done':
                            # Video is ready! Get URL from movie object
                            movie = data.get('movie', {})
                            video_url = movie.get('url', '')
                            
                            if video_url:
                                print(f"✅ Video ready: {video_url}")
                                render_time = time.time() - start_time
                                minutes = int(render_time // 60)
                                seconds = int(render_time % 60)
                                print(f"⏱️ Total render time: {minutes}m {seconds}s")
                                
                                return {
                                    'success': True,
                                    'video_url': video_url,
                                    'status': 'done',
                                    'render_time': render_time
                                }
                            else:
                                print(f"⚠️ Video done but URL not found in response")
                                # Fallback to CloudFront URL
                                video_url = f"https://d1oco4z2z1fhwp.cloudfront.net/projects/{project_id}/project.mp4"
                                return {
                                    'success': True,
                                    'video_url': video_url,
                                    'status': 'done',
                                    'render_time': time.time() - start_time
                                }
                        
                        elif status == 'error':
                            error_msg = data.get('message', 'Unknown error')
                            print(f"❌ Video rendering failed: {error_msg}")
                            return {
                                'success': False,
                                'error': f'Rendering failed: {error_msg}',
                                'status': 'error'
                            }
                        
                        elif status in ['pending', 'running']:
                            # Still processing, wait and retry
                            elapsed = int(time.time() - start_time)
                            remaining = max_wait - elapsed
                            if remaining > 0:
                                print(f"   ⏳ Still {status}... (next check in 30s)")
                            else:
                                print(f"   ⏱️ Timeout approaching...")
                        
                    else:
                        print(f"⚠️ API returned status {response.status}")
                
            except Exception as e:
                print(f"⚠️ Error checking status: {e}")
            
            # Wait before next poll
            await asyncio.sleep(poll_interval)
        
        # Timeout reached
        print(f"❌ Timeout: Video not ready after {max_wait} seconds")
        return {
            'success': False,
            'error': f'Timeout after {max_wait} seconds',
            'status': 'timeout'
        }

async def get_video_with_retry(record: Dict, config: Dict) -> Dict:
    """
    Enhanced video retrieval with status checking and retry logic
    """
    project_id = record.get('fields', {}).get('JSON2VideoProjectID')
    
    if not project_id:
        return {
            'success': False,
            'error': 'No project ID found in record'
        }
    
    # First, wait for video to be ready
    result = await wait_for_video_and_download(project_id, config)
    
    if result['success']:
        # Update record with final video URL
        record['fields']['FinalVideo'] = result['video_url']
        record['fields']['VideoRenderTime'] = result.get('render_time', 0)
        
        return {
            'success': True,
            'video_url': result['video_url'],
            'updated_record': record
        }
    else:
        return result