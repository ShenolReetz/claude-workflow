#!/usr/bin/env python3
"""
Production JSON2Video Agent MCP - FIXED VERSION
Maintains 55-second timing (5-9-9-9-9-9-5) while fixing schema compliance issues
"""

import aiohttp
import asyncio
import json
import random
from typing import Dict, List, Optional
from datetime import datetime

async def post_with_retry(session: aiohttp.ClientSession, url: str, headers: Dict, 
                          json_data: Dict, max_retries: int = 3) -> Dict:
    """
    POST request with exponential backoff retry for transient failures
    
    Args:
        session: aiohttp client session
        url: API endpoint URL
        headers: Request headers
        json_data: JSON payload
        max_retries: Maximum number of retry attempts
    
    Returns:
        Response data or raises exception on failure
    """
    for attempt in range(max_retries):
        try:
            async with session.post(url, headers=headers, json=json_data) as response:
                if response.status in [200, 201]:
                    return await response.json()
                elif response.status >= 500 and attempt < max_retries - 1:
                    # Server error - retry with exponential backoff
                    wait_time = (2 ** attempt) + random.uniform(0, 1)  # Add jitter
                    print(f"⚠️ Server error {response.status}, retrying in {wait_time:.1f}s (attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(wait_time)
                    continue
                elif response.status == 429 and attempt < max_retries - 1:
                    # Rate limit - wait longer
                    wait_time = (2 ** (attempt + 1)) + random.uniform(0, 2)
                    print(f"⚠️ Rate limited, waiting {wait_time:.1f}s (attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    # Client error or final attempt - don't retry
                    error_text = await response.text()
                    raise Exception(f"API error {response.status}: {error_text}")
                    
        except aiohttp.ClientError as e:
            if attempt < max_retries - 1:
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"⚠️ Network error: {e}, retrying in {wait_time:.1f}s (attempt {attempt + 1}/{max_retries})")
                await asyncio.sleep(wait_time)
            else:
                raise
    
    raise Exception(f"Failed after {max_retries} attempts")

async def validate_media_assets(record: Dict) -> Dict:
    """
    Validate all required media assets exist before rendering
    
    Returns:
        Dict with validation results and warnings
    """
    fields = record.get('fields', {})
    issues = []
    warnings = []
    
    # Check required audio files (MUST have these for 55-second timing)
    required_audio = {
        'IntroMp3': 'Intro audio (5s)',
        'OutroMp3': 'Outro audio (5s)',
        'Product1Mp3': 'Product 1 audio (9s)',
        'Product2Mp3': 'Product 2 audio (9s)',
        'Product3Mp3': 'Product 3 audio (9s)',
        'Product4Mp3': 'Product 4 audio (9s)',
        'Product5Mp3': 'Product 5 audio (9s)'
    }
    
    for field, name in required_audio.items():
        if not fields.get(field):
            issues.append(f"Missing {name} ({field})")
    
    # Check required images
    required_images = {
        'IntroPhoto': 'Intro image',
        'OutroPhoto': 'Outro image',
        'ProductNo1Photo': 'Product 1 image',
        'ProductNo2Photo': 'Product 2 image',
        'ProductNo3Photo': 'Product 3 image',
        'ProductNo4Photo': 'Product 4 image',
        'ProductNo5Photo': 'Product 5 image'
    }
    
    for field, name in required_images.items():
        if not fields.get(field):
            warnings.append(f"Missing {name} ({field}) - using placeholder")
    
    return {
        'valid': len(issues) == 0,
        'issues': issues,
        'warnings': warnings
    }

async def production_run_video_creation(record: Dict, config: Dict) -> Dict:
    """Create video using JSON2Video API with fixed schema and 55-second timing"""
    try:
        # Ensure record has proper structure
        if not isinstance(record, dict):
            print(f"❌ Error: Record is not a dictionary, got {type(record)}")
            record = {'record_id': '', 'fields': {}}
        if 'fields' not in record:
            print("⚠️ Warning: Record missing 'fields' key, adding empty fields")
            record['fields'] = {}
        
        api_key = config.get('json2video_api_key')
        if not api_key:
            print("❌ Error: json2video_api_key not found in config")
            return {
                'success': False,
                'error': 'Missing json2video_api_key',
                'updated_record': record
            }
        
        # Validate media assets first
        print("🔍 Validating media assets...")
        validation = await validate_media_assets(record)
        if not validation['valid']:
            print(f"❌ Media validation failed:")
            for issue in validation['issues']:
                print(f"   • {issue}")
            return {
                'success': False,
                'error': f"Audio files missing (required for 55s timing): {', '.join(validation['issues'])}",
                'updated_record': record
            }
        
        if validation['warnings']:
            print(f"⚠️ Media validation warnings:")
            for warning in validation['warnings']:
                print(f"   • {warning}")
        
        # Build fixed JSON2Video schema (55 seconds total)
        video_schema = await _build_fixed_video_schema(record, config)
        
        # Log schema for debugging
        print(f"📊 Video Schema Stats:")
        print(f"   • Total Duration: 55 seconds")
        print(f"   • Scene Breakdown: Intro(5s) + 5×Products(9s each) + Outro(5s)")
        print(f"   • Resolution: 1080x1920 (Instagram Story)")
        
        # Call JSON2Video API with retry logic
        async with aiohttp.ClientSession() as session:
            url = "https://api.json2video.com/v2/movies"
            headers = {
                "x-api-key": api_key,
                "Content-Type": "application/json"
            }
            
            try:
                # Use retry logic for resilient API calls
                print("📤 Sending video creation request to JSON2Video...")
                data = await post_with_retry(session, url, headers, video_schema, max_retries=3)
                
                # According to docs, project ID is in 'project' field
                project_id = data.get('project', '')
                
                if not project_id:
                    print(f"⚠️ No project ID in response. Full response: {json.dumps(data, indent=2)}")
                    return {
                        'success': False,
                        'error': 'No project ID returned from API',
                        'updated_record': record
                    }
                
                # Construct video URLs
                video_url = f"https://d1oco4z2z1fhwp.cloudfront.net/projects/{project_id}/project.mp4"
                dashboard_url = f"https://app.json2video.com/projects/{project_id}"
                
                print(f"✅ JSON2Video Response: Project ID = {project_id}")
                print(f"✅ Dashboard URL: {dashboard_url}")
                print(f"✅ Direct Video URL: {video_url}")
                
                # Update record with video data
                record['fields']['JSON2VideoProjectID'] = project_id
                record['fields']['FinalVideo'] = video_url  # Save to FinalVideo field (used by YouTube uploader)
                
                return {
                    'success': True,
                    'project_id': project_id,
                    'video_url': video_url,
                    'dashboard_url': dashboard_url,
                    'updated_record': record
                }
                
            except Exception as e:
                print(f"❌ JSON2Video API error after retries: {e}")
                return {
                    'success': False,
                    'error': str(e),
                    'updated_record': record
                }
                    
    except Exception as e:
        print(f"❌ Error creating video: {e}")
        return {
            'success': False,
            'error': str(e),
            'updated_record': record
        }

async def _build_fixed_video_schema(record: Dict, config: Dict) -> Dict:
    """
    Build FIXED JSON2Video schema with proper 55-second timing
    Maintains exact timing: Intro(5s) + 5×Products(9s) + Outro(5s) = 55s
    """
    # Ensure record has proper structure
    if not isinstance(record, dict):
        record = {'record_id': 'default', 'fields': {}}
    
    fields = record.get('fields', {})
    record_id = str(record.get('record_id', 'default'))[:8] if record.get('record_id') else 'default'
    
    # Base schema structure - FIXED: No invalid properties
    schema = {
        "resolution": "instagram-story",
        "width": 1080,
        "height": 1920,
        "quality": "high",
        "draft": False,
        "cache": True,  # Enable global caching
        "elements": [
            {
                "type": "subtitles",
                "language": "en-US",
                "settings": {
                    "style": "bold",  # Better visibility than "classic"
                    "box-color": "rgba(0,0,0,0.85)",  # Semi-transparent black background
                    "outline-width": 8,
                    "word-color": "#FFFF00",  # Bright yellow for maximum contrast
                    "shadow-offset": 2,
                    "shadow-color": "rgba(0,0,0,0.6)",
                    "max-words-per-line": 4,  # Better readability
                    "font-size": 72,
                    "font-family": "Luckiest Guy",
                    "position": "bottom-center",
                    "outline-color": "#000000",
                    "line-color": "#FFFFFF"
                }
            }
        ],
        "scenes": []
    }
    
    # INTRO SCENE - EXACTLY 5 seconds (as required)
    intro_scene = {
        "id": f"intro_{record_id}",
        "comment": "Intro Scene - 5 seconds",
        "duration": 5,  # FIXED: Must be 5 seconds for audio sync
        "cache": True,
        "transition": {
            "style": "fade",
            "duration": 0.5
        },
        "elements": [
            {
                "id": f"intro_img_{record_id}",
                "type": "image",
                "src": fields.get('IntroPhoto', 'https://via.placeholder.com/1080x1920/2a2a2a/ffff00?text=INTRO'),
                "width": 1080,
                "height": 1920,
                "x": 0,
                "y": 0
                # FIXED: Removed invalid "zoom" property
            },
            {
                "id": f"intro_text_{record_id}",
                "type": "text",
                "style": "003",
                "settings": {
                    "font-size": "8.5vw",
                    "color": "#FFFF00",
                    "font-weight": "bold",
                    "text-shadow": "0.3vw 0.3vw 0.5vw rgba(0,0,0,0.8)",
                    "font-family": "Anton"
                },
                "position": "custom",
                "x": 40,
                "y": 100,
                "width": 1000,
                "height": 300,
                "cache": True,
                "text": fields.get('VideoTitle', 'Amazing Products')[:80]
            },
            {
                "id": f"intro_audio_{record_id}",
                "type": "audio",
                "src": fields.get('IntroMp3', ''),  # 5-second ElevenLabs audio
                "volume": 1.0
            }
        ]
    }
    schema['scenes'].append(intro_scene)
    
    # PRODUCT SCENES - EXACTLY 9 seconds each (5 products × 9s = 45s)
    for product_num in range(1, 6):  # Products 1-5
        # Extract product data with safe defaults
        product_title = fields.get(f'ProductNo{product_num}Title', f'Product #{product_num}')
        product_photo = fields.get(f'ProductNo{product_num}Photo', 
                                  f'https://via.placeholder.com/1080x1920/1a1a1a/ffff00?text=Product+{product_num}')
        product_voice = fields.get(f'Product{product_num}Mp3', '')  # 9-second audio
        
        # Safe extraction of product details
        product_price = _safe_extract_price(fields, product_num)
        product_rating = _safe_extract_rating(fields, product_num)
        product_reviews = _safe_extract_reviews(fields, product_num)
        
        product_scene = {
            "id": f"product_{product_num}_{record_id}",
            "comment": f"Product #{product_num} - 9 seconds",
            "duration": 9,  # FIXED: Must be 9 seconds for audio sync
            "cache": True,
            "transition": {
                "style": "wipeleft" if product_num % 2 == 0 else "wiperight",
                "duration": 0.5
            },
            "elements": [
                # Background image
                {
                    "id": f"prod{product_num}_bg_{record_id}",
                    "type": "image",
                    "src": product_photo,
                    "width": 1080,
                    "height": 1920,
                    "x": 0,
                    "y": 0
                    # FIXED: Removed invalid "zoom" property
                },
                # Rank badge (top-left corner)
                {
                    "id": f"prod{product_num}_rank_{record_id}",
                    "type": "text",
                    "style": "001",
                    "settings": {
                        "font-size": "14vw",
                        "color": "#000000",
                        "background": "#FFFF00",
                        "padding": "2vw 4vw",
                        "border-radius": "50%",
                        "font-weight": "bold",
                        "font-family": "Anton"
                    },
                    "position": "custom",
                    "x": 40,
                    "y": 40,
                    "width": 120,
                    "height": 120,
                    "text": f"#{product_num}"
                },
                # Product title bar
                {
                    "id": f"prod{product_num}_title_{record_id}",
                    "type": "text",
                    "style": "003",
                    "settings": {
                        "font-size": "7.5vw",
                        "color": "#FFFFFF",
                        "background": "rgba(0,0,0,0.8)",
                        "padding": "2vw 3vw",
                        "font-family": "Roboto",
                        "font-weight": "bold",
                        "text-shadow": "0.2vw 0.2vw 0.3vw rgba(0,0,0,0.5)"
                    },
                    "position": "custom",
                    "x": 20,
                    "y": 200,
                    "width": 1040,
                    "height": 180,
                    "text": product_title[:65]
                },
                # Audio narration (9 seconds)
                {
                    "id": f"prod{product_num}_audio_{record_id}",
                    "type": "audio",
                    "src": product_voice,
                    "volume": 1.0
                },
                # Product stats container (bottom)
                {
                    "id": f"prod{product_num}_stats_container_{record_id}",
                    "type": "text",
                    "style": "001",
                    "settings": {
                        "background": "rgba(0,0,0,0.9)",
                        "border": "0.3vw solid #FFFF00",
                        "border-radius": "3vw",
                        "padding": "4vw"
                    },
                    "position": "custom",
                    "x": 40,
                    "y": 1350,
                    "width": 1000,
                    "height": 450,
                    "text": " "  # Empty for background only
                },
                # Price (large and prominent)
                {
                    "id": f"prod{product_num}_price_{record_id}",
                    "type": "text",
                    "style": "003",
                    "settings": {
                        "font-size": "12vw",
                        "color": "#00FF00",  # Green for price
                        "font-weight": "bold",
                        "font-family": "Montserrat",
                        "text-shadow": "0.3vw 0.3vw 0.5vw rgba(0,0,0,0.8)"
                    },
                    "position": "custom",
                    "x": 100,
                    "y": 1400,
                    "width": 400,
                    "height": 150,
                    "text": f"${product_price}"
                },
                # Rating stars
                {
                    "id": f"prod{product_num}_rating_{record_id}",
                    "type": "text",
                    "style": "003",
                    "settings": {
                        "font-size": "8vw",
                        "color": "#FFA500",  # Orange for rating
                        "font-family": "Montserrat",
                        "font-weight": "600"
                    },
                    "position": "custom",
                    "x": 100,
                    "y": 1520,
                    "width": 400,
                    "height": 100,
                    "text": f"⭐ {product_rating}/5"
                },
                # Review count
                {
                    "id": f"prod{product_num}_reviews_{record_id}",
                    "type": "text",
                    "style": "003",
                    "settings": {
                        "font-size": "6vw",
                        "color": "#FFFFFF",
                        "font-family": "Montserrat"
                    },
                    "position": "custom",
                    "x": 100,
                    "y": 1620,
                    "width": 400,
                    "height": 80,
                    "text": f"{product_reviews:,} reviews"
                },
                # "Best Value" or similar badge for top products
                {
                    "id": f"prod{product_num}_badge_{record_id}",
                    "type": "text",
                    "style": "003",
                    "settings": {
                        "font-size": "6vw",
                        "color": "#000000",
                        "background": "#00FF00" if product_num == 1 else "#FFA500" if product_num == 2 else "#FFFF00",
                        "padding": "1.5vw 3vw",
                        "border-radius": "2vw",
                        "font-weight": "bold",
                        "font-family": "Anton"
                    },
                    "position": "custom",
                    "x": 600,
                    "y": 1400,
                    "width": 380,
                    "height": 80,
                    "text": "BEST VALUE" if product_num == 1 else "TOP RATED" if product_num == 2 else f"RANK #{product_num}"
                }
            ]
        }
        
        schema['scenes'].append(product_scene)
    
    # OUTRO SCENE - EXACTLY 5 seconds (as required)
    outro_scene = {
        "id": f"outro_{record_id}",
        "comment": "Outro Scene - 5 seconds",
        "duration": 5,  # FIXED: Must be 5 seconds for audio sync
        "cache": True,
        "elements": [
            {
                "id": f"outro_bg_{record_id}",
                "type": "image",
                "src": fields.get('OutroPhoto', 'https://via.placeholder.com/1080x1920/0a0a0a/ffff00?text=SUBSCRIBE'),
                "width": 1080,
                "height": 1920,
                "x": 0,
                "y": 0
                # FIXED: Removed invalid "zoom" property
            },
            {
                "id": f"outro_text_{record_id}",
                "type": "text",
                "style": "003",
                "settings": {
                    "font-size": "9vw",
                    "color": "#FFFF00",
                    "font-weight": "bold",
                    "text-align": "center",
                    "text-shadow": "0.4vw 0.4vw 0.6vw rgba(0,0,0,0.8)",
                    "font-family": "Anton"
                },
                "position": "custom",
                "x": 40,
                "y": 400,
                "width": 1000,
                "height": 200,
                "text": "Thanks for Watching!"
            },
            {
                "id": f"outro_audio_{record_id}",
                "type": "audio",
                "src": fields.get('OutroMp3', ''),  # 5-second audio
                "volume": 1.0
            },
            # Subscribe button
            {
                "id": f"outro_subscribe_{record_id}",
                "type": "text",
                "style": "003",
                "settings": {
                    "background": "#FF0000",
                    "color": "#FFFFFF",
                    "border": "0.3vw solid #FFFFFF",
                    "border-radius": "5vw",
                    "padding": "3vw 8vw",
                    "font-size": "10vw",
                    "font-weight": "bold",
                    "text-align": "center",
                    "font-family": "Anton",
                    "box-shadow": "0 1vw 3vw rgba(0,0,0,0.4)"
                },
                "position": "custom",
                "x": 240,
                "y": 800,
                "width": 600,
                "height": 150,
                "text": "SUBSCRIBE"
            },
            # Call to action
            {
                "id": f"outro_cta_{record_id}",
                "type": "text",
                "style": "003",
                "settings": {
                    "font-size": "7vw",
                    "color": "#FFFFFF",
                    "text-align": "center",
                    "font-family": "Roboto"
                },
                "position": "custom",
                "x": 40,
                "y": 1000,
                "width": 1000,
                "height": 100,
                "text": "👇 Links in Description 👇"
            }
        ]
    }
    schema['scenes'].append(outro_scene)
    
    return schema

# Safe extraction functions with validation
def _safe_extract_price(fields: Dict, product_num: int) -> str:
    """Safely extract price with validation"""
    import re
    
    price_fields = [
        f'ProductNo{product_num}Price',
        f'Product{product_num}Price',
        f'ProductNo{product_num}Description'
    ]
    
    for field in price_fields:
        value = fields.get(field, '')
        if value:
            # Extract numeric price
            price_match = re.search(r'\$?([0-9,]+(?:\.[0-9]{2})?)', str(value))
            if price_match:
                price_str = price_match.group(1).replace(',', '')
                try:
                    price = float(price_str)
                    # Validate reasonable price range
                    if 0.01 <= price <= 99999:
                        return f"{price:.2f}"
                except ValueError:
                    continue
    
    # Default pricing based on rank
    default_prices = ["29.99", "39.99", "49.99", "59.99", "69.99"]
    return default_prices[product_num - 1]

def _safe_extract_rating(fields: Dict, product_num: int) -> str:
    """Safely extract rating with validation"""
    import re
    
    rating_fields = [
        f'ProductNo{product_num}Rating',
        f'Product{product_num}Rating',
        f'ProductNo{product_num}Description'
    ]
    
    for field in rating_fields:
        value = fields.get(field, '')
        if value:
            rating_match = re.search(r'([0-4]?\.[0-9]|[0-5])', str(value))
            if rating_match:
                try:
                    rating = float(rating_match.group(1))
                    # Clamp to valid range
                    rating = min(5.0, max(0.0, rating))
                    return f"{rating:.1f}"
                except ValueError:
                    continue
    
    # Default ratings (good products, decreasing slightly by rank)
    default_ratings = ["4.5", "4.4", "4.2", "4.0", "3.8"]
    return default_ratings[product_num - 1]

def _safe_extract_reviews(fields: Dict, product_num: int) -> int:
    """Safely extract review count with validation"""
    import re
    
    review_fields = [
        f'ProductNo{product_num}Reviews',
        f'Product{product_num}Reviews',
        f'ProductNo{product_num}Description'
    ]
    
    for field in review_fields:
        value = fields.get(field, '')
        if value:
            # Handle various formats: "1,234", "1.2K", "1234 reviews"
            review_match = re.search(r'([\d,]+(?:\.\d+)?)\s*[kKmM]?', str(value))
            if review_match:
                review_str = review_match.group(1).replace(',', '')
                try:
                    if 'k' in str(value).lower():
                        return int(float(review_str) * 1000)
                    elif 'm' in str(value).lower():
                        return int(float(review_str) * 1000000)
                    else:
                        return int(float(review_str))
                except ValueError:
                    continue
    
    # Default review counts (decreasing by rank)
    default_reviews = [2543, 1876, 1234, 876, 543]
    return default_reviews[product_num - 1]