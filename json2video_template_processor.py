#!/usr/bin/env python3
"""
JSON2Video Template Processor
Processes the unified JSON schema template with Airtable data
"""

import json
import re
from typing import Dict, Any

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
            # Convert rating fields to stars
            if 'Rating' in key and isinstance(value, (str, int, float)):
                star_value = convert_rating_to_stars(str(value))
                template_str = template_str.replace(f"{{{{{key}}}}}", star_value)
            else:
                # Replace regular placeholders
                template_str = template_str.replace(f"{{{{{key}}}}}", str(value))
    
    # Handle special star rating conversions for products
    for i in range(1, 6):
        rating_key = f"ProductNo{i}Rating"
        if rating_key in data:
            stars = convert_rating_to_stars(str(data[rating_key]))
            template_str = template_str.replace(f"{{{{ProductNo{i}Stars}}}}", stars)
    
    # Clean up any remaining placeholders with default values
    template_str = re.sub(r'\{\{VideoTitle\}\}', data.get('VideoTitle', 'Top 5 Products'), template_str)
    template_str = re.sub(r'\{\{VideoDescription\}\}', data.get('VideoDescription', 'Check out these amazing products!'), template_str)
    
    # Product placeholders with defaults
    for i in range(1, 6):
        template_str = re.sub(f'\\{{\\{{ProductNo{i}Title\\}}\\}}', data.get(f'ProductNo{i}Title', f'Product {i}'), template_str)
        template_str = re.sub(f'\\{{\\{{ProductNo{i}Price\\}}\\}}', data.get(f'ProductNo{i}Price', '$99.99'), template_str)
        template_str = re.sub(f'\\{{\\{{ProductNo{i}Reviews\\}}\\}}', data.get(f'ProductNo{i}Reviews', '1,234'), template_str)
        template_str = re.sub(f'\\{{\\{{ProductNo{i}Rating\\}}\\}}', data.get(f'ProductNo{i}Rating', '4.5'), template_str)
        template_str = re.sub(f'\\{{\\{{ProductNo{i}Stars\\}}\\}}', convert_rating_to_stars(str(data.get(f'ProductNo{i}Rating', '4.5'))), template_str)
        template_str = re.sub(f'\\{{\\{{ProductNo{i}Photo\\}}\\}}', data.get(f'ProductNo{i}Photo', 'https://via.placeholder.com/400'), template_str)
    
    # Audio placeholders
    template_str = re.sub(r'\{\{IntroAudio\}\}', data.get('IntroAudio', ''), template_str)
    template_str = re.sub(r'\{\{OutroAudio\}\}', data.get('OutroAudio', ''), template_str)
    for i in range(1, 6):
        template_str = re.sub(f'\\{{\\{{ProductNo{i}Audio\\}}\\}}', data.get(f'ProductNo{i}Audio', ''), template_str)
    
    # Remove any remaining empty placeholders
    template_str = re.sub(r'\{\{[^}]+\}\}', '', template_str)
    
    # Parse back to JSON
    try:
        processed_template = json.loads(template_str)
        return processed_template
    except json.JSONDecodeError as e:
        print(f"Error processing template: {e}")
        print(f"Template string: {template_str[:500]}...")
        raise

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