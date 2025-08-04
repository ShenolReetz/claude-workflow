#!/usr/bin/env python3
"""
Classify Airtable columns by importance and necessity for core workflow
"""

# Core workflow essential fields - MUST be populated for video generation
CORE_ESSENTIAL = [
    # Primary workflow fields
    'ID', 'Title', 'Status',
    
    # Video content - required for video creation
    'VideoTitle', 'VideoTitleStatus', 'VideoDescription', 'VideoDescriptionStatus',
    'VideoScript', 'IntroHook', 'OutroCallToAction',
    
    # Product data - required for Top 5 countdown
    'ProductNo1Title', 'ProductNo1Description', 'ProductNo1Price', 'ProductNo1Rating', 'ProductNo1Reviews',
    'ProductNo2Title', 'ProductNo2Description', 'ProductNo2Price', 'ProductNo2Rating', 'ProductNo2Reviews',
    'ProductNo3Title', 'ProductNo3Description', 'ProductNo3Price', 'ProductNo3Rating', 'ProductNo3Reviews',
    'ProductNo4Title', 'ProductNo4Description', 'ProductNo4Price', 'ProductNo4Rating', 'ProductNo4Reviews',
    'ProductNo5Title', 'ProductNo5Description', 'ProductNo5Price', 'ProductNo5Rating', 'ProductNo5Reviews',
    
    # Audio files - required for video scenes
    'IntroMp3', 'OutroMp3', 'Product1Mp3', 'Product2Mp3', 'Product3Mp3', 'Product4Mp3', 'Product5Mp3',
    
    # Images - required for video scenes
    'IntroPhoto', 'OutroPhoto',
    'ProductNo1Photo', 'ProductNo2Photo', 'ProductNo3Photo', 'ProductNo4Photo', 'ProductNo5Photo',
    
    # Final output
    'JSON2VideoProjectID', 'FinalVideo'
]

# Platform content - important for multi-platform publishing
PLATFORM_IMPORTANT = [
    # YouTube
    'YouTubeTitle', 'YouTubeDescription', 'YouTubeKeywords',
    
    # TikTok
    'TikTokTitle', 'TikTokDescription', 'TikTokCaption', 'TikTokHashtags',
    
    # Instagram
    'InstagramTitle', 'InstagramCaption', 'InstagramHashtags',
    
    # WordPress
    'WordPressTitle', 'WordPressContent', 'WordPressSEO',
    
    # Keywords
    'UniversalKeywords', 'KeyWords'
]

# SEO and optimization - valuable but not essential
SEO_VALUABLE = [
    'SEOScore', 'TitleOptimizationScore', 'KeywordDensity', 'EngagementPrediction',
    'LastOptimizationDate'
]

# Status tracking - operational but not content
STATUS_OPERATIONAL = [
    'ProductNo1TitleStatus', 'ProductNo1DescriptionStatus', 'ProductNo1PhotoStatus',
    'ProductNo2TitleStatus', 'ProductNo2DescriptionStatus', 'ProductNo2PhotoStatus',
    'ProductNo3TitleStatus', 'ProductNo3DescriptionStatus', 'ProductNo3PhotoStatus',
    'ProductNo4TitleStatus', 'ProductNo4DescriptionStatus', 'ProductNo4PhotoStatus',
    'ProductNo5TitleStatus', 'ProductNo5DescriptionStatus', 'ProductNo5PhotoStatus',
    'VideoProductionRDY', 'TextControlStatus', 'ContentValidationStatus',
    'PlatformReadiness'
]

# Quality control and validation - nice to have
QUALITY_CONTROL = [
    'ValidationIssues', 'RegenerationCount', 'GenerationAttempts'
]

# Publishing URLs - only populated after actual publishing
PUBLISHING_URLS = [
    'YouTubeURL', 'TikTokURL'
]

# Affiliate and commercial data - important for monetization
AFFILIATE_IMPORTANT = [
    'ProductNo1AffiliateLink', 'ProductNo2AffiliateLink', 'ProductNo3AffiliateLink',
    'ProductNo4AffiliateLink', 'ProductNo5AffiliateLink'
]

