#!/usr/bin/env python3
"""
Check reference video project schema tK74gpADaEkrg6bg 
to understand the correct review element implementation
"""

import asyncio
import json
import requests
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_reference_project_schema():
    """Check the reference project schema via JSON2Video API"""
    
    # Load API configuration
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    api_key = config.get('json2video_api_key')
    project_id = 'tK74gpADaEkrg6bg'
    
    if not api_key:
        logger.error("❌ JSON2Video API key not found")
        return
    
    logger.info(f"🔍 Checking reference project schema: {project_id}")
    logger.info("📋 This is the CORRECT implementation where review elements render properly")
    
    try:
        # Call JSON2Video API to get project details
        headers = {
            'x-api-key': api_key,
            'Content-Type': 'application/json'
        }
        
        # Try the movies endpoint first
        logger.info("📡 Calling JSON2Video API...")
        response = requests.get(
            f"https://api.json2video.com/v2/movies?project={project_id}",
            headers=headers,
            timeout=10
        )
        
        logger.info(f"📊 API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            logger.info("✅ Successfully retrieved project data")
            
            # Save the full response for analysis
            with open('/home/claude-workflow/reference_project_data.json', 'w') as f:
                json.dump(result, f, indent=2)
            
            logger.info("💾 Full project data saved to reference_project_data.json")
            
            # Extract and analyze key information
            if isinstance(result, list) and len(result) > 0:
                project_data = result[0]
            else:
                project_data = result
            
            # Look for schema information
            logger.info("🔍 ANALYZING PROJECT STRUCTURE:")
            
            if 'status' in project_data:
                logger.info(f"   📊 Status: {project_data['status']}")
            
            if 'url' in project_data:
                logger.info(f"   🎬 Video URL: {project_data['url']}")
            
            if 'duration' in project_data:
                logger.info(f"   ⏱️ Duration: {project_data['duration']} seconds")
            
            # Look for template or schema data
            schema_fields = ['template', 'schema', 'movie', 'scenes', 'elements']
            for field in schema_fields:
                if field in project_data:
                    logger.info(f"   📋 Found {field} data: {type(project_data[field])}")
                    
                    # Save detailed schema if found
                    if field in ['movie', 'scenes', 'elements']:
                        schema_file = f'/home/claude-workflow/reference_{field}_schema.json'
                        with open(schema_file, 'w') as f:
                            json.dump(project_data[field], f, indent=2)
                        logger.info(f"   💾 {field.title()} schema saved to reference_{field}_schema.json")
            
            # Look specifically for review elements
            logger.info("🔍 SEARCHING FOR REVIEW ELEMENTS:")
            
            def search_for_reviews(data, path=""):
                """Recursively search for review-related elements"""
                if isinstance(data, dict):
                    for key, value in data.items():
                        current_path = f"{path}.{key}" if path else key
                        
                        # Check for review-related keys
                        if any(term in key.lower() for term in ['star', 'rating', 'review', 'score']):
                            logger.info(f"   ⭐ Found review element: {current_path} = {value}")
                        
                        # Check for review-related text content
                        if isinstance(value, str) and any(term in value.lower() for term in ['★', '⭐', 'stars', 'rating', 'reviews']):
                            logger.info(f"   📊 Found review content: {current_path} = {value}")
                        
                        search_for_reviews(value, current_path)
                        
                elif isinstance(data, list):
                    for i, item in enumerate(data):
                        search_for_reviews(item, f"{path}[{i}]")
            
            search_for_reviews(project_data)
            
            logger.info("✅ Reference project analysis complete")
            logger.info("📋 Check saved files for detailed schema structure")
            
        elif response.status_code == 404:
            logger.warning(f"⚠️ Project {project_id} not found (404)")
            logger.info("💡 This might mean the project is private or the ID is incorrect")
            
        else:
            logger.error(f"❌ API Error: {response.status_code}")
            logger.error(f"   Response: {response.text}")
    
    except Exception as e:
        logger.error(f"❌ Error checking reference project: {str(e)}")

if __name__ == "__main__":
    asyncio.run(check_reference_project_schema())