#!/usr/bin/env python3
"""
JSON2Video Template Processor
Processes the unified JSON schema template with Airtable data
"""

import json
import re
import logging
from typing import Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_rating_to_stars(rating: str) -> str:
    """Convert numeric rating to star display"""
    try:
        rating_float = float(rating)
        full_stars = int(rating_float)
        half_star = 1 if (rating_float - full_stars) >= 0.5 else 0
        empty_stars = 5 - full_stars - half_star
        
        star_display = "★" * full_stars
        if half_star:
            star_display += "☆"
        star_display += "☆" * empty_stars
        
        return star_display
    except (ValueError, TypeError):
        return "★★★★☆"  # Default 4 stars

def process_template(template_path: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process JSON2Video template with Airtable data
    
    Args:
        template_path: Path to the JSON template file
        data: Dictionary containing Airtable record data
        
    Returns:
        Processed JSON ready for JSON2Video API
    """
    # Load the template
    with open(template_path, 'r') as f:
        template = json.load(f)
    
    # Convert template to string for placeholder replacement
    template_str = json.dumps(template)
    
    # Process all placeholders in the template
    for key, value in data.items():
        if value is not None:
            # Ensure value is string-compatible
            try:
                # Convert ONLY StarRating fields to stars, keep Rating fields numeric
                if 'StarRating' in key and isinstance(value, (str, int, float)):
                    star_value = convert_rating_to_stars(str(value))
                    template_str = template_str.replace(f"{{{{{key}}}}}", star_value)
                else:
                    # Safely convert to string, handling all data types
                    if isinstance(value, (dict, list)):
                        str_value = json.dumps(value)
                    elif isinstance(value, bool):
                        str_value = str(value).lower()
                    elif isinstance(value, (int, float)):
                        str_value = str(value)
                    else:
                        str_value = str(value)
                    
                    # Replace regular placeholders
                    template_str = template_str.replace(f"{{{{{key}}}}}", str_value)
            except Exception as e:
                print(f"Warning: Could not process key {key} with value {value}: {e}")
                # Skip problematic values
                continue
    
    # Handle special rating conversions for products - NUMERIC for JSON2Video components
    for i in range(1, 6):
        rating_key = f"ProductNo{i}Rating"
        reviews_key = f"ProductNo{i}Reviews"
        price_key = f"ProductNo{i}Price"
        
        # Ensure ratings are numeric integers for JSON2Video components (e.g., 4.5 -> 4)
        if rating_key in data:
            try:
                # Convert to integer for component value (JSON2Video advanced/070 expects integer)
                numeric_rating = int(float(str(data[rating_key])))
                data[rating_key] = numeric_rating
                logger.info(f"🌟 Component rating for Product {i}: {numeric_rating}")
            except (ValueError, TypeError):
                data[rating_key] = 4  # Default to 4 stars
        
        # Ensure review counts are numeric integers (remove commas, convert to int)
        if reviews_key in data:
            try:
                # Remove commas and convert to integer for component counter
                review_count = str(data[reviews_key]).replace(',', '').replace(' Reviews', '').strip()
                numeric_reviews = int(float(review_count))
                data[reviews_key] = numeric_reviews
            except (ValueError, TypeError):
                data[reviews_key] = 1234  # Default review count
        
        # Ensure prices are numeric integers (remove $ and convert to int)
        if price_key in data:
            try:
                # Remove $ and convert to integer for component counter
                price_value = str(data[price_key]).replace('$', '').replace(',', '').strip()
                numeric_price = int(float(price_value))
                data[price_key] = numeric_price
            except (ValueError, TypeError):
                data[price_key] = 99  # Default price
    
    # Clean up any remaining placeholders with default values - ENSURE ALL ARE STRINGS
    template_str = re.sub(r'\{\{VideoTitle\}\}', str(data.get('VideoTitle', 'Top 5 Products')), template_str)
    template_str = re.sub(r'\{\{VideoDescription\}\}', str(data.get('VideoDescription', 'Check out these amazing products!')), template_str)
    
    # Product placeholders with defaults - ENSURE ALL VALUES ARE STRINGS
    for i in range(1, 6):
        template_str = re.sub(f'\\{{\\{{ProductNo{i}Title\\}}\\}}', str(data.get(f'ProductNo{i}Title', f'Product {i}')), template_str)
        template_str = re.sub(f'\\{{\\{{ProductNo{i}Price\\}}\\}}', str(data.get(f'ProductNo{i}Price', '$99.99')), template_str)
        template_str = re.sub(f'\\{{\\{{ProductNo{i}Reviews\\}}\\}}', str(data.get(f'ProductNo{i}Reviews', '1,234')), template_str)
        
        # CRITICAL FIX: Keep numeric rating as number, stars as stars
        numeric_rating = str(data.get(f'ProductNo{i}Rating', '4.5'))
        template_str = re.sub(f'\\{{\\{{ProductNo{i}Rating\\}}\\}}', numeric_rating, template_str)
        
        # Handle star field names - convert numeric rating to stars
        star_rating = convert_rating_to_stars(numeric_rating)
        template_str = re.sub(f'\\{{\\{{ProductNo{i}Stars\\}}\\}}', star_rating, template_str)
        template_str = re.sub(f'\\{{\\{{ProductNo{i}StarRating\\}}\\}}', star_rating, template_str)
        
        template_str = re.sub(f'\\{{\\{{ProductNo{i}Photo\\}}\\}}', str(data.get(f'ProductNo{i}Photo', 'https://via.placeholder.com/400')), template_str)
    
    # Audio placeholders - ENSURE ALL ARE STRINGS
    template_str = re.sub(r'\{\{IntroVoiceURL\}\}', str(data.get('IntroVoiceURL', '')), template_str)
    template_str = re.sub(r'\{\{OutroVoiceURL\}\}', str(data.get('OutroVoiceURL', '')), template_str)
    for i in range(1, 6):
        template_str = re.sub(f'\\{{\\{{Product{i}VoiceURL\\}}\\}}', str(data.get(f'Product{i}VoiceURL', '')), template_str)
    
    # Legacy audio field support
    template_str = re.sub(r'\{\{IntroAudio\}\}', str(data.get('IntroAudio', '')), template_str)
    template_str = re.sub(r'\{\{OutroAudio\}\}', str(data.get('OutroAudio', '')), template_str)
    for i in range(1, 6):
        template_str = re.sub(f'\\{{\\{{ProductNo{i}Audio\\}}\\}}', str(data.get(f'ProductNo{i}Audio', '')), template_str)
    
    # Handle any remaining placeholders with working audio URLs
    # Using working audio files until Google Drive file IDs are available
    working_audio_url = 'https://www.learningcontainer.com/wp-content/uploads/2020/02/Kalimba.mp3'
    
    # IntroVoiceURL and OutroVoiceURL fallbacks  
    template_str = re.sub(r'\{\{IntroVoiceURL\}\}', working_audio_url, template_str)
    template_str = re.sub(r'\{\{OutroVoiceURL\}\}', working_audio_url, template_str)
    
    # Product voice URL fallbacks - use the same working URL for all products
    for i in range(1, 6):
        template_str = re.sub(f'\\{{\\{{Product{i}VoiceURL\\}}\\}}', working_audio_url, template_str)
    
    # Remove any remaining empty placeholders after all fallbacks
    template_str = re.sub(r'\{\{[^}]+\}\}', '', template_str)
    
    # Parse back to JSON
    try:
        processed_template = json.loads(template_str)
        
        # Validate and clean the processed template
        cleaned_template = validate_and_clean_template(processed_template)
        return cleaned_template
    except json.JSONDecodeError as e:
        print(f"Error processing template: {e}")
        print(f"Template string: {template_str[:500]}...")
        raise

def validate_and_clean_template(template: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and clean JSON2Video template to prevent API validation errors
    
    Args:
        template: Processed JSON template
        
    Returns:
        Cleaned template with invalid properties removed
    """
    
    # List of invalid properties that cause JSON2Video API errors
    INVALID_SUBTITLE_PROPERTIES = [
        'vertical-align',  # CRITICAL: This property is not allowed in subtitle elements
        'vertical_align',   # Alternative naming
        'text-align',      # Use alignment in style instead
        'align'            # Use alignment in style instead
    ]
    
    cleaned_template = template.copy()
    fixes_applied = []
    
    # Check all scenes for subtitle elements
    if 'scenes' in cleaned_template:
        for scene_idx, scene in enumerate(cleaned_template['scenes']):
            if 'elements' in scene:
                for elem_idx, element in enumerate(scene['elements']):
                    if element.get('type') == 'subtitles':
                        if 'settings' in element:
                            # Remove invalid properties from subtitle settings
                            for invalid_prop in INVALID_SUBTITLE_PROPERTIES:
                                if invalid_prop in element['settings']:
                                    del element['settings'][invalid_prop]
                                    fix_msg = f"Removed '{invalid_prop}' from scene[{scene_idx}].elements[{elem_idx}].settings"
                                    fixes_applied.append(fix_msg)
                                    logger.info(f"🧹 {fix_msg}")
                            
                            # Ensure offset-y is used for positioning instead of vertical-align
                            if 'offset-y' not in element['settings']:
                                element['settings']['offset-y'] = 900  # Default bottom positioning
                                fix_msg = f"Added 'offset-y': 900 to scene[{scene_idx}].elements[{elem_idx}].settings"
                                fixes_applied.append(fix_msg)
                                logger.info(f"✅ {fix_msg}")
    
    if fixes_applied:
        logger.info(f"🔧 Applied {len(fixes_applied)} template fixes to prevent JSON2Video API errors")
        for fix in fixes_applied:
            logger.info(f"   - {fix}")
    else:
        logger.info("✅ Template validation passed - no fixes needed")
    
    return cleaned_template

if __name__ == "__main__":
    # Test the processor
    test_data = {
        'VideoTitle': 'Top 5 Amazing Products',
        'VideoDescription': 'Check out these incredible finds!',
        'ProductNo1Title': 'Amazing Product 1',
        'ProductNo1Price': '$29.99',
        'ProductNo1Rating': '4.5',
        'ProductNo1Reviews': '1,234',
        'ProductNo1Photo': 'https://example.com/product1.jpg'
    }
    
    template_path = 'Test_json2video_schema.json'
    try:
        result = process_template(template_path, test_data)
        print("✅ Template processing successful")
        print(f"Scenes: {len(result.get('scenes', []))}")
    except Exception as e:
        print(f"❌ Template processing failed: {e}")