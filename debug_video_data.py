#!/usr/bin/env python3
"""
Debug script to check what data was sent to JSON2Video
"""

import json
from json2video_template_processor import process_template

# Test data similar to what the workflow uses
test_data = {
    'VideoTitle': 'Test Video Title',
    'ProductNo1Title': 'Test Product 1',
    'ProductNo1Rating': '4.5',
    'ProductNo1Reviews': '1,234',
    'ProductNo1Price': '29.99',
    'ProductNo1StarRating': '★★★★☆',  # This should be auto-generated
    
    'ProductNo2Title': 'Test Product 2', 
    'ProductNo2Rating': '4.2',
    'ProductNo2Reviews': '856',
    'ProductNo2Price': '39.99',
    
    # Add some voice URLs
    'IntroVoiceURL': 'https://www.learningcontainer.com/wp-content/uploads/2020/02/Kalimba.mp3',
    'OutroVoiceURL': 'https://www.learningcontainer.com/wp-content/uploads/2020/02/Kalimba.mp3',
    'Product1VoiceURL': 'https://www.learningcontainer.com/wp-content/uploads/2020/02/Kalimba.mp3',
    'Product2VoiceURL': 'https://www.learningcontainer.com/wp-content/uploads/2020/02/Kalimba.mp3',
}

# Add missing products
for i in range(3, 6):
    test_data[f'ProductNo{i}Title'] = f'Test Product {i}'
    test_data[f'ProductNo{i}Rating'] = '4.3'
    test_data[f'ProductNo{i}Reviews'] = '999'
    test_data[f'ProductNo{i}Price'] = '49.99'
    test_data[f'Product{i}VoiceURL'] = 'https://www.learningcontainer.com/wp-content/uploads/2020/02/Kalimba.mp3'

# Process template
template_path = '/home/claude-workflow/Test_json2video_schema.json'
processed_json = process_template(template_path, test_data)

# Check star rating elements specifically
print("🔍 CHECKING STAR RATING ELEMENTS:")
for scene in processed_json.get('scenes', []):
    scene_id = scene.get('id', 'unknown')
    print(f"\n📋 Scene: {scene_id}")
    
    for element in scene.get('elements', []):
        element_id = element.get('id', 'unknown')
        if 'stars' in element_id or 'StarRating' in element.get('text', ''):
            print(f"   ⭐ Element {element_id}:")
            print(f"      Text: '{element.get('text', 'NO TEXT')}'")
            print(f"      Type: {element.get('type', 'NO TYPE')}")
            print(f"      Position: x={element.get('x')}, y={element.get('y')}")

# Save debug JSON to file  
with open('/home/claude-workflow/debug_processed_template.json', 'w') as f:
    json.dump(processed_json, f, indent=2)

print(f"\n✅ Processed template saved to debug_processed_template.json")
print(f"📊 Total scenes: {len(processed_json.get('scenes', []))}")