# Image URLs - reference data
IMAGE_REFERENCES = [
    'ProductNo1ImageURL', 'ProductNo2ImageURL', 'ProductNo3ImageURL', 'ProductNo4ImageURL', 'ProductNo5ImageURL',
    'ProductNo1OpenAIImageURL', 'ProductNo2OpenAIImageURL', 'ProductNo3OpenAIImageURL', 
    'ProductNo4OpenAIImageURL', 'ProductNo5OpenAIImageURL'
]

# Optional metadata - truly optional
OPTIONAL_METADATA = [
    'TitleID',  # Legacy field
    'Content Category',  # Linked table reference
    'TikTokVideoID', 'TikTokPublishID', 'TikTokUsername', 'TikTokStatus',  # Publishing metadata
    'TikTokKeywords'  # May be redundant with TikTokHashtags
]

def classify_missing_fields(missing_fields):
    """Classify missing fields by importance"""
    
    classification = {
        'CRITICAL_MISSING': [],
        'IMPORTANT_MISSING': [],
        'VALUABLE_MISSING': [],
        'OPERATIONAL_MISSING': [],
        'OPTIONAL_MISSING': []
    }
    
    for field in missing_fields:
        if field in CORE_ESSENTIAL:
            classification['CRITICAL_MISSING'].append(field)
        elif field in PLATFORM_IMPORTANT or field in AFFILIATE_IMPORTANT:
            classification['IMPORTANT_MISSING'].append(field)
        elif field in SEO_VALUABLE or field in IMAGE_REFERENCES:
            classification['VALUABLE_MISSING'].append(field)
        elif field in STATUS_OPERATIONAL or field in QUALITY_CONTROL or field in PUBLISHING_URLS:
            classification['OPERATIONAL_MISSING'].append(field)
        else:
            classification['OPTIONAL_MISSING'].append(field)
    
    return classification

def analyze_workflow_completeness():
    """Analyze how complete the workflow is for different use cases"""
    
    from column_population_audit import check_field_population
    
    populated, missing = check_field_population()
    classification = classify_missing_fields(missing)
    
    # Calculate coverage by category
    total_core = len(CORE_ESSENTIAL)
    missing_core = len(classification['CRITICAL_MISSING'])
    core_coverage = ((total_core - missing_core) / total_core) * 100
    
    total_platform = len(PLATFORM_IMPORTANT)
    missing_platform = len([f for f in classification['IMPORTANT_MISSING'] if f in PLATFORM_IMPORTANT])
    platform_coverage = ((total_platform - missing_platform) / total_platform) * 100
    
    print("🎯 WORKFLOW COMPLETENESS ANALYSIS")
    print("=" * 50)
    
    print(f"\n🔴 CORE ESSENTIAL FIELDS:")
    print(f"   Coverage: {core_coverage:.1f}% ({total_core - missing_core}/{total_core})")
    if classification['CRITICAL_MISSING']:
        print(f"   Missing critical: {len(classification['CRITICAL_MISSING'])}")
        for field in sorted(classification['CRITICAL_MISSING']):
            print(f"     - {field}")
    else:
        print(f"   ✅ ALL CORE FIELDS COVERED!")
    
    print(f"\n🟠 PLATFORM PUBLISHING:")
    print(f"   Coverage: {platform_coverage:.1f}% ({total_platform - missing_platform}/{total_platform})")
    if missing_platform > 0:
        print(f"   Missing platform fields: {missing_platform}")
    
    print(f"\n🟡 MISSING BY CATEGORY:")
    for category, fields in classification.items():
        if fields:
            print(f"   {category}: {len(fields)}")
            for field in sorted(fields)[:5]:  # Show first 5
                print(f"     - {field}")
            if len(fields) > 5:
                print(f"     ... and {len(fields) - 5} more")
    
    print(f"\n📊 OVERALL ASSESSMENT:")
    if core_coverage >= 95:
        print("   🎉 WORKFLOW IS PRODUCTION READY!")
    elif core_coverage >= 80:
        print("   ✅ WORKFLOW IS MOSTLY COMPLETE")
    elif core_coverage >= 60:
        print("   ⚠️ WORKFLOW NEEDS CRITICAL FIXES")
    else:
        print("   🚨 WORKFLOW IS INCOMPLETE")
    
    return classification

if __name__ == "__main__":
    analyze_workflow_completeness()