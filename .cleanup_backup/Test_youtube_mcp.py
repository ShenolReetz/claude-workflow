#!/usr/bin/env python3
"""
Test YouTube MCP Agent
Hardcoded responses for testing - no API usage
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional
from pathlib import Path
import sys
import uuid
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent.parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestYouTubeMCP:
    """Test YouTube MCP Agent with hardcoded responses"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.channel_id = config.get('youtube_channel_id', 'test-channel-123')
        
        print("🧪 TEST MODE: YouTube MCP using hardcoded responses")
        logger.info("🧪 Test YouTube MCP initialized")
    
    async def upload_video(self, 
                          video_url: str, 
                          title: str, 
                          description: str, 
                          tags: List[str],
                          category: str = "Howto & Style",
                          privacy: str = "public") -> Dict:
        """Simulate YouTube video upload with hardcoded success"""
        
        logger.info(f"📺 Test: Uploading video to YouTube: {title[:50]}...")
        print(f"🧪 TEST: Simulating YouTube upload")
        print(f"   Title: {title[:60]}...")
        print(f"   Tags: {', '.join(tags[:5])}...")
        print(f"   Category: {category}")
        print(f"   Privacy: {privacy}")
        
        try:
            # Simulate upload processing time
            await asyncio.sleep(1.0)
            
            # Generate test video ID
            test_video_id = f"test_video_{uuid.uuid4().hex[:8]}"
            test_watch_url = f"https://www.youtube.com/watch?v={test_video_id}"
            
            # Hardcoded successful upload response
            upload_result = {
                'success': True,
                'video_id': test_video_id,
                'watch_url': test_watch_url,
                'channel_url': f"https://www.youtube.com/channel/{self.channel_id}",
                'embed_url': f"https://www.youtube.com/embed/{test_video_id}",
                'upload_time': datetime.now().isoformat(),
                'status': 'uploaded',
                'privacy_status': privacy,
                'category': category,
                'metadata': {
                    'title': title,
                    'description': description[:200] + "..." if len(description) > 200 else description,
                    'tags': tags,
                    'duration': '60 seconds (estimated)',
                    'thumbnail_url': f"https://i.ytimg.com/vi/{test_video_id}/maxresdefault.jpg"
                },
                'analytics': {
                    'expected_views': '100-500 (first 24h)',
                    'target_audience': 'Product reviewers & shoppers',
                    'seo_score': 'High (optimized title & tags)'
                },
                'test_mode': True,
                'api_usage': 0  # No API tokens used in test mode
            }
            
            logger.info(f"✅ Test: YouTube upload successful - {test_watch_url}")
            print(f"🧪 TEST: YouTube upload SUCCESS")
            print(f"   Video ID: {test_video_id}")
            print(f"   Watch URL: {test_watch_url}")
            
            return upload_result
            
        except Exception as e:
            logger.error(f"❌ Test YouTube upload error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'test_mode': True
            }
    
    async def update_video_metadata(self, video_id: str, updates: Dict) -> Dict:
        """Simulate updating video metadata"""
        
        logger.info(f"📝 Test: Updating video metadata for {video_id}")
        print(f"🧪 TEST: Simulating metadata update for {video_id}")
        
        try:
            await asyncio.sleep(0.5)
            
            logger.info(f"✅ Test: Video metadata updated successfully")
            print(f"🧪 TEST: Metadata update SUCCESS")
            
            return {
                'success': True,
                'video_id': video_id,
                'updated_fields': list(updates.keys()),
                'test_mode': True,
                'api_usage': 0
            }
            
        except Exception as e:
            logger.error(f"❌ Test metadata update error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'test_mode': True
            }
    
    async def get_video_analytics(self, video_id: str) -> Dict:
        """Get hardcoded video analytics for testing"""
        
        logger.info(f"📊 Test: Getting analytics for video {video_id}")
        print(f"🧪 TEST: Simulating analytics retrieval for {video_id}")
        
        try:
            await asyncio.sleep(0.3)
            
            # Hardcoded analytics data
            analytics_data = {
                'success': True,
                'video_id': video_id,
                'analytics': {
                    'views': 247,
                    'likes': 18,
                    'dislikes': 1,
                    'comments': 12,
                    'shares': 8,
                    'watch_time_minutes': 156,
                    'avg_view_duration': '42 seconds',
                    'click_through_rate': '8.2%',
                    'subscriber_gain': 5,
                    'revenue_estimate': '$2.34',
                    'top_traffic_sources': ['YouTube Search', 'Suggested Videos', 'Browse Features'],
                    'audience_retention': '68%',
                    'demographics': {
                        'age_groups': {'18-24': 25, '25-34': 35, '35-44': 20, '45-54': 15, '55+': 5},
                        'gender': {'male': 65, 'female': 35},
                        'top_countries': ['United States', 'Canada', 'United Kingdom', 'Australia']
                    }
                },
                'performance_score': 'Good',
                'recommendations': [
                    'Consider adding end screens to promote other videos',
                    'Thumbnail could be more eye-catching',
                    'Good keyword optimization'
                ],
                'test_mode': True,
                'api_usage': 0
            }
            
            logger.info(f"✅ Test: Analytics retrieved - {analytics_data['analytics']['views']} views")
            print(f"🧪 TEST: Analytics SUCCESS - {analytics_data['analytics']['views']} views")
            
            return analytics_data
            
        except Exception as e:
            logger.error(f"❌ Test analytics error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'test_mode': True
            }
    
    async def create_playlist(self, playlist_title: str, video_ids: List[str]) -> Dict:
        """Create hardcoded playlist for testing"""
        
        logger.info(f"📋 Test: Creating playlist: {playlist_title}")
        print(f"🧪 TEST: Creating playlist with {len(video_ids)} videos")
        
        try:
            await asyncio.sleep(0.8)
            
            test_playlist_id = f"test_playlist_{uuid.uuid4().hex[:8]}"
            
            playlist_result = {
                'success': True,
                'playlist_id': test_playlist_id,
                'playlist_url': f"https://www.youtube.com/playlist?list={test_playlist_id}",
                'title': playlist_title,
                'video_count': len(video_ids),
                'videos_added': video_ids,
                'privacy': 'public',
                'created_at': datetime.now().isoformat(),
                'test_mode': True,
                'api_usage': 0
            }
            
            logger.info(f"✅ Test: Playlist created - {test_playlist_id}")
            print(f"🧪 TEST: Playlist creation SUCCESS")
            
            return playlist_result
            
        except Exception as e:
            logger.error(f"❌ Test playlist creation error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'test_mode': True
            }
    
    async def schedule_video(self, video_id: str, publish_time: str) -> Dict:
        """Schedule video for later publishing"""
        
        logger.info(f"⏰ Test: Scheduling video {video_id} for {publish_time}")
        print(f"🧪 TEST: Scheduling video for {publish_time}")
        
        try:
            await asyncio.sleep(0.4)
            
            schedule_result = {
                'success': True,
                'video_id': video_id,
                'scheduled_time': publish_time,
                'status': 'scheduled',
                'message': f'Video scheduled for {publish_time}',
                'test_mode': True,
                'api_usage': 0
            }
            
            logger.info(f"✅ Test: Video scheduled successfully")
            print(f"🧪 TEST: Video scheduling SUCCESS")
            
            return schedule_result
            
        except Exception as e:
            logger.error(f"❌ Test scheduling error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'test_mode': True
            }
    
    async def get_channel_stats(self) -> Dict:
        """Get hardcoded channel statistics"""
        
        logger.info(f"📈 Test: Getting channel statistics")
        print(f"🧪 TEST: Retrieving channel stats")
        
        try:
            await asyncio.sleep(0.6)
            
            channel_stats = {
                'success': True,
                'channel_id': self.channel_id,
                'channel_name': 'Test Product Reviews Channel',
                'statistics': {
                    'subscriber_count': 12567,
                    'video_count': 89,
                    'total_views': 456789,
                    'total_watch_time_hours': 12345,
                    'avg_views_per_video': 5132,
                    'engagement_rate': '6.8%',
                    'upload_frequency': '3 videos per week',
                    'top_performing_category': 'Product Reviews'
                },
                'recent_performance': {
                    'last_30_days_views': 45678,
                    'last_30_days_subscribers': 234,
                    'trending_videos': 3,
                    'top_keywords': ['amazon', 'product review', 'best', 'top 5', '2025']
                },
                'test_mode': True,
                'api_usage': 0
            }
            
            logger.info(f"✅ Test: Channel stats retrieved - {channel_stats['statistics']['subscriber_count']} subscribers")
            print(f"🧪 TEST: Channel stats SUCCESS - {channel_stats['statistics']['subscriber_count']} subscribers")
            
            return channel_stats
            
        except Exception as e:
            logger.error(f"❌ Test channel stats error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'test_mode': True
            }

