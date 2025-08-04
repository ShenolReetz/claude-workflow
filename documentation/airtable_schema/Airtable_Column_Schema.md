# Airtable Column Schema Documentation

**Table Name:** Video Titles  
**Base ID:** From config/api_keys.json  
**Last Updated:** August 3, 2025  
**Total Fields:** 107

## 📊 Complete Field Schema

### 🔑 Primary Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `ID` | number (precision: 1) | Sequential ID for workflow processing |
| `TitleID` | number (precision: 1) | Original title identifier |
| `Title` | singleLineText | Original title from source |
| `Status` | singleSelect | Workflow status: `Pending`, `Completed`, `In Progress`, `Processing`, `Skiped`, `NotUsed` |

### 🎬 Video Content Fields

| Field Name | Type | Status Field | Status Options |
|------------|------|--------------|----------------|
| `VideoTitle` | multilineText | `VideoTitleStatus` | `Pending`, `Ready` |
| `VideoDescription` | richText | `VideoDescriptionStatus` | `Pending`, `Ready` |
| `VideoProductionRDY` | singleSelect | - | `Pending`, `Ready` |
| `VideoScript` | multilineText | - | - |
| `IntroHook` | multilineText | - | - |
| `OutroCallToAction` | multilineText | - | - |

### 📦 Product Fields (1-5)

#### Product 1
| Field Name | Type | Status Field | Status Options |
|------------|------|--------------|----------------|
| `ProductNo1Title` | singleLineText | `ProductNo1TitleStatus` | `Pending`, `Ready` |
| `ProductNo1Description` | richText | `ProductNo1DescriptionStatus` | `Pending`, `Ready` |
| `ProductNo1Photo` | url | `ProductNo1PhotoStatus` | `Pending`, `Ready` |
| `ProductNo1Price` | number (precision: 1) | - | - |
| `ProductNo1Rating` | number (precision: 1) | - | - |
| `ProductNo1Reviews` | number (precision: 1) | - | - |
| `ProductNo1AffiliateLink` | url | - | - |

#### Product 2
| Field Name | Type | Status Field | Status Options |
|------------|------|--------------|----------------|
| `ProductNo2Title` | singleLineText | `ProductNo2TitleStatus` | `Pending`, `Ready` |
| `ProductNo2Description` | richText | `ProductNo2DescriptionStatus` | `Pending`, `Ready` |
| `ProductNo2Photo` | url | `ProductNo2PhotoStatus` | `Pending`, `Ready` |
| `ProductNo2Price` | number (precision: 1) | - | - |
| `ProductNo2Rating` | number (precision: 1) | - | - |
| `ProductNo2Reviews` | number (precision: 1) | - | - |
| `ProductNo2AffiliateLink` | url | - | - |

#### Product 3
| Field Name | Type | Status Field | Status Options |
|------------|------|--------------|----------------|
| `ProductNo3Title` | singleLineText | `ProductNo3TitleStatus` | `Pending`, `Ready` |
| `ProductNo3Description` | richText | `ProductNo3DescriptionStatus` | `Pending`, `Ready` |
| `ProductNo3Photo` | url | `ProductNo3PhotoStatus` | `Pending`, `Ready` |
| `ProductNo3Price` | number (precision: 1) | - | - |
| `ProductNo3Rating` | number (precision: 1) | - | - |
| `ProductNo3Reviews` | number (precision: 1) | - | - |
| `ProductNo3AffiliateLink` | url | - | - |

#### Product 4
| Field Name | Type | Status Field | Status Options |
|------------|------|--------------|----------------|
| `ProductNo4Title` | singleLineText | `ProductNo4TitleStatus` | `Pending`, `Ready` |
| `ProductNo4Description` | richText | `ProductNo4DescriptionStatus` | `Pending`, `Ready` |
| `ProductNo4Photo` | url | `ProductNo4PhotoStatus` | `Pending`, `Ready` |
| `ProductNo4Price` | number (precision: 1) | - | - |
| `ProductNo4Rating` | number (precision: 1) | - | - |
| `ProductNo4Reviews` | number (precision: 1) | - | - |
| `ProductNo4AffiliateLink` | url | - | - |

#### Product 5
| Field Name | Type | Status Field | Status Options |
|------------|------|--------------|----------------|
| `ProductNo5Title` | singleLineText | `ProductNo5TitleStatus` | `Pending`, `Ready` |
| `ProductNo5Description` | richText | `ProductNo5DescriptionStatus` | `Pending`, `Ready` |
| `ProductNo5Photo` | url | `ProductNo5PhotoStatus` | `Pending`, `Ready` |
| `ProductNo5Price` | number (precision: 1) | - | - |
| `ProductNo5Rating` | number (precision: 1) | - | - |
| `ProductNo5Reviews` | number (precision: 1) | - | - |
| `ProductNo5AffiliateLink` | url | - | - |

### 🎵 Audio Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `IntroMp3` | url | Intro audio file URL |
| `OutroMp3` | url | Outro audio file URL |
| `Product1Mp3` | url | Product 1 audio narration |
| `Product2Mp3` | url | Product 2 audio narration |
| `Product3Mp3` | url | Product 3 audio narration |
| `Product4Mp3` | url | Product 4 audio narration |
| `Product5Mp3` | url | Product 5 audio narration |

