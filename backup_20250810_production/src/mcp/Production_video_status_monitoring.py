#!/usr/bin/env python3
"""
Production Video Status Monitoring - Monitor JSON2Video Status
"""

import aiohttp
import asyncio
from typing import Dict

async def production_monitor_video_status(project_id: str, config: Dict) -> Dict:
    """Monitor JSON2Video project status"""
    try:
        api_key = config.get('json2video_api_key')
        
        # Check project status
        url = f"https://api.json2video.com/v2/movies/{project_id}"
        headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json"
        }
        
        max_checks = 10
        for i in range(max_checks):
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        status = data.get('status', 'unknown')
                        
                        if status in ['done', 'finished', 'completed']:
                            return {
                                'success': True,
                                'final_status': status,
                                'project_id': project_id,
                                'video_ready': True
                            }
                        elif status in ['error', 'failed']:
                            return {
                                'success': False,
                                'final_status': status,
                                'project_id': project_id,
                                'error': 'Video generation failed'
                            }
                        
                        # Still processing, wait and retry
                        await asyncio.sleep(30)  # Wait 30 seconds
            
        # Timeout after max checks
        return {
            'success': False,
            'error': 'Timeout waiting for video completion',
            'project_id': project_id
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'project_id': project_id
        }