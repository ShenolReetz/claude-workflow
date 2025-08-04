#!/usr/bin/env python3
"""
Comprehensive Airtable Column Population Audit
Checks which of the 107 fields are populated by the current workflow
"""

import re

# All 107 Airtable fields from schema
ALL_AIRTABLE_FIELDS = [
    # Primary Fields
    'ID', 'TitleID', 'Title', 'Status',
    
    # Video Content Fields
    'VideoTitle', 'VideoTitleStatus', 'VideoDescription', 'VideoDescriptionStatus',
    'VideoProductionRDY', 'VideoScript', 'IntroHook', 'OutroCallToAction',
    
    # Product Fields (1-5)
    'ProductNo1Title', 'ProductNo1TitleStatus', 'ProductNo1Description', 'ProductNo1DescriptionStatus',
    'ProductNo1Photo', 'ProductNo1PhotoStatus', 'ProductNo1Price', 'ProductNo1Rating', 
    'ProductNo1Reviews', 'ProductNo1AffiliateLink',
    
    'ProductNo2Title', 'ProductNo2TitleStatus', 'ProductNo2Description', 'ProductNo2DescriptionStatus',
    'ProductNo2Photo', 'ProductNo2PhotoStatus', 'ProductNo2Price', 'ProductNo2Rating',
    'ProductNo2Reviews', 'ProductNo2AffiliateLink',
    
    'ProductNo3Title', 'ProductNo3TitleStatus', 'ProductNo3Description', 'ProductNo3DescriptionStatus',
    'ProductNo3Photo', 'ProductNo3PhotoStatus', 'ProductNo3Price', 'ProductNo3Rating',
    'ProductNo3Reviews', 'ProductNo3AffiliateLink',
    
    'ProductNo4Title', 'ProductNo4TitleStatus', 'ProductNo4Description', 'ProductNo4DescriptionStatus',
    'ProductNo4Photo', 'ProductNo4PhotoStatus', 'ProductNo4Price', 'ProductNo4Rating',
    'ProductNo4Reviews', 'ProductNo4AffiliateLink',
    
    'ProductNo5Title', 'ProductNo5TitleStatus', 'ProductNo5Description', 'ProductNo5DescriptionStatus',
    'ProductNo5Photo', 'ProductNo5PhotoStatus', 'ProductNo5Price', 'ProductNo5Rating',
    'ProductNo5Reviews', 'ProductNo5AffiliateLink',
    
    # Audio Fields
    'IntroMp3', 'OutroMp3', 'Product1Mp3', 'Product2Mp3', 'Product3Mp3', 'Product4Mp3', 'Product5Mp3',
    
    # Image Fields
    'IntroPhoto', 'OutroPhoto',
    
    # Platform-Specific Content Fields
    # YouTube
    'YouTubeTitle', 'YouTubeDescription', 'YouTubeKeywords', 'YouTubeURL',
    
    # TikTok
    'TikTokTitle', 'TikTokDescription', 'TikTokKeywords', 'TikTokCaption', 'TikTokHashtags',
    'TikTokURL', 'TikTokVideoID', 'TikTokPublishID', 'TikTokStatus', 'TikTokUsername',
    
    # Instagram
    'InstagramTitle', 'InstagramCaption', 'InstagramHashtags',
    
    # WordPress
    'WordPressTitle', 'WordPressContent', 'WordPressSEO',
    
    # SEO & Keywords
    'UniversalKeywords', 'KeyWords', 'SEOScore', 'TitleOptimizationScore',
    'KeywordDensity', 'EngagementPrediction',
    
    # Validation & Control Fields
    'TextControlStatus', 'ContentValidationStatus', 'ValidationIssues',
    'GenerationAttempts', 'RegenerationCount', 'PlatformReadiness', 'LastOptimizationDate',
    
    # Output Fields
    'FinalVideo', 'JSON2VideoProjectID',
    
    # Additional fields from schema that might be missing
    'ProductNo1OpenAIImageURL', 'ProductNo2OpenAIImageURL', 'ProductNo3OpenAIImageURL', 
    'ProductNo4OpenAIImageURL', 'ProductNo5OpenAIImageURL',
    'ProductNo1ImageURL', 'ProductNo2ImageURL', 'ProductNo3ImageURL', 'ProductNo4ImageURL', 'ProductNo5ImageURL',
    
    # Linked Fields
    'Content Category'
]

