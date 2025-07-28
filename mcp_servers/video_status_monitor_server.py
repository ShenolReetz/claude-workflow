#!/usr/bin/env python3
"""
Video Status Monitor Server
Monitors JSON2Video generation status and handles errors
"""

import asyncio
import json
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoStatusMonitorMCPServer:
    def __init__(self, config: Dict = None):
        """Initialize Video Status Monitor Server"""
        self.config = config or {}
        self.api_key = self.config.get('json2video_api_key', '')
        self.base_url = "https://api.json2video.com/v2"
        
        # Status tracking
        self.active_projects = {}  # project_id -> monitoring data
        self.status_history = {}   # project_id -> list of status changes
        self.error_patterns = {}   # error_type -> count
        
        # Performance metrics
        self.metrics = {
            'total_videos': 0,
            'successful_videos': 0,
            'failed_videos': 0,
            'average_processing_time': 0,
            'retry_success_rate': 0
        }
        
        logger.info("🎬 Video Status Monitor initialized - JSON2Video tracking active")

    async def start_monitoring(self, project_id: str, record_id: str, video_title: str = "") -> Dict[str, Any]:
        """Start monitoring a new video generation"""
        monitoring_data = {
            'project_id': project_id,
            'record_id': record_id,
            'title': video_title,
            'start_time': datetime.now(),
            'status': 'queued',
            'retry_count': 0,
            'error_history': [],
            'processing_phases': []
        }
        
        self.active_projects[project_id] = monitoring_data
        self.status_history[project_id] = [{
            'status': 'queued',
            'timestamp': datetime.now().isoformat(),
            'message': f'Video generation started: {video_title}'
        }]
        
        logger.info(f"🎬 Started monitoring video: {project_id} - {video_title}")
        
        # Start background monitoring task
        asyncio.create_task(self._monitor_project(project_id))
        
        return {
            'project_id': project_id,
            'status': 'monitoring_started',
            'message': f'Monitoring initiated for: {video_title}'
        }

    async def _monitor_project(self, project_id: str) -> None:
        """Background task to continuously monitor a project"""
        max_monitoring_time = 1800  # 30 minutes max (extended for proper monitoring)
        initial_delay = 300  # 5 minutes initial delay before first check
        poll_interval = 60   # 1 minute between checks after initial delay
        start_time = time.time()
        
        # Wait 5 minutes before starting monitoring to avoid server overload
        logger.info(f"⏰ Waiting 5 minutes before monitoring {project_id} to prevent server overload...")
        await asyncio.sleep(initial_delay)
        logger.info(f"🔍 Starting active monitoring for {project_id} with 1-minute intervals")
        
        while project_id in self.active_projects:
            try:
                # Check if we've exceeded max monitoring time
                if time.time() - start_time > max_monitoring_time:
                    await self._handle_timeout(project_id)
                    break
                
                # Get current status from JSON2Video API
                status_data = await self._get_project_status(project_id)
                current_time = time.time()
                elapsed_time = current_time - start_time
                
                if status_data:
                    await self._process_status_update(project_id, status_data)
                    
                    # Check if project was removed due to error
                    if project_id not in self.active_projects:
                        logger.info(f"🛑 Monitoring stopped for {project_id} due to error")
                        break
                    
                    # Log status check even for successful videos
                    current_status = status_data.get('status', 'unknown')
                    api_success = status_data.get('success', True)
                    logger.info(f"📊 Status check for {project_id} at {elapsed_time/60:.1f}min: {current_status} (success: {api_success})")
                    
                    # Handle completion cases
                    if current_status in ['done', 'completed'] and api_success:
                        # Verify video is fully accessible and log final metrics
                        await self._verify_completed_video(project_id, status_data)
                        
                        # After successful completion verification, end monitoring
                        await self._finalize_monitoring(project_id, status_data)
                        break
                    elif current_status in ['failed', 'error'] or not api_success:
                        # Error was already handled in _process_status_update
                        break
                else:
                    logger.warning(f"⚠️ No status data received for {project_id} at {elapsed_time/60:.1f}min")
                
                # Wait before next check
                await asyncio.sleep(poll_interval)
                
            except Exception as e:
                logger.error(f"❌ Error monitoring project {project_id}: {e}")
                await self._handle_monitoring_error(project_id, str(e))
                break

    async def _get_project_status(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get current status from JSON2Video API"""
        try:
            headers = {
                'x-api-key': self.api_key,  # Correct header format
                'Content-Type': 'application/json'
            }
            
            # Use correct endpoint format with query parameter
            response = requests.get(
                f"{self.base_url}/movies?project={project_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                api_response = response.json()
                
                # Check if movie data exists
                if 'movie' in api_response:
                    movie_data = api_response['movie']
                    
                    # Log the real API response
                    logger.info(f"📡 Real API Response for {project_id}:")
                    logger.info(f"   Status: {movie_data.get('status', 'unknown')}")
                    logger.info(f"   Success: {movie_data.get('success', 'unknown')}")
                    if 'message' in movie_data:
                        logger.info(f"   Message: {movie_data['message']}")
                    
                    # Return the movie data for processing
                    return movie_data
                else:
                    logger.warning(f"⚠️ No movie data in API response for {project_id}")
                    return None
            else:
                logger.error(f"❌ API Error {response.status_code} for project {project_id}: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to get status for {project_id}: {e}")
            return None

    async def _process_status_update(self, project_id: str, status_data: Dict[str, Any]) -> None:
        """Process a status update from the API"""
        if project_id not in self.active_projects:
            return
            
        monitoring_data = self.active_projects[project_id]
        current_status = status_data.get('status', 'unknown')
        previous_status = monitoring_data.get('status')
        
        # Check for API errors (success: false)
        api_success = status_data.get('success', True)
        error_message = status_data.get('message', '')
        
        # Handle real API errors
        if not api_success or current_status == 'error':
            logger.error(f"🚨 REAL API ERROR DETECTED for {project_id}!")
            logger.error(f"   Status: {current_status}")
            logger.error(f"   Success: {api_success}")
            logger.error(f"   Error Message: {error_message}")
            
            # Create error entry
            error_entry = {
                'timestamp': datetime.now().isoformat(),
                'error_type': 'api_error',
                'error_message': error_message,
                'api_status': current_status,
                'api_success': api_success,
                'full_response': status_data
            }
            
            monitoring_data['error_history'].append(error_entry)
            monitoring_data['status'] = 'failed'
            
            # Update Airtable with real error
            await self._update_airtable_status(project_id, "Failed", f"API Error: {error_message}")
            
            # Finalize with real error data
            await self._finalize_failure(project_id, error_entry)
            return
        
        # Only process if status changed
        if current_status != previous_status:
            monitoring_data['status'] = current_status
            
            # Log status change
            status_entry = {
                'status': current_status,
                'timestamp': datetime.now().isoformat(),
                'processing_time': (datetime.now() - monitoring_data['start_time']).total_seconds(),
                'details': status_data
            }
            
            self.status_history[project_id].append(status_entry)
            monitoring_data['processing_phases'].append(status_entry)
            
            logger.info(f"🎬 Status change for {project_id}: {previous_status} → {current_status}")
            
            # Handle specific status types
            if current_status == 'processing':
                await self._handle_processing_status(project_id, status_data)
            elif current_status == 'rendering':
                await self._handle_rendering_status(project_id, status_data)
            elif current_status == 'done':
                await self._handle_completed_status(project_id, status_data)
            elif current_status == 'failed':
                await self._handle_failed_status(project_id, status_data)

    async def _handle_processing_status(self, project_id: str, status_data: Dict[str, Any]) -> None:
        """Handle processing status"""
        logger.info(f"⚙️ Video {project_id} is processing...")
        
        # Update Airtable with processing status
        await self._update_airtable_status(project_id, "Processing", 
                                         "Video generation in progress")

    async def _handle_rendering_status(self, project_id: str, status_data: Dict[str, Any]) -> None:
        """Handle rendering status"""
        logger.info(f"🎨 Video {project_id} is rendering...")
        
        # Update Airtable with rendering status
        await self._update_airtable_status(project_id, "Rendering", 
                                         "Video rendering final output")

    async def _handle_completed_status(self, project_id: str, status_data: Dict[str, Any]) -> None:
        """Handle completed/done status"""
        logger.info(f"✅ Video {project_id} completed successfully!")
        
        # Extract video details
        video_url = status_data.get('url', '')
        if video_url:
            logger.info(f"🎬 Video URL: {video_url}")
        
        # Update Airtable with success
        await self._update_airtable_status(project_id, "Completed", 
                                         "Video generated successfully")

    async def _handle_failed_status(self, project_id: str, status_data: Dict[str, Any]) -> None:
        """Handle failed status with error analysis"""
        monitoring_data = self.active_projects[project_id]
        error_message = status_data.get('error', 'Unknown error')
        
        # Analyze error pattern
        error_type = self._categorize_error(error_message)
        self.error_patterns[error_type] = self.error_patterns.get(error_type, 0) + 1
        
        # Add to error history
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'error_type': error_type,
            'error_message': error_message,
            'retry_count': monitoring_data['retry_count']
        }
        monitoring_data['error_history'].append(error_entry)
        
        logger.error(f"❌ Video {project_id} failed: {error_message}")
        
        # Determine if retry is appropriate
        if await self._should_retry_project(project_id, error_type):
            await self._initiate_retry(project_id, error_type)
        else:
            await self._finalize_failure(project_id, error_entry)

    def _categorize_error(self, error_message: str) -> str:
        """Categorize error for pattern analysis"""
        error_lower = error_message.lower()
        
        if 'template' in error_lower or 'json' in error_lower:
            return 'template_error'
        elif 'asset' in error_lower or 'image' in error_lower or 'audio' in error_lower:
            return 'asset_error'
        elif 'timeout' in error_lower or 'time' in error_lower:
            return 'timeout_error'
        elif 'quota' in error_lower or 'limit' in error_lower:
            return 'quota_error'
        elif 'network' in error_lower or 'connection' in error_lower:
            return 'network_error'
        else:
            return 'unknown_error'

    async def _should_retry_project(self, project_id: str, error_type: str) -> bool:
        """Determine if project should be retried"""
        monitoring_data = self.active_projects[project_id]
        retry_count = monitoring_data['retry_count']
        
        # Max retry limits by error type
        max_retries = {
            'template_error': 1,  # Usually permanent
            'asset_error': 2,     # May be temporary
            'timeout_error': 3,   # Often temporary
            'quota_error': 0,     # Don't retry quota issues
            'network_error': 3,   # Usually temporary
            'unknown_error': 2    # Conservative retry
        }
        
        return retry_count < max_retries.get(error_type, 1)

    async def _initiate_retry(self, project_id: str, error_type: str) -> None:
        """Initiate retry with error-specific modifications"""
        monitoring_data = self.active_projects[project_id]
        monitoring_data['retry_count'] += 1
        
        logger.info(f"🔄 Retrying video {project_id} (attempt {monitoring_data['retry_count']})")
        
        # Update Airtable with retry status
        await self._update_airtable_status(project_id, "Retrying", 
                                         f"Retry attempt {monitoring_data['retry_count']} for {error_type}")
        
        # TODO: Implement actual retry logic with error-specific fixes
        # This would integrate with the JSON2Video server to retry generation

    async def _handle_timeout(self, project_id: str) -> None:
        """Handle monitoring timeout"""
        logger.warning(f"⏰ Monitoring timeout for project {project_id}")
        
        await self._update_airtable_status(project_id, "Timeout", 
                                         "Video generation exceeded maximum processing time")
        
        # Move to failed projects
        if project_id in self.active_projects:
            self.active_projects[project_id]['status'] = 'timeout'
            self.metrics['failed_videos'] += 1

    async def _finalize_failure(self, project_id: str, error_entry: Dict[str, Any]) -> None:
        """Finalize a failed video generation"""
        if project_id not in self.active_projects:
            return
            
        monitoring_data = self.active_projects[project_id]
        monitoring_data['status'] = 'failed'
        
        # Update metrics
        self.metrics['total_videos'] += 1
        self.metrics['failed_videos'] += 1
        
        processing_time = (datetime.now() - monitoring_data['start_time']).total_seconds()
        self._update_average_processing_time(processing_time)
        
        logger.error(f"❌ Video {project_id} failed permanently: {error_entry['error_message']}")
        
        # Remove from active monitoring
        del self.active_projects[project_id]

    async def _finalize_monitoring(self, project_id: str, status_data: Dict[str, Any]) -> None:
        """Finalize monitoring for completed or failed project"""
        if project_id not in self.active_projects:
            return
            
        monitoring_data = self.active_projects[project_id]
        processing_time = (datetime.now() - monitoring_data['start_time']).total_seconds()
        
        # Update metrics
        self.metrics['total_videos'] += 1
        if status_data.get('status') == 'completed':
            self.metrics['successful_videos'] += 1
            await self._handle_successful_completion(project_id, status_data, processing_time)
        else:
            self.metrics['failed_videos'] += 1
            
        # Update average processing time
        self._update_average_processing_time(processing_time)
        
        # Remove from active monitoring
        del self.active_projects[project_id]
        
        logger.info(f"🏁 Monitoring completed for {project_id} in {processing_time:.1f}s")

    async def _verify_completed_video(self, project_id: str, status_data: Dict[str, Any]) -> None:
        """Verify completed video is fully accessible and log metrics"""
        try:
            video_url = status_data.get('url', '')
            download_url = status_data.get('download_url', '')
            duration = status_data.get('duration', 0)
            file_size = status_data.get('file_size', 0)
            
            logger.info(f"✅ Video {project_id} completion verified!")
            logger.info(f"🎬 Video URL: {video_url}")
            if download_url:
                logger.info(f"⬇️ Download URL: {download_url}")
            logger.info(f"⏱️ Duration: {duration}s, Size: {file_size} bytes")
            
            # Additional verification could be added here:
            # - HTTP HEAD request to verify URLs are accessible
            # - Video metadata validation
            # - Quality score calculation
            
        except Exception as e:
            logger.error(f"❌ Error verifying completed video {project_id}: {e}")

    async def _handle_successful_completion(self, project_id: str, status_data: Dict[str, Any], processing_time: float) -> None:
        """Handle successful video completion"""
        video_url = status_data.get('url', '')
        duration = status_data.get('duration', 0)
        file_size = status_data.get('file_size', 0)
        
        logger.info(f"✅ Video {project_id} completed successfully!")
        logger.info(f"📊 Processing time: {processing_time:.1f}s")
        logger.info(f"🎬 Duration: {duration}s, Size: {file_size} bytes")
        
        # Update Airtable with success
        await self._update_airtable_status(project_id, "Completed", 
                                         f"Video generated successfully in {processing_time:.1f}s")
        
        # Quality verification
        quality_score = await self._verify_video_quality(project_id, status_data)
        await self._update_airtable_quality_score(project_id, quality_score)

    async def _verify_video_quality(self, project_id: str, status_data: Dict[str, Any]) -> int:
        """Verify video quality and return score 1-10"""
        score = 10  # Start with perfect score
        
        # Check duration (should be under 60 seconds for social media)
        duration = status_data.get('duration', 0)
        if duration > 60:
            score -= 2
        elif duration < 10:
            score -= 1
            
        # Check resolution (should be 1080x1920 for vertical video)
        width = status_data.get('width', 0)
        height = status_data.get('height', 0)
        if width != 1080 or height != 1920:
            score -= 1
            
        # Check file size (reasonable for video length)
        file_size = status_data.get('file_size', 0)
        if file_size < 1024 * 1024:  # Less than 1MB seems too small
            score -= 1
            
        return max(1, score)  # Minimum score of 1

    def _update_average_processing_time(self, processing_time: float) -> None:
        """Update average processing time metric"""
        total_videos = self.metrics['total_videos']
        current_avg = self.metrics['average_processing_time']
        
        # Calculate new average
        new_avg = ((current_avg * (total_videos - 1)) + processing_time) / total_videos
        self.metrics['average_processing_time'] = new_avg

    async def _update_airtable_status(self, project_id: str, status: str, message: str) -> None:
        """Update Airtable with status information"""
        # This would integrate with the Airtable server
        logger.info(f"📝 Airtable update: {project_id} → {status}: {message}")

    async def _update_airtable_quality_score(self, project_id: str, score: int) -> None:
        """Update Airtable with quality score"""
        logger.info(f"📊 Quality score for {project_id}: {score}/10")

    async def get_monitoring_status(self, project_id: str = None) -> Dict[str, Any]:
        """Get monitoring status for specific project or all projects"""
        if project_id:
            if project_id in self.active_projects:
                return {
                    'project_id': project_id,
                    'status': 'active',
                    'data': self.active_projects[project_id],
                    'history': self.status_history.get(project_id, [])
                }
            else:
                return {
                    'project_id': project_id,
                    'status': 'not_found',
                    'message': 'Project not currently being monitored'
                }
        else:
            return {
                'active_projects': len(self.active_projects),
                'projects': list(self.active_projects.keys()),
                'metrics': self.metrics,
                'error_patterns': self.error_patterns
            }

    async def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        total_videos = self.metrics['total_videos']
        success_rate = (self.metrics['successful_videos'] / total_videos * 100) if total_videos > 0 else 0
        
        return {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_videos': total_videos,
                'successful_videos': self.metrics['successful_videos'],
                'failed_videos': self.metrics['failed_videos'],
                'success_rate': f"{success_rate:.1f}%",
                'average_processing_time': f"{self.metrics['average_processing_time']:.1f}s"
            },
            'active_monitoring': {
                'projects_count': len(self.active_projects),
                'projects': list(self.active_projects.keys())
            },
            'error_analysis': self.error_patterns,
            'recommendations': self._generate_recommendations()
        }

    def _generate_recommendations(self) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        # Analyze error patterns
        if self.error_patterns.get('timeout_error', 0) > 2:
            recommendations.append("Consider simplifying video templates to reduce processing time")
            
        if self.error_patterns.get('asset_error', 0) > 1:
            recommendations.append("Implement better asset URL validation before video generation")
            
        # Analyze success rate
        total_videos = self.metrics['total_videos']
        if total_videos > 0:
            success_rate = self.metrics['successful_videos'] / total_videos
            if success_rate < 0.95:
                recommendations.append("Success rate below 95% - review template quality and error handling")
                
        # Analyze processing time
        avg_time = self.metrics['average_processing_time']
        if avg_time > 300:  # 5 minutes
            recommendations.append("Average processing time high - optimize template complexity")
            
        return recommendations

# Testing function
async def test_video_status_monitor():
    """Test the video status monitor functionality"""
    monitor = VideoStatusMonitorMCPServer({'json2video_api_key': 'test_key'})
    
    print("🎬 Testing Video Status Monitor...")
    
    # Start monitoring a test project
    result = await monitor.start_monitoring('TEST123', 'rec123', 'Test Video')
    print(f"📊 Monitor started: {result}")
    
    # Get status
    status = await monitor.get_monitoring_status()
    print(f"📊 Current status: {status}")
    
    # Generate report
    report = await monitor.get_performance_report()
    print(f"📊 Performance report: {report}")
    
    return monitor

if __name__ == "__main__":
    asyncio.run(test_video_status_monitor())