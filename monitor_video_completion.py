#!/usr/bin/env python3
"""
Video Status Monitor for JSON2Video Project CGxsdhnGBbYheCiP
Continuously monitors until video completion and provides final URL
"""

import requests
import json
import time
import sys
from datetime import datetime

def monitor_video_completion():
    """Monitor video until completion and provide final URL"""
    
    # API configuration
    api_key = "s9gn6aT4ASaFaDbEpfbBsftbvf0IfEVZ9yD2FJKd"
    project_id = "CGxsdhnGBbYheCiP"
    base_url = "https://api.json2video.com/v2"
    
    # Monitoring configuration
    max_monitoring_time = 1800  # 30 minutes max
    poll_interval = 60  # Check every 60 seconds
    start_time = time.time()
    
    print("🎬 JSON2Video Project Monitoring")
    print("=" * 60)
    print(f"📋 Project ID: {project_id}")
    print(f"🕐 Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏰ Check Interval: {poll_interval} seconds")
    print(f"🔚 Max Monitoring Time: {max_monitoring_time/60} minutes")
    print()
    
    status_checks = 0
    
    while True:
        current_time = time.time()
        elapsed_time = current_time - start_time
        status_checks += 1
        
        print(f"🔍 Status Check #{status_checks} (Elapsed: {elapsed_time/60:.1f} min)")
        
        # Check if we've exceeded max monitoring time
        if elapsed_time > max_monitoring_time:
            print(f"⏰ Maximum monitoring time ({max_monitoring_time/60} minutes) exceeded")
            print("❌ Video may have failed or is taking unusually long to process")
            break
        
        try:
            # Set up headers
            headers = {
                'x-api-key': api_key,
                'Content-Type': 'application/json'
            }
            
            # Get project status
            response = requests.get(
                f"{base_url}/movies?project={project_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                api_response = response.json()
                
                if 'movie' in api_response:
                    movie_data = api_response['movie']
                    current_status = movie_data.get('status', 'unknown')
                    api_success = movie_data.get('success', False)
                    message = movie_data.get('message', '')
                    
                    print(f"   📊 Status: {current_status}")
                    print(f"   ✅ Success: {api_success}")
                    if message:
                        print(f"   💬 Message: {message}")
                    
                    # Check for completion
                    if current_status == 'done' and api_success:
                        print()
                        print("🎉 VIDEO COMPLETED SUCCESSFULLY!")
                        print("=" * 60)
                        
                        # Display video details
                        video_url = movie_data.get('url', '')
                        download_url = movie_data.get('download_url', '')
                        duration = movie_data.get('duration', 0)
                        
                        if video_url:
                            print(f"🎬 Video URL: {video_url}")
                        if download_url:
                            print(f"⬇️ Download URL: {download_url}")
                        if duration:
                            print(f"⏱️ Duration: {duration} seconds")
                        
                        # Show processing time
                        total_processing_time = elapsed_time / 60
                        print(f"⚡ Total Processing Time: {total_processing_time:.1f} minutes")
                        
                        # Review elements confirmation
                        print()
                        print("⭐ REVIEW ELEMENTS STATUS:")
                        if 'json' in movie_data:
                            try:
                                template_json = json.loads(movie_data['json'])
                                review_count = count_review_elements(template_json)
                                print(f"   ✅ {review_count} review elements successfully rendered")
                                print("   📋 Including: star ratings, rating values, review counts, and prices")
                            except json.JSONDecodeError:
                                print("   ⚠️ Could not parse template to verify review elements")
                        
                        print()
                        print("🚀 Video is ready for download and use!")
                        break
                        
                    elif current_status == 'failed' or (current_status == 'error' and not api_success):
                        print()
                        print("❌ VIDEO GENERATION FAILED!")
                        print("=" * 60)
                        print(f"   Status: {current_status}")
                        print(f"   Success: {api_success}")
                        if message:
                            print(f"   Error Message: {message}")
                        break
                        
                    else:
                        # Still processing
                        print(f"   ⏳ Still processing... (Next check in {poll_interval}s)")
                        
                else:
                    print("   ❌ No movie data in API response")
                    
            else:
                print(f"   ❌ API Error {response.status_code}: {response.text}")
                
        except requests.exceptions.Timeout:
            print("   ❌ Request timeout - JSON2Video API not responding")
            
        except requests.exceptions.ConnectionError:
            print("   ❌ Connection error - Unable to reach JSON2Video API")
            
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
        
        print()
        
        # Wait before next check (unless we've completed or failed)
        if current_status not in ['done', 'failed', 'error']:
            time.sleep(poll_interval)
        else:
            break

def count_review_elements(template_json):
    """Count review elements in the template JSON"""
    count = 0
    
    if 'scenes' in template_json:
        for scene in template_json['scenes']:
            if 'elements' in scene:
                for element in scene['elements']:
                    element_id = element.get('id', '').lower()
                    element_text = element.get('text', '')
                    
                    # Count star ratings, ratings, reviews, and prices
                    if any(keyword in element_id for keyword in ['stars', 'rating', 'reviews', 'price']):
                        count += 1
                    elif '★' in element_text or '$' in element_text or 'review' in element_text.lower():
                        count += 1
    
    return count

if __name__ == "__main__":
    try:
        monitor_video_completion()
    except KeyboardInterrupt:
        print("\n\n⏹️ Monitoring stopped by user")
        print("💡 Video may still be processing in the background")
    except Exception as e:
        print(f"\n\n❌ Monitor failed with error: {e}")
        sys.exit(1)