def check_field_population():
    """Check which fields are populated across all workflow files"""
    
    import glob
    import os
    
    # Read all workflow files
    workflow_files = [
        '/home/claude-workflow/src/workflow_runner.py',
        '/home/claude-workflow/src/mcp/json2video_agent_mcp.py',
        '/home/claude-workflow/src/mcp/amazon_images_workflow_v2.py',
        '/home/claude-workflow/src/mcp/amazon_guided_image_generation.py',
        '/home/claude-workflow/src/mcp/intro_image_generator.py',
        '/home/claude-workflow/src/mcp/outro_image_generator.py',
        '/home/claude-workflow/mcp_servers/amazon_category_scraper.py'
    ]
    
    workflow_content = ""
    for file_path in workflow_files:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                workflow_content += f.read() + "\n"
    
    populated_fields = set()
    missing_fields = set()
    
    # Check each field
    for field in ALL_AIRTABLE_FIELDS:
        # Look for field name in update statements
        patterns = [
            f"'{field}':",
            f'"{field}":',
            f"['{field}']",
            f'["{field}"]',
            f"update_fields['{field}']",
            f'update_fields["{field}"]',
            f"f'{field}",  # f-string patterns
            f'f"{field}'   # f-string patterns
        ]
        
        found = False
        for pattern in patterns:
            if pattern in workflow_content:
                populated_fields.add(field)
                found = True
                break
        
        if not found:
            missing_fields.add(field)
    
    return populated_fields, missing_fields

def analyze_missing_fields(missing_fields):
    """Analyze missing fields and categorize them"""
    
    analysis = {
        'critical_missing': [],
        'publishing_missing': [],
        'optional_missing': [],
        'status_missing': []
    }
    
    for field in missing_fields:
        if field in ['JSON2VideoProjectID', 'FinalVideo']:
            analysis['critical_missing'].append(field)
        elif 'URL' in field and field != 'ProductNo1ImageURL':  # ProductNoXImageURL are Amazon URLs
            analysis['publishing_missing'].append(field)
        elif 'OpenAIImageURL' in field:
            analysis['optional_missing'].append(field)
        elif 'Status' in field:
            analysis['status_missing'].append(field)
        else:
            analysis['optional_missing'].append(field)
    
    return analysis

if __name__ == "__main__":
    print("🔍 Auditing Airtable Column Population...")
    print(f"📊 Total fields in schema: {len(ALL_AIRTABLE_FIELDS)}")
    
    populated, missing = check_field_population()
    
    print(f"✅ Populated fields: {len(populated)}")
    print(f"❌ Missing fields: {len(missing)}")
    print(f"📈 Coverage: {len(populated)/len(ALL_AIRTABLE_FIELDS)*100:.1f}%")
    
    if missing:
        print(f"\n🚨 MISSING FIELDS ({len(missing)}):")
        analysis = analyze_missing_fields(missing)
        
        if analysis['critical_missing']:
            print(f"\n🔴 CRITICAL MISSING ({len(analysis['critical_missing'])}):")
            for field in sorted(analysis['critical_missing']):
                print(f"  - {field}")
        
        if analysis['publishing_missing']:
            print(f"\n🟠 PUBLISHING MISSING ({len(analysis['publishing_missing'])}):")
            for field in sorted(analysis['publishing_missing']):
                print(f"  - {field}")
        
        if analysis['status_missing']:
            print(f"\n🟡 STATUS MISSING ({len(analysis['status_missing'])}):")
            for field in sorted(analysis['status_missing']):
                print(f"  - {field}")
        
        if analysis['optional_missing']:
            print(f"\n🔵 OPTIONAL MISSING ({len(analysis['optional_missing'])}):")
            for field in sorted(analysis['optional_missing']):
                print(f"  - {field}")
    
    print(f"\n✅ POPULATED FIELDS ({len(populated)}):")
    for field in sorted(populated):
        print(f"  - {field}")