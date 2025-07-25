#!/usr/bin/env python3
"""
JSON2Video Template Processor
Processes the unified schema template with dynamic data from Airtable records
"""

import json
import re
from typing import Dict, Any

def convert_rating_to_stars(rating: str) -> str:
    """Convert numeric rating (e.g., '4.5') to star display (★★★★☆)"""
    try:
        rating_float = float(rating)
        full_stars = int(rating_float)
        has_half = rating_float - full_stars >= 0.5
        empty_stars = 5 - full_stars - (1 if has_half else 0)
        
        star_display = "★" * full_stars
        if has_half:
            star_display += "☆"  # Half star representation
        star_display += "☆" * empty_stars
        
        return star_display
    except (ValueError, TypeError):
        return "★★★★★"  # Default to 5 stars if error

def process_template(template_path: str, record_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process the JSON2Video template with actual data from Airtable record
    
    Args:
        template_path: Path to the JSON template file
        record_data: Dictionary containing Airtable record data
        
    Returns:
        Processed JSON schema ready for JSON2Video API
    """
    
    # Load the template
    with open(template_path, 'r') as f:
        template_content = f.read()
    
    # Create dynamic replacements dictionary
    replacements = {
        # Video metadata
        "{{VideoTitle}}": record_data.get('VideoTitle', 'Top 5 Products Review'),
        "{{SubtitleSRTURL}}": record_data.get('SubtitleSRTURL', ''),
        
        # Intro data
        "{{IntroHook}}": record_data.get('IntroHook', 'Welcome! Today we\'re counting down the top 5 products.'),
        "{{IntroPhoto}}": record_data.get('IntroPhoto', 'https://drive.google.com/uc?id=1s5J3T82ISC3P6COkFjenhOT58JACwSfD&export=download'),
        "{{IntroVoiceURL}}": record_data.get('IntroVoiceURL', ''),
        
        # Outro data
        "{{OutroCallToAction}}": record_data.get('OutroCallToAction', 'Thanks for watching! Subscribe for more!'),
        "{{OutroPhoto}}": record_data.get('OutroPhoto', 'https://drive.google.com/uc?id=1s5J3T82ISC3P6COkFjenhOT58JACwSfD&export=download'),
        "{{OutroVoiceURL}}": record_data.get('OutroVoiceURL', '')
    }
    
    # Process each product (1-5)
    for i in range(1, 6):
        # Product data
        product_title = record_data.get(f'ProductNo{i}Title', f'Product {i}')
        product_photo = record_data.get(f'ProductNo{i}Photo', 'https://drive.google.com/uc?id=1s5J3T82ISC3P6COkFjenhOT58JACwSfD&export=download')
        product_reviews = record_data.get(f'ProductNo{i}Reviews', '1,000')
        product_rating = record_data.get(f'ProductNo{i}Rating', '4.5')
        product_price = record_data.get(f'ProductNo{i}Price', '99.99')
        product_voice_url = record_data.get(f'Product{i}VoiceURL', '')
        
        # Convert rating to stars
        star_rating = convert_rating_to_stars(product_rating)
        
        # Add to replacements
        replacements.update({
            f"{{{{ProductNo{i}Title}}}}": product_title,
            f"{{{{ProductNo{i}Photo}}}}": product_photo,
            f"{{{{ProductNo{i}Reviews}}}}": product_reviews,
            f"{{{{ProductNo{i}Rating}}}}": product_rating,
            f"{{{{ProductNo{i}StarRating}}}}": star_rating,
            f"{{{{ProductNo{i}Price}}}}": product_price,
            f"{{{{Product{i}VoiceURL}}}}": product_voice_url
        })
    
    # Replace all placeholders
    processed_content = template_content
    for placeholder, value in replacements.items():
        processed_content = processed_content.replace(placeholder, str(value))
    
    # Convert to JSON object
    processed_json = json.loads(processed_content)
    
    # Clean up empty audio sources
    for scene in processed_json.get('scenes', []):
        for element in scene.get('elements', []):
            if element.get('type') == 'audio' and not element.get('src'):
                # Remove audio element if no source URL
                scene['elements'].remove(element)
    
    # Handle missing subtitle URL
    if processed_json.get('elements'):
        subtitle_element = processed_json['elements'][0]
        if subtitle_element.get('type') == 'subtitles' and not subtitle_element.get('captions'):
            # Remove captions field if empty
            subtitle_element.pop('captions', None)
    
    return processed_json

def save_processed_schema(schema: Dict[str, Any], output_path: str):
    """Save the processed schema to a JSON file"""
    with open(output_path, 'w') as f:
        json.dump(schema, f, indent=2)
    print(f"✅ Processed schema saved to: {output_path}")

# Example usage
if __name__ == "__main__":
    # Example Airtable record data
    sample_record_data = {
        'VideoTitle': 'Top 5 Best Kitchen Gadgets 2025',
        'IntroHook': 'Welcome! Today we\'re reviewing the best kitchen gadgets that will transform your cooking!',
        'IntroPhoto': 'https://drive.google.com/uc?id=1W7eRtz9cxkAOoAOF-5N7oc013YsOvSuX&export=download',
        'IntroVoiceURL': 'https://example.com/intro_voice.mp3',
        
        # Product 1 (Winner)
        'ProductNo1Title': 'InstantPot Duo Plus',
        'ProductNo1Photo': 'https://drive.google.com/uc?id=1s5J3T82ISC3P6COkFjenhOT58JACwSfD&export=download',
        'ProductNo1Reviews': '45,678',
        'ProductNo1Rating': '4.8',
        'ProductNo1Price': '89.99',
        'Product1VoiceURL': 'https://example.com/product1_voice.mp3',
        
        # Product 2
        'ProductNo2Title': 'Ninja Foodi Blender',
        'ProductNo2Photo': 'https://drive.google.com/uc?id=10-vElXFcVhVU5FDJUEGdh4I_ZziDN2lJ&export=download',
        'ProductNo2Reviews': '23,456',
        'ProductNo2Rating': '4.5',
        'ProductNo2Price': '149.99',
        'Product2VoiceURL': 'https://example.com/product2_voice.mp3',
        
        # Product 3
        'ProductNo3Title': 'KitchenAid Stand Mixer',
        'ProductNo3Photo': 'https://drive.google.com/uc?id=1wQYvUpZsCLGx8A2o90cTcO88dSsXJnFE&export=download',
        'ProductNo3Reviews': '34,567',
        'ProductNo3Rating': '4.7',
        'ProductNo3Price': '279.99',
        'Product3VoiceURL': 'https://example.com/product3_voice.mp3',
        
        # Product 4
        'ProductNo4Title': 'Air Fryer Pro Max',
        'ProductNo4Photo': 'https://drive.google.com/uc?id=13VuwBBsIsv6gLYoiS3q6XfoRvVZGgQpZ&export=download',
        'ProductNo4Reviews': '12,345',
        'ProductNo4Rating': '4.3',
        'ProductNo4Price': '69.99',
        'Product4VoiceURL': 'https://example.com/product4_voice.mp3',
        
        # Product 5
        'ProductNo5Title': 'Smart Coffee Maker',
        'ProductNo5Photo': 'https://drive.google.com/uc?id=1W7eRtz9cxkAOoAOF-5N7oc013YsOvSuX&export=download',
        'ProductNo5Reviews': '8,901',
        'ProductNo5Rating': '4.1',
        'ProductNo5Price': '199.99',
        'Product5VoiceURL': 'https://example.com/product5_voice.mp3',
        
        # Outro
        'OutroCallToAction': 'Thanks for watching! Subscribe and hit the bell for more amazing product reviews!',
        'OutroPhoto': 'https://drive.google.com/uc?id=1s5J3T82ISC3P6COkFjenhOT58JACwSfD&export=download',
        'OutroVoiceURL': 'https://example.com/outro_voice.mp3'
    }
    
    # Process the template
    processed_schema = process_template(
        'json2video_unified_schema_template.json',
        sample_record_data
    )
    
    # Save the processed schema
    save_processed_schema(processed_schema, 'json2video_processed_example.json')
    
    # Print summary
    print(f"\n📊 Video Summary:")
    print(f"   Title: {sample_record_data['VideoTitle']}")
    print(f"   Total Duration: {sum(scene['duration'] for scene in processed_schema['scenes'])} seconds")
    print(f"   Number of Scenes: {len(processed_schema['scenes'])}")
    print(f"   Resolution: {processed_schema['width']}x{processed_schema['height']} (9:16)")