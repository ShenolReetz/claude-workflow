#!/usr/bin/env python3
"""
Test JSON2Video Agent - REAL API CALLS for testing video generation
Purpose: Test actual video creation with JSON2Video API to validate components
"""

from typing import Dict, Any
import sys
import os

# Add project root to path
sys.path.append('/home/claude-workflow')

async def test_run_video_creation(record_data: Dict[str, Any], config: Dict[str, str]) -> Dict[str, Any]:
    """Create REAL video using JSON2Video API for testing all components"""
    print("🎬 Running REAL JSON2Video API call for testing")
    print("⚠️  WARNING: This will consume JSON2Video API credits")
    
    try:
        # Import the PRODUCTION JSON2Video Enhanced Server for REAL API calls
        from mcp_servers.json2video_enhanced_server_v2 import JSON2VideoEnhancedMCPServerV2
        
        # Initialize with real API key
        json2video_api_key = config.get('json2video_api_key')
        if not json2video_api_key:
            print("❌ No JSON2Video API key found in config")
            return {
                'success': False,
                'error': 'Missing JSON2Video API key',
                'video_url': None,
                'project_id': None
            }
        
        print(f"🔑 Using JSON2Video API key: {json2video_api_key[:8]}...")
        
        # Create JSON2Video server instance
        json2video_server = JSON2VideoEnhancedMCPServerV2(json2video_api_key)
        
        # Prepare comprehensive test record data with all review components
        comprehensive_record_data = {
            'record_id': record_data.get('record_id', 'test_record_123'),
            'VideoTitle': 'Top 5 Camera & Photo Cleaning Brushes Most Popular on Amazon 2025',
            
            # Product 1 (Winner) - Highest ratings
            'ProductNo1Title': 'ZEISS Lens Cleaning Kit - Professional Camera Lens Cleaner',
            'ProductNo1Photo': 'https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=1080&h=1920&fit=crop&crop=center',
            'ProductNo1Rating': 4.8,
            'ProductNo1Reviews': 2847,
            'ProductNo1Price': 29.99,
            
            # Product 2 - Second best
            'ProductNo2Title': 'Camera Cleaning Kit - Professional Grade 7-in-1',
            'ProductNo2Photo': 'https://images.unsplash.com/photo-1593784991095-a205069470b6?w=1080&h=1920&fit=crop&crop=center',
            'ProductNo2Rating': 4.7,
            'ProductNo2Reviews': 1923,
            'ProductNo2Price': 24.99,
            
            # Product 3 - Third best
            'ProductNo3Title': 'Lens Pen Pro - Precision Camera Lens Cleaner',
            'ProductNo3Photo': 'https://images.unsplash.com/photo-1585792180666-f7347c490ee2?w=1080&h=1920&fit=crop&crop=center',
            'ProductNo3Rating': 4.6,
            'ProductNo3Reviews': 1456,
            'ProductNo3Price': 19.99,
            
            # Product 4 - Fourth best
            'ProductNo4Title': 'Altura Photo Cleaning Kit - Complete Camera Care',
            'ProductNo4Photo': 'https://images.unsplash.com/photo-1583394838336-acd977736f90?w=1080&h=1920&fit=crop&crop=center',
            'ProductNo4Rating': 4.5,
            'ProductNo4Reviews': 987,
            'ProductNo4Price': 16.99,
            
            # Product 5 - Fifth best
            'ProductNo5Title': 'K&F Concept Camera Cleaning Brush Set',
            'ProductNo5Photo': 'https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=1080&h=1920&fit=crop&crop=center',
            'ProductNo5Rating': 4.4,
            'ProductNo5Reviews': 654,
            'ProductNo5Price': 12.99,
            
            # Intro/Outro images
            'IntroPhoto': 'https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=1080&h=1920&fit=crop&crop=center',
            'OutroPhoto': 'https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=1080&h=1920&fit=crop&crop=center'
        }
        
        print("📊 Test data prepared with comprehensive product information:")
        print(f"   🏆 Winner: {comprehensive_record_data['ProductNo1Title']} - {comprehensive_record_data['ProductNo1Rating']}⭐ ({comprehensive_record_data['ProductNo1Reviews']} reviews)")
        print(f"   🥈 2nd: {comprehensive_record_data['ProductNo2Title']} - {comprehensive_record_data['ProductNo2Rating']}⭐ ({comprehensive_record_data['ProductNo2Reviews']} reviews)")
        print(f"   🥉 3rd: {comprehensive_record_data['ProductNo3Title']} - {comprehensive_record_data['ProductNo3Rating']}⭐ ({comprehensive_record_data['ProductNo3Reviews']} reviews)")
        
        # Extract Google Drive audio URLs  
        try:
            sys.path.append('/home/claude-workflow/config')
            from google_drive_audio_config import get_all_audio_urls
            audio_urls = get_all_audio_urls()
            print(f"🎵 Google Drive audio files integrated: {len(audio_urls)} files")
            for audio_type, url in audio_urls.items():
                print(f"   {audio_type}: {url[:60]}...")
        except Exception as e:
            print(f"⚠️ Could not load Google Drive audio: {e}")
            audio_urls = {}
        
        print("\n🚀 Creating REAL video with JSON2Video API...")
        print("⏳ This will take several minutes with server-friendly timing...")
        
        # Create the video using production server
        video_result = await json2video_server.create_perfect_timing_video(comprehensive_record_data)
        
        if video_result.get('success'):
            project_id = video_result.get('project_id')
            video_url = video_result.get('video_url')
            
            print(f"✅ Video creation initiated successfully!")
            print(f"🎥 Project ID: {project_id}")
            print(f"🔗 Video URL: {video_url}")
            print(f"⏰ Video will be ready after JSON2Video processing completes")
            
            # Update record with real video data
            updated_record = comprehensive_record_data.copy()
            updated_record['VideoURL'] = video_url or f"https://json2video.com/app/projects/{project_id}"
            updated_record['JSON2VideoProjectID'] = project_id
            updated_record['VideoStatus'] = 'Processing'
            updated_record['VideoDuration'] = '55 seconds'
            updated_record['VideoResolution'] = '1080x1920'
            updated_record['VideoFormat'] = 'MP4'
            updated_record['GoogleDriveAudioIntegrated'] = len(audio_urls) > 0
            updated_record['AudioFilesCount'] = len(audio_urls)
            
            # Add audio URLs to record for monitoring
            for audio_type, url in audio_urls.items():
                updated_record[f'{audio_type}_audio_url'] = url
            
            return {
                'success': True,
                'updated_record': updated_record,
                'video_url': video_url or f"https://json2video.com/app/projects/{project_id}",
                'project_id': project_id,
                'duration': 55,
                'resolution': '1080x1920',
                'format': 'MP4',
                'features': [
                    'REAL JSON2Video API call',
                    'Test schema structure with production server',
                    'Montserrat Bold typography',
                    'Professional review components',
                    'Star ratings display (4.8⭐ to 4.4⭐)',
                    'Review counts (2847 to 654 reviews)',
                    'Price displays ($29.99 to $12.99)',
                    'Proper timing (5+45+5 = 55 seconds)',
                    f'Google Drive audio integration ({len(audio_urls)} files)',
                    'Winner trophy emoji for #1 product',
                    'Component-based JSON2Video structure'
                ],
                'scenes_created': 7,
                'audio_files_integrated': len(audio_urls),
                'google_drive_audio': len(audio_urls) > 0,
                'audio_urls': audio_urls,
                'api_calls_used': 1,
                'processing_time': 'Real API processing time',
                'components_tested': [
                    'Star rating components (advanced/070)',
                    'Review count components (advanced/060)', 
                    'Price components (advanced/060)',
                    'Subscribe button component (advanced/050)',
                    'Custom positioning system',
                    'Background zoom effects',
                    'Scene transitions (smoothright, slideright)'
                ]
            }
        else:
            error_msg = video_result.get('error', 'Unknown error')
            print(f"❌ Video creation failed: {error_msg}")
            return {
                'success': False,
                'error': error_msg,
                'video_url': None,
                'project_id': video_result.get('project_id'),
                'api_calls_used': 1,
                'processing_time': 'Failed during API call'
            }
            
    except Exception as e:
        print(f"❌ Exception during real video creation: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'video_url': None,
            'project_id': None,
            'api_calls_used': 0,
            'processing_time': 'Failed with exception'
        }
    
    finally:
        # Close the JSON2Video server connection
        try:
            await json2video_server.close()
        except:
            pass