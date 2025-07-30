#!/usr/bin/env python3
"""
🟣 Airtable Specialist Expert Agent
Professional Airtable data management and column expertise
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Airtable Schema Definition - Complete column mapping
AIRTABLE_COLUMNS = {
    # Core Record Fields
    'ID': {'type': 'number', 'description': 'Sequential record identifier (1-4188)', 'required': True},
    'Title': {'type': 'text', 'description': 'Original product category title', 'required': True},
    'Status': {'type': 'select', 'options': ['Pending', 'Processing', 'Completed', 'Failed'], 'description': 'Processing status'},
    
    # Video Content Fields
    'VideoTitle': {'type': 'text', 'description': 'Generated video title for platforms', 'max_length': 100},
    'VideoDescription': {'type': 'long_text', 'description': 'Generated video description', 'max_length': 5000},
    'VideoURL': {'type': 'url', 'description': 'Generated video URL from JSON2Video'},
    'JSON2VideoProjectID': {'type': 'text', 'description': 'JSON2Video project identifier'},
    'VideoStatus': {'type': 'select', 'options': ['Pending', 'Generated', 'Processing', 'Ready', 'Failed']},
    'VideoDuration': {'type': 'text', 'description': 'Video duration (e.g., "55 seconds")'},
    'VideoResolution': {'type': 'text', 'description': 'Video resolution (e.g., "1080x1920")'},
    'VideoFormat': {'type': 'text', 'description': 'Video format (e.g., "MP4")'},
    
    # Product Data Fields (Top 5 Products from Amazon Scraping)
    'ProductNo1Title': {'type': 'text', 'description': 'Product 1 title (Winner - highest rated)', 'max_length': 200},
    'ProductNo1Photo': {'type': 'url', 'description': 'Product 1 image URL from Amazon'},
    'ProductNo1Rating': {'type': 'number', 'description': 'Product 1 star rating (0-5)', 'format': 'decimal'},
    'ProductNo1Reviews': {'type': 'number', 'description': 'Product 1 review count', 'format': 'integer'},
    'ProductNo1Price': {'type': 'currency', 'description': 'Product 1 price in USD'},
    'ProductNo1AffiliateLink': {'type': 'url', 'description': 'Product 1 Amazon affiliate link'},
    'ProductNo1ASIN': {'type': 'text', 'description': 'Product 1 Amazon ASIN identifier'},
    
    'ProductNo2Title': {'type': 'text', 'description': 'Product 2 title (2nd highest rated)', 'max_length': 200},
    'ProductNo2Photo': {'type': 'url', 'description': 'Product 2 image URL from Amazon'},
    'ProductNo2Rating': {'type': 'number', 'description': 'Product 2 star rating (0-5)', 'format': 'decimal'},
    'ProductNo2Reviews': {'type': 'number', 'description': 'Product 2 review count', 'format': 'integer'},
    'ProductNo2Price': {'type': 'currency', 'description': 'Product 2 price in USD'},
    'ProductNo2AffiliateLink': {'type': 'url', 'description': 'Product 2 Amazon affiliate link'},
    'ProductNo2ASIN': {'type': 'text', 'description': 'Product 2 Amazon ASIN identifier'},
    
    'ProductNo3Title': {'type': 'text', 'description': 'Product 3 title (3rd highest rated)', 'max_length': 200},
    'ProductNo3Photo': {'type': 'url', 'description': 'Product 3 image URL from Amazon'},
    'ProductNo3Rating': {'type': 'number', 'description': 'Product 3 star rating (0-5)', 'format': 'decimal'},
    'ProductNo3Reviews': {'type': 'number', 'description': 'Product 3 review count', 'format': 'integer'},
    'ProductNo3Price': {'type': 'currency', 'description': 'Product 3 price in USD'},
    'ProductNo3AffiliateLink': {'type': 'url', 'description': 'Product 3 Amazon affiliate link'},
    'ProductNo3ASIN': {'type': 'text', 'description': 'Product 3 Amazon ASIN identifier'},
    
    'ProductNo4Title': {'type': 'text', 'description': 'Product 4 title (4th highest rated)', 'max_length': 200},
    'ProductNo4Photo': {'type': 'url', 'description': 'Product 4 image URL from Amazon'},
    'ProductNo4Rating': {'type': 'number', 'description': 'Product 4 star rating (0-5)', 'format': 'decimal'},
    'ProductNo4Reviews': {'type': 'number', 'description': 'Product 4 review count', 'format': 'integer'},
    'ProductNo4Price': {'type': 'currency', 'description': 'Product 4 price in USD'},
    'ProductNo4AffiliateLink': {'type': 'url', 'description': 'Product 4 Amazon affiliate link'},
    'ProductNo4ASIN': {'type': 'text', 'description': 'Product 4 Amazon ASIN identifier'},
    
    'ProductNo5Title': {'type': 'text', 'description': 'Product 5 title (5th highest rated)', 'max_length': 200},
    'ProductNo5Photo': {'type': 'url', 'description': 'Product 5 image URL from Amazon'},
    'ProductNo5Rating': {'type': 'number', 'description': 'Product 5 star rating (0-5)', 'format': 'decimal'},
    'ProductNo5Reviews': {'type': 'number', 'description': 'Product 5 review count', 'format': 'integer'},
    'ProductNo5Price': {'type': 'currency', 'description': 'Product 5 price in USD'},
    'ProductNo5AffiliateLink': {'type': 'url', 'description': 'Product 5 Amazon affiliate link'},
    'ProductNo5ASIN': {'type': 'text', 'description': 'Product 5 Amazon ASIN identifier'},
    
    # Text-to-Speech Validation Status Fields
    'VideoTitleStatus': {'type': 'select', 'options': ['Ready', 'Pending'], 'description': 'Video title TTS validation (5-second limit)'},
    'VideoDescriptionStatus': {'type': 'select', 'options': ['Ready', 'Pending'], 'description': 'Video description TTS validation (5-second limit)'},
    'ProductNo1TitleStatus': {'type': 'select', 'options': ['Ready', 'Pending'], 'description': 'Product 1 title TTS validation (9-second limit)'},
    'ProductNo1DescriptionStatus': {'type': 'select', 'options': ['Ready', 'Pending'], 'description': 'Product 1 description TTS validation (9-second limit)'},
    'ProductNo2TitleStatus': {'type': 'select', 'options': ['Ready', 'Pending'], 'description': 'Product 2 title TTS validation (9-second limit)'},
    'ProductNo2DescriptionStatus': {'type': 'select', 'options': ['Ready', 'Pending'], 'description': 'Product 2 description TTS validation (9-second limit)'},
    'ProductNo3TitleStatus': {'type': 'select', 'options': ['Ready', 'Pending'], 'description': 'Product 3 title TTS validation (9-second limit)'},
    'ProductNo3DescriptionStatus': {'type': 'select', 'options': ['Ready', 'Pending'], 'description': 'Product 3 description TTS validation (9-second limit)'},
    'ProductNo4TitleStatus': {'type': 'select', 'options': ['Ready', 'Pending'], 'description': 'Product 4 title TTS validation (9-second limit)'},
    'ProductNo4DescriptionStatus': {'type': 'select', 'options': ['Ready', 'Pending'], 'description': 'Product 4 description TTS validation (9-second limit)'},
    'ProductNo5TitleStatus': {'type': 'select', 'options': ['Ready', 'Pending'], 'description': 'Product 5 title TTS validation (9-second limit)'},
    'ProductNo5DescriptionStatus': {'type': 'select', 'options': ['Ready', 'Pending'], 'description': 'Product 5 description TTS validation (9-second limit)'},
    
    # Platform-Specific Content Fields
    'YouTubeTitle': {'type': 'text', 'description': 'YouTube-optimized title', 'max_length': 100},
    'YouTubeDescription': {'type': 'long_text', 'description': 'YouTube-optimized description with affiliate links'},
    'YouTubeKeywords': {'type': 'text', 'description': 'YouTube SEO keywords (comma-separated)'},
    'YouTubeStatus': {'type': 'select', 'options': ['Pending', 'Uploaded', 'Published', 'Failed']},
    
    'InstagramTitle': {'type': 'text', 'description': 'Instagram-optimized title', 'max_length': 100},
    'InstagramDescription': {'type': 'long_text', 'description': 'Instagram-optimized description with hashtags'},
    'InstagramHashtags': {'type': 'text', 'description': 'Instagram hashtags (comma-separated)'},
    'InstagramStatus': {'type': 'select', 'options': ['Pending', 'Uploaded', 'Published', 'Failed']},
    
    'TikTokTitle': {'type': 'text', 'description': 'TikTok-optimized title', 'max_length': 100},
    'TikTokDescription': {'type': 'long_text', 'description': 'TikTok-optimized description with hashtags'},
    'TikTokHashtags': {'type': 'text', 'description': 'TikTok hashtags (comma-separated)'},
    'TikTokStatus': {'type': 'select', 'options': ['Pending', 'Uploaded', 'Published', 'Failed']},
    
    'WordPressTitle': {'type': 'text', 'description': 'WordPress blog post title', 'max_length': 100},
    'WordPressContent': {'type': 'long_text', 'description': 'WordPress blog post content with affiliate links'},
    'WordPressKeywords': {'type': 'text', 'description': 'WordPress SEO keywords (comma-separated)'},
    'WordPressStatus': {'type': 'select', 'options': ['Pending', 'Published', 'Draft', 'Failed']},
    
    # Image and Media Fields
    'IntroPhoto': {'type': 'url', 'description': 'Generated intro image URL'},
    'OutroPhoto': {'type': 'url', 'description': 'Generated outro image URL'},
    'IntroVoiceURL': {'type': 'url', 'description': 'Intro voice narration URL'},
    'OutroVoiceURL': {'type': 'url', 'description': 'Outro voice narration URL'},
    
    # Google Drive Integration
    'GoogleDriveAudioIntegrated': {'type': 'checkbox', 'description': 'Google Drive audio files integrated'},
    'AudioFilesCount': {'type': 'number', 'description': 'Number of audio files integrated'},
    
    # Processing Metadata
    'ProcessedAt': {'type': 'datetime', 'description': 'When record was last processed'},
    'ProcessingDuration': {'type': 'text', 'description': 'Total processing time'},
    'ErrorLog': {'type': 'long_text', 'description': 'Error messages and debugging info'},
    'ScrapingTimestamp': {'type': 'datetime', 'description': 'When products were scraped from Amazon'},
    'ScrapingSource': {'type': 'text', 'description': 'Amazon search query used for scraping'}
}

async def execute_task(task_type, task_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute Airtable specialist task with professional data management
    
    🟣 Expert Agent: Airtable Specialist Expert
    📋 Specialization: Complete Airtable data management and column expertise
    🎯 Features: Schema validation, data type conversion, professional reporting
    """
    
    logger.info("🟣 Airtable Specialist Expert: Starting data management task")
    start_time = datetime.now()
    
    try:
        task_action = task_data.get('action', 'get_column_info')
        
        if task_action == 'get_column_info':
            return await _get_column_information(task_data, config)
        elif task_action == 'save_scraped_products':
            return await _save_scraped_products(task_data, config)
        elif task_action == 'get_record_data':
            return await _get_record_data(task_data, config)
        elif task_action == 'update_record':
            return await _update_record(task_data, config)
        elif task_action == 'validate_data':
            return await _validate_data_types(task_data, config)
        else:
            return {
                "success": False,
                "error": f"Unknown action: {task_action}",
                "agent": "airtable-specialist"
            }
        
    except Exception as e:
        logger.error(f"❌ Airtable Specialist Expert failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "agent": "airtable-specialist",
            "category": "🟣 Support",
            "duration": (datetime.now() - start_time).total_seconds()
        }