# Test function
if __name__ == "__main__":
    async def test_youtube_mcp():
        config = {
            'youtube_channel_id': 'test-channel-123',
            'youtube_api_key': 'test-api-key'
        }
        
        youtube = TestYouTubeMCP(config)
        
        print("🧪 Testing YouTube MCP Agent")
        print("=" * 50)
        
        # Test video upload
        upload_result = await youtube.upload_video(
            video_url='https://test-video-url.com/video.mp4',
            title='Top 5 Gaming Headsets with THOUSANDS of Reviews',
            description='Discover the best gaming headsets on Amazon with real reviews and ratings!',
            tags=['gaming', 'headsets', 'amazon', 'product review', '2025'],
            category='Howto & Style',
            privacy='public'
        )
        
        print(f"\n📺 Upload Result: {'✅ SUCCESS' if upload_result['success'] else '❌ FAILED'}")
        
        if upload_result['success']:
            # Test analytics
            analytics = await youtube.get_video_analytics(upload_result['video_id'])
            print(f"📊 Analytics: {'✅ SUCCESS' if analytics['success'] else '❌ FAILED'}")
            
            # Test channel stats
            stats = await youtube.get_channel_stats()
            print(f"📈 Channel Stats: {'✅ SUCCESS' if stats['success'] else '❌ FAILED'}")
        
        print(f"\n🧪 Total API Usage: 0 tokens")
        
    asyncio.run(test_youtube_mcp())