#!/usr/bin/env python3
"""
Video Status Checker for JSON2Video Project sSN2AyEr9QFU3n29
Checks if review elements (star ratings, rating values, review counts) are properly rendering
"""

import requests
import json
import sys
from datetime import datetime

def check_video_status():
    """Check the status of the specific JSON2Video project and analyze review elements"""
    
    # API configuration
    api_key = "s9gn6aT4ASaFaDbEpfbBsftbvf0IfEVZ9yD2FJKd"
    project_id = "sSN2AyEr9QFU3n29"
    base_url = "https://api.json2video.com/v2"
    
    print("🎬 JSON2Video Project Status Check")
    print("=" * 60)
    print(f"📋 Project ID: {project_id}")
    print(f"🕐 Check Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Set up headers
        headers = {
            'x-api-key': api_key,
            'Content-Type': 'application/json'
        }
        
        # Get project status
        print("📡 Fetching project status from JSON2Video API...")
        response = requests.get(
            f"{base_url}/movies?project={project_id}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            api_response = response.json()
            print("✅ API Response received successfully!")
            print()
            
            # Check if movie data exists
            if 'movie' in api_response:
                movie_data = api_response['movie']
                
                # Basic status information
                print("📊 PROJECT STATUS:")
                print(f"   Status: {movie_data.get('status', 'unknown')}")
                print(f"   Success: {movie_data.get('success', 'unknown')}")
                print(f"   Project ID: {movie_data.get('project', 'unknown')}")
                
                if 'message' in movie_data:
                    print(f"   Message: {movie_data['message']}")
                    
                if 'created' in movie_data:
                    print(f"   Created: {movie_data['created']}")
                    
                print()
                
                # Video details if available
                if movie_data.get('status') == 'done' or 'url' in movie_data:
                    print("🎬 VIDEO DETAILS:")
                    
                    if 'url' in movie_data:
                        print(f"   Video URL: {movie_data['url']}")
                    
                    if 'download_url' in movie_data:
                        print(f"   Download URL: {movie_data['download_url']}")
                        
                    if 'duration' in movie_data:
                        print(f"   Duration: {movie_data['duration']}s")
                        
                    if 'width' in movie_data and 'height' in movie_data:
                        print(f"   Resolution: {movie_data['width']}x{movie_data['height']}")
                        
                    if 'file_size' in movie_data:
                        file_size_mb = movie_data['file_size'] / (1024 * 1024)
                        print(f"   File Size: {file_size_mb:.1f}MB")
                        
                    print()
                
                # Template analysis for review elements
                print("⭐ REVIEW ELEMENTS ANALYSIS:")
                
                # Check if JSON template is available (as string)
                if 'json' in movie_data:
                    try:
                        template_json = json.loads(movie_data['json'])
                        analyze_template_json(template_json)
                    except json.JSONDecodeError:
                        print("   ❌ Could not parse template JSON")
                elif 'template' in movie_data:
                    template = movie_data['template']
                    analyze_review_elements(template)
                elif 'scenes' in movie_data:
                    scenes = movie_data['scenes']
                    analyze_scenes_for_reviews(scenes)
                else:
                    print("   ⚠️ Template/scenes data not available in API response")
                    print("   💡 This could mean:")
                    print("      - Video is still processing")
                    print("      - Template data is not included in status response")
                    print("      - Need to check the original template submission")
                
                print()
                
                # Full API response for debugging
                print("🔍 FULL API RESPONSE (for debugging):")
                print(json.dumps(api_response, indent=2))
                
            else:
                print("❌ No movie data found in API response")
                print("🔍 Raw API Response:")
                print(json.dumps(api_response, indent=2))
                
        elif response.status_code == 404:
            print("❌ Project not found!")
            print("💡 This could mean:")
            print("   - Project ID is incorrect")
            print("   - Project was deleted")
            print("   - Project belongs to different account")
            
        elif response.status_code == 401:
            print("❌ Authentication failed!")
            print("💡 Check API key configuration")
            
        else:
            print(f"❌ API Error {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timeout - JSON2Video API not responding")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - Unable to reach JSON2Video API")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def analyze_template_json(template_json):
    """Analyze the full template JSON for review elements"""
    print("   🔍 Analyzing template JSON for review elements...")
    
    review_elements_found = []
    
    # Look for scenes with review data
    if 'scenes' in template_json:
        for i, scene in enumerate(template_json['scenes']):
            scene_name = scene.get('comment', f'Scene {i+1}')
            scene_reviews = []
            
            # Check elements in each scene
            if 'elements' in scene:
                for element in scene['elements']:
                    element_id = element.get('id', '')
                    element_text = element.get('text', '')
                    element_comment = element.get('comment', '')
                    
                    # Look for star ratings
                    if '★' in element_text or '⭐' in element_text:
                        scene_reviews.append(f"⭐ Stars: {element_text} (ID: {element_id})")
                    
                    # Look for rating values  
                    if 'rating' in element_id.lower() or 'rating' in element_comment.lower():
                        scene_reviews.append(f"📊 Rating: {element_text} (ID: {element_id})")
                    
                    # Look for review counts
                    if 'reviews' in element_id.lower() or 'review' in element_text.lower():
                        scene_reviews.append(f"💬 Reviews: {element_text} (ID: {element_id})")
                    
                    # Look for prices
                    if 'price' in element_id.lower() or '$' in element_text:
                        scene_reviews.append(f"💰 Price: {element_text} (ID: {element_id})")
            
            if scene_reviews:
                print(f"   ✅ {scene_name}:")
                for review in scene_reviews:
                    print(f"      - {review}")
                review_elements_found.extend(scene_reviews)
    
    if not review_elements_found:
        print("   ⚠️ No review elements detected in template JSON")
    else:
        print(f"   📈 Total review elements found: {len(review_elements_found)}")
        
        # Summary of element types
        star_count = len([r for r in review_elements_found if '⭐ Stars' in r])
        rating_count = len([r for r in review_elements_found if '📊 Rating' in r])
        review_count = len([r for r in review_elements_found if '💬 Reviews' in r])
        price_count = len([r for r in review_elements_found if '💰 Price' in r])
        
        print(f"   📋 Summary: {star_count} star ratings, {rating_count} rating values, {review_count} review counts, {price_count} prices")

def analyze_review_elements(template):
    """Analyze template for review elements like stars, ratings, review counts"""
    print("   🔍 Analyzing template for review elements...")
    
    review_elements_found = []
    
    # Look for scenes with review data
    if 'scenes' in template:
        for i, scene in enumerate(template['scenes']):
            scene_reviews = []
            
            # Check elements in each scene
            if 'elements' in scene:
                for element in scene['elements']:
                    element_type = element.get('type', '')
                    element_text = element.get('text', '')
                    
                    # Look for star ratings
                    if '★' in element_text or 'star' in element_text.lower():
                        scene_reviews.append(f"Star rating: {element_text}")
                    
                    # Look for rating values
                    if any(rating in element_text for rating in ['4.', '5.', '3.', '2.', '1.']) and 'out of' in element_text.lower():
                        scene_reviews.append(f"Rating value: {element_text}")
                    
                    # Look for review counts
                    if 'review' in element_text.lower() and any(char.isdigit() for char in element_text):
                        scene_reviews.append(f"Review count: {element_text}")
            
            if scene_reviews:
                review_elements_found.extend([f"Scene {i+1}: {review}" for review in scene_reviews])
    
    if review_elements_found:
        print("   ✅ Review elements found:")
        for element in review_elements_found:
            print(f"      - {element}")
    else:
        print("   ⚠️ No review elements detected in template")
        print("   💡 Check if template includes:")
        print("      - Star ratings (★★★★☆)")
        print("      - Rating values (4.5 out of 5)")
        print("      - Review counts (1,234 reviews)")

def analyze_scenes_for_reviews(scenes):
    """Analyze scenes array for review elements"""
    print("   🔍 Analyzing scenes for review elements...")
    
    review_elements_found = []
    
    for i, scene in enumerate(scenes):
        scene_reviews = []
        
        # Check elements in each scene
        if 'elements' in scene:
            for element in scene['elements']:
                element_text = element.get('text', '')
                
                # Look for star ratings
                if '★' in element_text:
                    scene_reviews.append(f"Star rating: {element_text}")
                
                # Look for rating values
                if any(rating in element_text for rating in ['4.', '5.', '3.', '2.', '1.']):
                    scene_reviews.append(f"Rating value: {element_text}")
                
                # Look for review counts
                if 'review' in element_text.lower():
                    scene_reviews.append(f"Review count: {element_text}")
        
        if scene_reviews:
            review_elements_found.extend([f"Scene {i+1}: {review}" for review in scene_reviews])
    
    if review_elements_found:
        print("   ✅ Review elements found:")
        for element in review_elements_found:
            print(f"      - {element}")
    else:
        print("   ⚠️ No review elements detected in scenes")

if __name__ == "__main__":
    check_video_status()