### 🖼️ Image Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `IntroPhoto` | url | Intro scene image |
| `OutroPhoto` | url | Outro scene image |

### 📱 Platform-Specific Content Fields

#### YouTube
| Field Name | Type | Description |
|------------|------|-------------|
| `YouTubeTitle` | singleLineText | Optimized YouTube title |
| `YouTubeDescription` | multilineText | YouTube description with SEO |
| `YouTubeKeywords` | multilineText | YouTube tags/keywords |
| `YouTubeURL` | url | Published YouTube video URL |

#### TikTok
| Field Name | Type | Description |
|------------|------|-------------|
| `TikTokTitle` | singleLineText | TikTok video title |
| `TikTokDescription` | multilineText | TikTok caption |
| `TikTokKeywords` | multilineText | TikTok hashtags |
| `TikTokCaption` | multilineText | Full TikTok caption |
| `TikTokHashtags` | multilineText | TikTok hashtag list |
| `TikTokURL` | url | Published TikTok URL |
| `TikTokVideoID` | singleLineText | TikTok video identifier |
| `TikTokPublishID` | singleLineText | TikTok publish ID |
| `TikTokStatus` | singleSelect | `PROCESSING`, `PUBLISHED`, `FAILED` |
| `TikTokUsername` | singleLineText | TikTok account username |

#### Instagram
| Field Name | Type | Description |
|------------|------|-------------|
| `InstagramTitle` | singleLineText | Instagram post title |
| `InstagramCaption` | multilineText | Instagram caption |
| `InstagramHashtags` | multilineText | Instagram hashtags |

#### WordPress
| Field Name | Type | Description |
|------------|------|-------------|
| `WordPressTitle` | singleLineText | Blog post title |
| `WordPressContent` | multilineText | Full blog content |
| `WordPressSEO` | multilineText | SEO keywords for WordPress |

### 🔍 SEO & Keywords

| Field Name | Type | Description |
|------------|------|-------------|
| `UniversalKeywords` | multilineText | Keywords for all platforms |
| `KeyWords` | multilineText | General keywords |
| `SEOScore` | number (precision: 1) | SEO optimization score |
| `TitleOptimizationScore` | number (precision: 1) | Title quality score |
| `KeywordDensity` | number (precision: 1) | Keyword density percentage |
| `EngagementPrediction` | number (precision: 1) | Predicted engagement score |

### ✅ Validation & Control Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `TextControlStatus` | multilineText | Text validation status |
| `ContentValidationStatus` | singleSelect | `Draft`, `Validated`, `Failed`, `Regenerating` |
| `ValidationIssues` | multilineText | Validation error details |
| `GenerationAttempts` | number (precision: 1) | Number of generation attempts |
| `RegenerationCount` | number (precision: 1) | Number of regenerations |
| `PlatformReadiness` | multipleSelects | Which platforms are ready |
| `LastOptimizationDate` | date | Last optimization date |

### 🎬 Output Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `FinalVideo` | url | Final video URL |
| `JSON2VideoProjectID` | singleLineText | JSON2Video project identifier |

### 🔗 Linked Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `Content Category` | multipleRecordLinks | Link to Content Categories table |

## 🚨 Critical Implementation Notes

### Status Field Behavior
1. **ALL Status fields MUST be set to `"Ready"`** when their corresponding content field is populated
2. **Status fields are `singleSelect` type** - they only accept predefined values
3. **Valid Status Values:** `"Pending"` or `"Ready"` (case-sensitive)
4. **Video generation will fail** if any required status field is not `"Ready"`

### Product Field Requirements
1. **All 5 products MUST have Title fields populated** for video generation
2. **ProductNoXTitle** fields are `singleLineText` (not multiline)
3. **ProductNoXDescription** fields are `richText` format
4. **Price, Rating, Reviews** fields are numeric with precision 1

### Workflow Dependencies
```
Title Selection (ID field) 
    ↓
Product Research (validates min 5 products exist)
    ↓
Content Generation (populates Title/Description fields)
    ↓
Status Update (sets all Status fields to "Ready")
    ↓
Video Generation (requires all ProductNoXTitle fields)
```

### Common Pitfalls to Avoid
1. ❌ Don't assume field names - use exact names from schema
2. ❌ Don't forget to set Status fields to "Ready"
3. ❌ Don't use "Approved" or other values - only "Ready" or "Pending"
4. ❌ Don't skip product titles - video generation checks for them
5. ❌ Don't mix field types - respect singleLineText vs multilineText

## 📡 API Access Methods

### Method 1: Metadata API (Recommended)
```python
url = f"https://api.airtable.com/v0/meta/bases/{base_id}/tables"
# Returns complete schema with field types and options
```

### Method 2: Record Inference
```python
url = f"https://api.airtable.com/v0/{base_id}/Video%20Titles"
# Query records and infer types from data
```

## 🔄 Schema Validation Script

Use the `airtable_schema_inspector.py` script to verify the current schema:
```bash
python3 airtable_schema_inspector.py
```

This will:
- Connect to Airtable Metadata API
- Display all fields with types
- Show status field options
- Validate product field structure
- Confirm all required fields exist

## 📝 Last Verified

- **Date:** August 3, 2025
- **Verified By:** Airtable Metadata API
- **Total Fields:** 107
- **Product Fields:** All 5 products have complete field sets
- **Status Fields:** All have "Pending" and "Ready" options