async def _get_column_information(task_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """Provide comprehensive column information"""
    
    logger.info("📊 Providing complete Airtable schema information")
    
    # Categorize columns for better organization
    column_categories = {
        'Core Fields': ['ID', 'Title', 'Status'],
        'Video Content': ['VideoTitle', 'VideoDescription', 'VideoURL', 'JSON2VideoProjectID', 'VideoStatus', 'VideoDuration', 'VideoResolution', 'VideoFormat'],
        'Product Data (Product 1-5)': [col for col in AIRTABLE_COLUMNS.keys() if col.startswith('ProductNo') and not col.endswith('Status')],
        'TTS Validation Status': [col for col in AIRTABLE_COLUMNS.keys() if col.endswith('Status') and ('Title' in col or 'Description' in col)],
        'Platform Content': [col for col in AIRTABLE_COLUMNS.keys() if any(platform in col for platform in ['YouTube', 'Instagram', 'TikTok', 'WordPress'])],
        'Media Files': ['IntroPhoto', 'OutroPhoto', 'IntroVoiceURL', 'OutroVoiceURL', 'GoogleDriveAudioIntegrated', 'AudioFilesCount'],
        'Processing Metadata': ['ProcessedAt', 'ProcessingDuration', 'ErrorLog', 'ScrapingTimestamp', 'ScrapingSource']
    }
    
    return {
        "success": True,
        "agent": "airtable-specialist",
        "category": "🟣 Support", 
        "specialization": "Complete Airtable data management and column expertise",
        "total_columns": len(AIRTABLE_COLUMNS),
        "column_categories": column_categories,
        "complete_schema": AIRTABLE_COLUMNS,
        "key_insights": {
            "product_fields_per_product": 7,  # Title, Photo, Rating, Reviews, Price, AffiliateLink, ASIN
            "total_product_fields": 35,  # 7 fields × 5 products
            "tts_validation_fields": 12,  # VideoTitle/Description + 5 products × 2 fields each
            "platform_count": 4,  # YouTube, Instagram, TikTok, WordPress
            "required_for_video": ["ProductNo1Title", "ProductNo1Photo", "ProductNo1Rating", "ProductNo1Reviews", "ProductNo1Price"]
        },
        "data_flow": {
            "step_1": "Amazon Scraping Specialist scrapes top 5 products",
            "step_2": "Airtable Specialist saves scraped product data",
            "step_3": "Content generation uses saved product data",
            "step_4": "Video creation uses complete product information"
        },
        "timestamp": datetime.now().isoformat()
    }

async def _save_scraped_products(task_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """Save scraped Amazon products to Airtable record"""
    
    logger.info("💾 Saving scraped Amazon products to Airtable")
    
    record_id = task_data.get('record_id')
    scraped_products = task_data.get('scraped_products', [])
    
    if not record_id or not scraped_products:
        return {
            "success": False,
            "error": "Missing record_id or scraped_products data",
            "agent": "airtable-specialist"
        }
    
    # Validate we have exactly 5 products (top 5 countdown)
    if len(scraped_products) != 5:
        return {
            "success": False,
            "error": f"Expected 5 products for top 5 countdown, got {len(scraped_products)}",
            "agent": "airtable-specialist"
        }
    
    # Import Test Airtable server
    import sys
    sys.path.append('/home/claude-workflow')
    from mcp_servers.Test_airtable_server import TestAirtableMCPServer as AirtableMCPServer
    
    airtable_server = AirtableMCPServer(
        api_key=config.get('airtable_api_key'),
        base_id=config.get('airtable_base_id'),
        table_name=config.get('airtable_table_name')
    )
    
    # Prepare update data - map scraped products to Airtable fields
    update_data = {
        'ScrapingTimestamp': datetime.now().isoformat(),
        'ScrapingSource': task_data.get('search_query', 'Unknown')
    }
    
    # Map each product (sorted by rating descending, so index 0 = highest rated = ProductNo1)
    for i, product in enumerate(scraped_products, 1):
        product_prefix = f'ProductNo{i}'
        
        update_data.update({
            f'{product_prefix}Title': product.get('title', f'Product {i}'),
            f'{product_prefix}Photo': product.get('image_url', ''),
            f'{product_prefix}Rating': float(product.get('rating', 0)),
            f'{product_prefix}Reviews': int(product.get('review_count', 0)),
            f'{product_prefix}Price': product.get('price', 0),
            f'{product_prefix}AffiliateLink': product.get('affiliate_link', ''),
            f'{product_prefix}ASIN': product.get('asin', ''),
            # Set TTS status to Pending for new products
            f'{product_prefix}TitleStatus': 'Pending',
            f'{product_prefix}DescriptionStatus': 'Pending'
        })
    
    # Update the record
    try:
        result = await airtable_server.update_record(record_id, update_data)
        
        if result.get('success'):
            logger.info(f"✅ Successfully saved 5 scraped products to record {record_id}")
            return {
                "success": True,
                "agent": "airtable-specialist",
                "category": "🟣 Support",
                "action": "save_scraped_products",
                "record_id": record_id,
                "products_saved": 5,
                "fields_updated": len(update_data),
                "product_data": {
                    f"Product {i}": {
                        "title": product.get('title'),
                        "rating": product.get('rating'),
                        "reviews": product.get('review_count'),
                        "price": product.get('price')
                    } for i, product in enumerate(scraped_products, 1)
                },
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "error": result.get('error', 'Unknown Airtable update error'),
                "agent": "airtable-specialist"
            }
            
    except Exception as e:
        logger.error(f"❌ Failed to save scraped products: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "agent": "airtable-specialist"
        }

async def _get_record_data(task_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """Get complete record data with professional formatting"""
    
    record_id = task_data.get('record_id')
    if not record_id:
        return {
            "success": False,
            "error": "Missing record_id parameter",
            "agent": "airtable-specialist"
        }
    
    # Import Airtable server
    import sys
    sys.path.append('/home/claude-workflow')  
    from mcp_servers.airtable_server import AirtableMCPServer
    
    airtable_server = AirtableMCPServer(
        api_key=config.get('airtable_api_key'),
        base_id=config.get('airtable_base_id'),
        table_name=config.get('airtable_table_name')
    )
    
    try:
        record_data = await airtable_server.get_record_by_id(record_id)
        
        if record_data:
            # Professional data formatting and validation
            formatted_data = _format_record_data_professionally(record_data)
            
            return {
                "success": True,
                "agent": "airtable-specialist",
                "category": "🟣 Support",
                "action": "get_record_data",
                "record_id": record_id,
                "record_data": formatted_data,
                "data_quality": _assess_data_quality(record_data),
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "error": f"Record {record_id} not found",
                "agent": "airtable-specialist"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "agent": "airtable-specialist"
        }

async def _update_record(task_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """Update record with data validation and professional handling"""
    
    record_id = task_data.get('record_id')
    update_data = task_data.get('update_data', {})
    
    if not record_id or not update_data:
        return {
            "success": False,
            "error": "Missing record_id or update_data",
            "agent": "airtable-specialist"
        }
    
    # Validate data types before updating
    validated_data = _validate_and_convert_data(update_data)
    
    # Import Test Airtable server
    import sys
    sys.path.append('/home/claude-workflow')
    from mcp_servers.Test_airtable_server import TestAirtableMCPServer as AirtableMCPServer
    
    airtable_server = AirtableMCPServer(
        api_key=config.get('airtable_api_key'),
        base_id=config.get('airtable_base_id'),
        table_name=config.get('airtable_table_name')
    )
    
    try:
        result = await airtable_server.update_record(record_id, validated_data)
        
        return {
            "success": result.get('success', False),
            "agent": "airtable-specialist",
            "category": "🟣 Support",
            "action": "update_record",
            "record_id": record_id,
            "fields_updated": len(validated_data),
            "validation_applied": True,
            "error": result.get('error') if not result.get('success') else None,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "agent": "airtable-specialist"
        }

async def _validate_data_types(task_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate data types against Airtable schema"""
    
    data_to_validate = task_data.get('data', {})
    validation_results = {}
    
    for field_name, value in data_to_validate.items():
        if field_name in AIRTABLE_COLUMNS:
            field_schema = AIRTABLE_COLUMNS[field_name]
            validation_results[field_name] = _validate_field_value(value, field_schema)
        else:
            validation_results[field_name] = {
                'valid': False,
                'error': 'Field not found in schema',
                'suggestion': 'Check field name spelling'
            }
    
    return {
        "success": True,
        "agent": "airtable-specialist",
        "category": "🟣 Support",
        "action": "validate_data",
        "validation_results": validation_results,
        "total_fields_checked": len(validation_results),
        "valid_fields": sum(1 for r in validation_results.values() if r.get('valid')),
        "timestamp": datetime.now().isoformat()
    }

def _format_record_data_professionally(record_data: Dict) -> Dict:
    """Format record data with professional structure"""
    
    formatted = {
        'core_info': {},
        'video_content': {},
        'products': {},
        'platform_content': {},
        'media_files': {},
        'processing_status': {}
    }
    
    # Categorize fields for better organization
    for field_name, value in record_data.items():
        if field_name in ['ID', 'Title', 'Status']:
            formatted['core_info'][field_name] = value
        elif field_name.startswith('Video'):
            formatted['video_content'][field_name] = value
        elif field_name.startswith('ProductNo'):
            # Group by product number
            product_num = field_name[9]  # Extract number from ProductNo1Title, etc.
            if product_num not in formatted['products']:
                formatted['products'][product_num] = {}
            field_type = field_name[10:]  # Remove ProductNo1 prefix
            formatted['products'][product_num][field_type] = value
        elif any(platform in field_name for platform in ['YouTube', 'Instagram', 'TikTok', 'WordPress']):
            formatted['platform_content'][field_name] = value
        elif field_name in ['IntroPhoto', 'OutroPhoto', 'IntroVoiceURL', 'OutroVoiceURL', 'GoogleDriveAudioIntegrated', 'AudioFilesCount']:
            formatted['media_files'][field_name] = value
        else:
            formatted['processing_status'][field_name] = value
    
    return formatted

def _assess_data_quality(record_data: Dict) -> Dict:
    """Assess the quality and completeness of record data"""
    
    quality_score = 0
    max_score = 100
    issues = []
    
    # Check core fields (20 points)
    if record_data.get('ID'):
        quality_score += 10
    else:
        issues.append("Missing ID field")
    
    if record_data.get('Title'):
        quality_score += 10
    else:
        issues.append("Missing Title field")
    
    # Check product data completeness (50 points - 10 per product)
    for i in range(1, 6):
        product_score = 0
        required_fields = ['Title', 'Photo', 'Rating', 'Reviews', 'Price']
        
        for field in required_fields:
            field_name = f'ProductNo{i}{field}'
            if record_data.get(field_name):
                product_score += 2
            else:
                issues.append(f"Missing {field_name}")
        
        quality_score += product_score
    
    # Check video content (20 points)
    if record_data.get('VideoTitle'):
        quality_score += 10
    else:
        issues.append("Missing VideoTitle")
        
    if record_data.get('VideoURL'):
        quality_score += 10
    else:
        issues.append("Missing VideoURL")
    
    # Check platform content (10 points)
    platform_fields = ['YouTubeTitle', 'InstagramTitle', 'TikTokTitle', 'WordPressTitle']
    platform_score = sum(2.5 for field in platform_fields if record_data.get(field))
    quality_score += platform_score
    
    return {
        'quality_score': min(quality_score, max_score),
        'grade': _get_quality_grade(quality_score),
        'completeness': f"{quality_score:.1f}%",
        'issues': issues,
        'recommendations': _get_quality_recommendations(issues)
    }

def _get_quality_grade(score: float) -> str:
    """Convert quality score to letter grade"""
    if score >= 90:
        return "A+ (Excellent)"
    elif score >= 80:
        return "A (Very Good)"
    elif score >= 70:
        return "B (Good)"
    elif score >= 60:
        return "C (Fair)"
    elif score >= 50:
        return "D (Poor)"
    else:
        return "F (Incomplete)"

def _get_quality_recommendations(issues: List[str]) -> List[str]:
    """Generate recommendations based on data quality issues"""
    
    recommendations = []
    
    if any("ProductNo" in issue for issue in issues):
        recommendations.append("Run Amazon Scraping Specialist to populate missing product data")
    
    if any("Video" in issue for issue in issues):
        recommendations.append("Complete video generation process")
    
    if any("platform" in issue.lower() for issue in issues):
        recommendations.append("Generate platform-specific content")
    
    if not recommendations:
        recommendations.append("Data quality is excellent - ready for processing")
    
    return recommendations

def _validate_and_convert_data(data: Dict) -> Dict:
    """Validate and convert data types according to schema"""
    
    validated_data = {}
    
    for field_name, value in data.items():
        if field_name in AIRTABLE_COLUMNS:
            field_schema = AIRTABLE_COLUMNS[field_name]
            validated_value = _convert_value_to_type(value, field_schema)
            validated_data[field_name] = validated_value
        else:
            # Unknown field - pass through but log warning
            logger.warning(f"⚠️ Unknown field: {field_name}")
            validated_data[field_name] = value
    
    return validated_data

def _validate_field_value(value, field_schema: Dict) -> Dict:
    """Validate a single field value against its schema"""
    
    field_type = field_schema.get('type')
    
    try:
        if field_type == 'number':
            float(value)
            return {'valid': True, 'converted_value': float(value)}
        elif field_type == 'currency':
            # Remove currency symbols and convert to float
            clean_value = str(value).replace('$', '').replace(',', '')
            float(clean_value)
            return {'valid': True, 'converted_value': float(clean_value)}
        elif field_type == 'url':
            if str(value).startswith(('http://', 'https://')):
                return {'valid': True, 'converted_value': str(value)}
            else:
                return {'valid': False, 'error': 'URL must start with http:// or https://'}
        elif field_type == 'select':
            options = field_schema.get('options', [])
            if value in options:
                return {'valid': True, 'converted_value': value}
            else:
                return {'valid': False, 'error': f'Value must be one of: {options}'}
        elif field_type in ['text', 'long_text']:
            max_length = field_schema.get('max_length')
            if max_length and len(str(value)) > max_length:
                return {'valid': False, 'error': f'Text too long (max {max_length} chars)'}
            return {'valid': True, 'converted_value': str(value)}
        else:
            return {'valid': True, 'converted_value': value}
            
    except (ValueError, TypeError) as e:
        return {'valid': False, 'error': str(e)}

def _convert_value_to_type(value, field_schema: Dict):
    """Convert value to appropriate type based on schema"""
    
    field_type = field_schema.get('type')
    
    try:
        if field_type == 'number':
            return float(value) if value is not None else None
        elif field_type == 'currency':
            if value is None:
                return None
            clean_value = str(value).replace('$', '').replace(',', '')
            return float(clean_value)
        elif field_type in ['text', 'long_text', 'url']:
            return str(value) if value is not None else None
        elif field_type == 'checkbox':
            return bool(value) if value is not None else False
        else:
            return value
    except (ValueError, TypeError):
        logger.warning(f"⚠️ Could not convert value {value} to type {field_type}")
        return value