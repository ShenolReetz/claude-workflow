#!/usr/bin/env python3
"""
Test Outro Image Generator
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

class TestOutroImageGenerator:
    """Test Outro Image Generator with hardcoded responses"""
    
    def __init__(self, config: Dict):
        self.config = config
        
        # Image generation settings (same as production)
        self.image_specs = {
            'width': 1080,
            'height': 1920,  # 9:16 aspect ratio for vertical video
            'format': 'PNG',
            'quality': 'high',
            'style': 'call_to_action'
        }
        
        print("🧪 TEST MODE: Outro Image Generator using hardcoded responses")
        logger.info("🧪 Test Outro Image Generator initialized")
    
    async def generate_outro_image(self, 
                                  call_to_action: str = "Subscribe for More Reviews!", 
                                  channel_name: str = "Product Reviews",
                                  brand_color: str = "#FFD700",
                                  include_subscribe_button: bool = True) -> Dict:
        """Generate hardcoded outro image for testing"""
        
        logger.info(f"🎬 Test: Generating outro image with CTA: {call_to_action[:30]}...")
        print(f"🧪 TEST: Generating outro image")
        print(f"   CTA: {call_to_action[:50]}...")
        print(f"   Channel: {channel_name}")
        print(f"   Brand Color: {brand_color}")
        print(f"   Subscribe Button: {include_subscribe_button}")
        
        try:
            # Simulate image generation processing time
            await asyncio.sleep(1.8)
            
            # Generate test image URLs and metadata
            test_image_id = f"outro_img_{uuid.uuid4().hex[:8]}"
            test_image_url = f"https://test-images.storage.com/outros/{test_image_id}.png"
            test_thumbnail_url = f"https://test-images.storage.com/outros/thumb_{test_image_id}.png"
            
            # Hardcoded successful generation response
            generation_result = {
                'success': True,
                'image_id': test_image_id,
                'image_url': test_image_url,
                'thumbnail_url': test_thumbnail_url,
                'local_path': f"/tmp/outro_images/{test_image_id}.png",
                'specifications': {
                    'width': self.image_specs['width'],
                    'height': self.image_specs['height'],
                    'aspect_ratio': '9:16',
                    'format': self.image_specs['format'],
                    'file_size': '2.1 MB',
                    'resolution': 'Full HD+'
                },
                'design_elements': {
                    'call_to_action': call_to_action,
                    'channel_name': channel_name,
                    'brand_color': brand_color,
                    'subscribe_button': include_subscribe_button,
                    'typography': 'Montserrat Bold',
                    'layout': 'centered_cta_focus',
                    'effects': ['gradient_background', 'button_glow', 'text_shadow'],
                    'interactive_elements': ['subscribe_button', 'bell_icon', 'thumbs_up_reminder']
                },
                'cta_optimization': {
                    'text_length': len(call_to_action),
                    'readability_score': 'Excellent',
                    'urgency_level': 'High',
                    'action_clarity': 'Very Clear',
                    'engagement_potential': 'High'
                },
                'brand_elements': {
                    'channel_branding': True,
                    'consistent_colors': True,
                    'logo_placement': 'bottom_center',
                    'brand_recognition': 'Optimized',
                    'visual_consistency': 'High'
                },
                'engagement_features': {
                    'subscribe_button_prominent': include_subscribe_button,
                    'notification_bell': True,
                    'like_reminder': True,
                    'comment_encouragement': True,
                    'share_suggestion': True
                },
                'metadata': {
                    'created_at': datetime.now().isoformat(),
                    'purpose': 'video_outro',
                    'target_platform': 'multi_platform',
                    'style_version': 'v2.1',
                    'color_palette': [brand_color, '#FFFFFF', '#000000', '#FF0000'],  # Red for subscribe
                    'accessibility': {
                        'high_contrast': True,
                        'readable_fonts': True,
                        'button_visibility': 'High'
                    }
                },
                'platform_optimization': {
                    'youtube_optimized': True,
                    'tiktok_ready': True,
                    'instagram_compatible': True,
                    'mobile_friendly': True,
                    'desktop_friendly': True
                },
                'test_mode': True,
                'api_usage': 0  # No API tokens used in test mode
            }
            
            logger.info(f"✅ Test: Outro image generated - {test_image_url}")
            print(f"🧪 TEST: Outro image generation SUCCESS")
            print(f"   Image ID: {test_image_id}")
            print(f"   Resolution: {self.image_specs['width']}x{self.image_specs['height']}")
            print(f"   File Size: {generation_result['specifications']['file_size']}")
            
            return generation_result
            
        except Exception as e:
            logger.error(f"❌ Test outro image generation error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'test_mode': True
            }
    
    async def generate_subscription_outro(self, 
                                        subscriber_count: str = "2.5K",
                                        recent_video_title: str = "",
                                        next_video_preview: str = "") -> Dict:
        """Generate subscription-focused outro with hardcoded success"""
        
        logger.info(f"📺 Test: Generating subscription outro for {subscriber_count} subscribers")
        print(f"🧪 TEST: Generating subscription-focused outro")
        print(f"   Subscribers: {subscriber_count}")
        print(f"   Recent Video: {recent_video_title[:40]}...")
        print(f"   Next Video: {next_video_preview[:40]}...")
        
        try:
            await asyncio.sleep(2.0)
            
            test_image_id = f"sub_outro_{uuid.uuid4().hex[:8]}"
            test_image_url = f"https://test-images.storage.com/subscription/{test_image_id}.png"
            
            subscription_result = {
                'success': True,
                'image_id': test_image_id,
                'image_url': test_image_url,
                'thumbnail_url': f"https://test-images.storage.com/subscription/thumb_{test_image_id}.png",
                'subscription_elements': {
                    'subscriber_count': subscriber_count,
                    'subscribe_button_style': 'red_gradient_glow',
                    'bell_icon': True,
                    'subscriber_milestone': self._calculate_milestone(subscriber_count),
                    'growth_message': f"Join our {subscriber_count} subscribers!",
                    'community_focus': True
                },
                'content_promotion': {
                    'recent_video_featured': bool(recent_video_title),
                    'next_video_teaser': bool(next_video_preview),
                    'playlist_suggestion': True,
                    'related_content': ['More Reviews', 'Latest Finds', 'Top Picks']
                },
                'engagement_tactics': {
                    'urgency_messaging': "Don't miss our weekly reviews!",
                    'community_building': f"Be part of our {subscriber_count} strong community",
                    'value_proposition': "Get the best product recommendations first",
                    'notification_reminder': "Turn on notifications for new uploads"
                },
                'design_optimization': {
                    'button_prominence': 'Maximum',
                    'text_hierarchy': 'Optimized',
                    'visual_flow': 'Subscribe-focused',
                    'color_psychology': 'Action-oriented'
                },
                'specifications': self.image_specs,
                'test_mode': True,
                'api_usage': 0
            }
            
            logger.info(f"✅ Test: Subscription outro generated successfully")
            print(f"🧪 TEST: Subscription outro generation SUCCESS")
            print(f"   Target: {subscriber_count} subscribers")
            
            return subscription_result
            
        except Exception as e:
            logger.error(f"❌ Test subscription outro error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'test_mode': True
            }
    
    def _calculate_milestone(self, subscriber_count: str) -> str:
        """Calculate next subscriber milestone"""
        try:
            # Extract number from subscriber count (e.g., "2.5K" -> 2500)
            if 'K' in subscriber_count:
                num = float(subscriber_count.replace('K', '')) * 1000
            elif 'M' in subscriber_count:
                num = float(subscriber_count.replace('M', '')) * 1000000
            else:
                num = float(subscriber_count)
            
            # Calculate next milestone
            if num < 1000:
                return "1K"
            elif num < 5000:
                return "5K"
            elif num < 10000:
                return "10K"
            elif num < 50000:
                return "50K"
            elif num < 100000:
                return "100K"
            else:
                return "1M"
        except:
            return "10K"  # Default milestone
    
    async def generate_end_screen_outro(self, 
                                      suggested_videos: List[Dict],
                                      playlist_info: Dict = {}) -> Dict:
        """Generate end screen outro with video suggestions"""
        
        logger.info(f"🎞️ Test: Generating end screen outro with {len(suggested_videos)} video suggestions")
        print(f"🧪 TEST: Generating end screen outro")
        print(f"   Suggested Videos: {len(suggested_videos)}")
        
        try:
            await asyncio.sleep(1.6)
            
            test_image_id = f"endscreen_{uuid.uuid4().hex[:8]}"
            
            endscreen_result = {
                'success': True,
                'image_id': test_image_id,
                'image_url': f"https://test-images.storage.com/endscreens/{test_image_id}.png",
                'suggested_content': {
                    'video_count': len(suggested_videos),
                    'videos': suggested_videos[:4],  # Limit to 4 for layout
                    'playlist_featured': bool(playlist_info),
                    'content_mix': 'Balanced (recent + popular + related)'
                },
                'layout_design': {
                    'grid_style': '2x2_video_grid',
                    'video_thumbnails': True,
                    'title_previews': True,
                    'view_counts': True,
                    'duration_badges': True
                },
                'interaction_elements': {
                    'clickable_areas': len(suggested_videos),
                    'subscribe_button': True,
                    'playlist_button': bool(playlist_info),
                    'channel_link': True,
                    'social_links': ['Instagram', 'TikTok', 'Twitter']
                },
                'engagement_optimization': {
                    'thumbnail_quality': 'High',
                    'title_truncation': 'Smart',
                    'visual_hierarchy': 'Optimized',
                    'click_encouragement': 'Strong'
                },
                'specifications': self.image_specs,
                'test_mode': True,
                'api_usage': 0
            }
            
            logger.info(f"✅ Test: End screen outro generated with {len(suggested_videos)} videos")
            print(f"🧪 TEST: End screen outro generation SUCCESS")
            
            return endscreen_result
            
        except Exception as e:
            logger.error(f"❌ Test end screen outro error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'test_mode': True
            }
    
    async def generate_social_outro(self, 
                                  social_handles: Dict,
                                  hashtags: List[str] = []) -> Dict:
        """Generate social media focused outro"""
        
        logger.info(f"📱 Test: Generating social outro with {len(social_handles)} platforms")
        print(f"🧪 TEST: Generating social media outro")
        print(f"   Platforms: {', '.join(social_handles.keys())}")
        print(f"   Hashtags: {len(hashtags)}")
        
        try:
            await asyncio.sleep(1.4)
            
            test_image_id = f"social_outro_{uuid.uuid4().hex[:8]}"
            
            social_result = {
                'success': True,
                'image_id': test_image_id,
                'image_url': f"https://test-images.storage.com/social/{test_image_id}.png",
                'social_elements': {
                    'platforms_included': list(social_handles.keys()),
                    'handles': social_handles,
                    'qr_codes': len(social_handles) <= 2,  # Only for 1-2 platforms
                    'hashtags_featured': hashtags[:5],  # Top 5 hashtags
                    'cross_platform_messaging': True
                },
                'engagement_strategy': {
                    'follow_encouragement': "Follow us on all platforms!",
                    'hashtag_usage': "Use our hashtags in your posts",
                    'community_building': "Join the conversation",
                    'user_generated_content': "Share your reviews with us"
                },
                'design_features': {
                    'platform_icons': True,
                    'handle_visibility': 'High',
                    'hashtag_formatting': 'Stylized',
                    'social_proof': 'Follower counts displayed',
                    'call_to_action': 'Multi-platform follow'
                },
                'specifications': self.image_specs,
                'test_mode': True,
                'api_usage': 0
            }
            
            logger.info(f"✅ Test: Social outro generated for {len(social_handles)} platforms")
            print(f"🧪 TEST: Social outro generation SUCCESS")
            
            return social_result
            
        except Exception as e:
            logger.error(f"❌ Test social outro error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'test_mode': True
            }
    
    async def get_outro_performance_analytics(self, image_id: str) -> Dict:
        """Get hardcoded performance analytics for outro image"""
        
        logger.info(f"📈 Test: Getting outro performance analytics for {image_id}")
        print(f"🧪 TEST: Retrieving outro performance analytics")
        
        try:
            await asyncio.sleep(0.7)
            
            analytics_data = {
                'success': True,
                'image_id': image_id,
                'performance_metrics': {
                    'estimated_ctr': '12.3%',  # Click-through rate
                    'subscribe_conversion': '8.7%',
                    'engagement_score': 92,
                    'retention_rate': '78%',
                    'action_completion': '15.4%'
                },
                'design_effectiveness': {
                    'button_visibility': 95,
                    'cta_clarity': 89,
                    'visual_appeal': 91,
                    'brand_consistency': 88,
                    'mobile_optimization': 94
                },
                'user_interaction_prediction': {
                    'subscribe_likelihood': 'High',
                    'video_suggestion_clicks': 'Medium-High',
                    'social_follow_rate': 'Medium',
                    'overall_engagement': 'High'
                },
                'comparison_benchmarks': {
                    'industry_average_ctr': '8.2%',
                    'your_predicted_ctr': '12.3%',
                    'performance_vs_average': '+50%',
                    'ranking': 'Top 20% of outro designs'
                },
                'optimization_suggestions': [
                    "Consider A/B testing different CTA phrases",
                    "Experiment with button colors for higher contrast",
                    "Add subscriber count to create social proof",
                    "Include limited-time offer messaging for urgency"
                ],
                'predicted_outcomes': {
                    'weekly_new_subscribers': '45-67',
                    'increased_video_views': '23%',
                    'channel_growth_impact': 'Positive',
                    'audience_retention': 'Improved'
                },
                'test_mode': True,
                'api_usage': 0
            }
            
            logger.info(f"✅ Test: Outro analytics retrieved - CTR: {analytics_data['performance_metrics']['estimated_ctr']}")
            print(f"🧪 TEST: Analytics SUCCESS - Predicted CTR: {analytics_data['performance_metrics']['estimated_ctr']}")
            
            return analytics_data
            
        except Exception as e:
            logger.error(f"❌ Test outro analytics error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'test_mode': True
            }

async def test_generate_outro_image_for_workflow(record_data: Dict, config: Dict) -> Dict:
    """Test function expected by Test_workflow_runner.py"""
    print("🧪 TEST: test_generate_outro_image_for_workflow called")
    
    # Initialize test generator
    config = {
        'openai_api_key': 'test-api-key',
        'image_storage_bucket': 'test-bucket'
    }
    generator = TestOutroImageGenerator(config)
    
    # Extract title from record data
    title = record_data.get('VideoTitle', 'Top 5 Gaming Headsets')
    
    # Simulate outro image generation
    await asyncio.sleep(1.8)
    
    # Return hardcoded success response with updated_record
    updated_record = record_data.copy()
    updated_record['outro_image_generated'] = True
    updated_record['outro_image_url'] = 'https://test-images.storage.com/outros/outro_img_12345.png'
    updated_record['outro_image_id'] = 'outro_img_12345'
    
    return {
        'success': True,
        'updated_record': updated_record,
        'image_id': 'outro_img_12345',
        'image_url': 'https://test-images.storage.com/outros/outro_img_12345.png',
        'engagement_score': 92,
        'cta': 'Subscribe for More Reviews!',
        'test_mode': True,
        'api_usage': 0
    }

# Test function
if __name__ == "__main__":
    async def test_outro_image_generator():
        config = {
            'openai_api_key': 'test-api-key',
            'image_storage_bucket': 'test-bucket'
        }
        
        generator = TestOutroImageGenerator(config)
        
        print("🧪 Testing Outro Image Generator")
        print("=" * 50)
        
        # Test basic outro generation
        outro_result = await generator.generate_outro_image(
            call_to_action='Subscribe for More Amazing Product Reviews!',
            channel_name='Best Product Reviews',
            brand_color='#FFD700',
            include_subscribe_button=True
        )
        
        print(f"\n🎬 Basic Outro: {'✅ SUCCESS' if outro_result['success'] else '❌ FAILED'}")
        
        if outro_result['success']:
            # Test subscription outro
            sub_outro = await generator.generate_subscription_outro(
                subscriber_count='2.5K',
                recent_video_title='Top 5 Gaming Headsets Review',
                next_video_preview='Best Car Amplifiers Coming Soon'
            )
            print(f"📺 Subscription Outro: {'✅ SUCCESS' if sub_outro['success'] else '❌ FAILED'}")
            
            # Test social outro
            social_handles = {
                'instagram': '@productreviews',
                'tiktok': '@bestproducts',
                'twitter': '@reviews2025'
            }
            hashtags = ['#ProductReviews', '#Amazon', '#BestFinds', '#TechReviews']
            
            social_outro = await generator.generate_social_outro(social_handles, hashtags)
            print(f"📱 Social Outro: {'✅ SUCCESS' if social_outro['success'] else '❌ FAILED'}")
            
            # Test performance analytics
            analytics = await generator.get_outro_performance_analytics(outro_result['image_id'])
            print(f"📈 Performance Analytics: {'✅ SUCCESS' if analytics['success'] else '❌ FAILED'}")
        
        print(f"\n🧪 Total API Usage: 0 tokens")
        
    asyncio.run(test_outro_image_generator())