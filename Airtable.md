# Airtable Database Schema Reference

> **Auto-generated on 2025-07-15** from Airtable API metadata  
> **Base ID:** `appTtNBJ8dAnjvkPP`  
> **Total Tables:** 2  
> **Primary Table:** Video Titles (104 fields)

---

## 📋 Table Overview

| Table Name | Table ID | Fields | Purpose |
|------------|----------|--------|---------|
| **Video Titles** | `tblhGDEW6eUbmaYZx` | 104 | Main workflow data |
| **Content Categories** | `tblBgpNLnE2C3cqSu` | 3 | Category management |

---

## 🎬 Video Titles Table (104 Fields)

### 📝 Basic Content Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `Title` | singleLineText | Original input title |
| `Status` | singleSelect | Workflow status: Pending, Completed, In Progress, Processing |
| `Content Category` | multipleRecordLinks | Links to Content Categories table |
| `VideoTitle` | multilineText | AI-generated video title |
| `VideoTitleStatus` | singleSelect | Approval status: Approved, Rejected, Pending |
| `VideoDescription` | richText | Video description content |
| `VideoDescriptionStatus` | singleSelect | Approval status: Approved, Rejected, Pending |

### 🛍️ Product Fields (Products 1-5)

#### Product 5 Fields
| Field Name | Type | Description |
|------------|------|-------------|
| `ProductNo5Title` | singleLineText | Product #5 title (The Product Number 5 from the Top 5) |
| `ProductNo5TitleStatus` | singleSelect | Status: Pending, Ready |
| `ProductNo5Description` | richText | Product #5 description |
| `ProductNo5DescriptionStatus` | singleSelect | Status: Pending, Ready |
| `ProductNo5Photo` | url | Product #5 image URL (The First Photo for the Product No 5) |
| `ProductNo5PhotoStatus` | singleSelect | Status: Pending, Ready |
| `ProductNo5AffiliateLink` | url | Amazon affiliate link |
| `ProductNo5Price` | number | Product price (precision: 1) |
| `ProductNo5Rating` | number | Star rating (precision: 1) |
| `ProductNo5Reviews` | number | Review count (precision: 1) |

#### Product 4 Fields
| Field Name | Type | Description |
|------------|------|-------------|
| `ProductNo4Title` | singleLineText | Product #4 title |
| `ProductNo4TitleStatus` | singleSelect | Status: Pending, Ready |
| `ProductNo4Description` | richText | Product #4 description |
| `ProductNo4DescriptionStatus` | singleSelect | Status: Pending, Ready |
| `ProductNo4Photo` | url | Product #4 image URL |
| `ProductNo4PhotoStatus` | singleSelect | Status: Pending, Ready |
| `ProductNo4AffiliateLink` | url | Amazon affiliate link |
| `ProductNo4Price` | number | Product price (precision: 1) |
| `ProductNo4Rating` | number | Star rating (precision: 1) |
| `ProductNo4Reviews` | number | Review count (precision: 1) |

#### Product 3 Fields
| Field Name | Type | Description |
|------------|------|-------------|
| `ProductNo3Title` | singleLineText | Product #3 title |
| `ProductNo3TitleStatus` | singleSelect | Status: Pending, Ready |
| `ProductNo3Description` | richText | Product #3 description |
| `ProductNo3DescriptionStatus` | singleSelect | Status: Pending, Ready |
| `ProductNo3Photo` | url | Product #3 image URL |
| `ProductNo3PhotoStatus` | singleSelect | Status: Pending, Ready |
| `ProductNo3AffiliateLink` | url | Amazon affiliate link |
| `ProductNo3Price` | number | Product price (precision: 1) |
| `ProductNo3Rating` | number | Star rating (precision: 1) |
| `ProductNo3Reviews` | number | Review count (precision: 1) |

#### Product 2 Fields
| Field Name | Type | Description |
|------------|------|-------------|
| `ProductNo2Title` | singleLineText | Product #2 title |
| `ProductNo2TitleStatus` | singleSelect | Status: Pending, Ready |
| `ProductNo2Description` | richText | Product #2 description |
| `ProductNo2DescriptionStatus` | singleSelect | Status: Pending, Ready |
| `ProductNo2Photo` | url | Product #2 image URL |
| `ProductNo2PhotoStatus` | singleSelect | Status: Pending, Ready |
| `ProductNo2AffiliateLink` | url | Amazon affiliate link |
| `ProductNo2Price` | number | Product price (precision: 1) |
| `ProductNo2Rating` | number | Star rating (precision: 1) |
| `ProductNo2Reviews` | number | Review count (precision: 1) |

#### Product 1 Fields
| Field Name | Type | Description |
|------------|------|-------------|
| `ProductNo1Title` | singleLineText | Product #1 title |
| `ProductNo1TitleStatus` | singleSelect | Status: Pending, Ready |
| `ProductNo1Description` | richText | Product #1 description |
| `ProductNo1DescriptionStatus` | singleSelect | Status: Pending, Ready |
| `ProductNo1Photo` | url | Product #1 image URL |
| `ProductNo1PhotoStatus` | singleSelect | Status: Pending, Ready |
| `ProductNo1AffiliateLink` | url | Amazon affiliate link |
| `ProductNo1Price` | number | Product price (precision: 1) |
| `ProductNo1Rating` | number | Star rating (precision: 1) |
| `ProductNo1Reviews` | number | Review count (precision: 1) |

### 🎤 Voice & Audio Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `IntroMp3` | url | **VOICE FIELD** - Intro voice file URL |
| `OutroMp3` | url | **VOICE FIELD** - Outro voice file URL |
| `Product1Mp3` | url | **VOICE FIELD** - Product 1 voice file URL |
| `Product2Mp3` | url | **VOICE FIELD** - Product 2 voice file URL |
| `Product3Mp3` | url | **VOICE FIELD** - Product 3 voice file URL |
| `Product4Mp3` | url | **VOICE FIELD** - Product 4 voice file URL |
| `Product5Mp3` | url | **VOICE FIELD** - Product 5 voice file URL |

### 🖼️ Media Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `IntroPhoto` | url | Intro scene image |
| `OutroPhoto` | url | Outro scene image |
| `FinalVideo` | url | **FINAL OUTPUT** - Completed video URL |

### 🔍 Keywords & SEO Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `KeyWords` | multilineText | Legacy keyword field |
| `YouTubeKeywords` | multilineText | YouTube tags and search keywords (comma-separated) |
| `InstagramHashtags` | multilineText | Instagram hashtags with # symbol (space-separated, max 30) |
| `TikTokKeywords` | multilineText | TikTok discovery keywords and trending terms |
| `WordPressSEO` | multilineText | Long-tail SEO keywords for blog post optimization |
| `UniversalKeywords` | multilineText | Core keywords that work across all platforms |

### 📱 Platform-Specific Content

#### Titles
| Field Name | Type | Description |
|------------|------|-------------|
| `YouTubeTitle` | singleLineText | Optimized for YouTube Shorts (60 char limit) |
| `TikTokTitle` | singleLineText | Gen Z language, trending hooks |
| `InstagramTitle` | singleLineText | Visual storytelling focus |
| `WordPressTitle` | singleLineText | Long-tail SEO optimized |

#### Descriptions
| Field Name | Type | Description |
|------------|------|-------------|
| `YouTubeDescription` | multilineText | Video description with hashtags |
| `TikTokDescription` | multilineText | Caption with trending hashtags |
| `InstagramCaption` | multilineText | Engaging caption with story elements |
| `WordPressContent` | multilineText | SEO blog post content |

### 📝 Script & Content Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `IntroHook` | multilineText | **VOICE TEXT** - Attention-grabbing intro (5 seconds) |
| `OutroCallToAction` | multilineText | **VOICE TEXT** - Strong CTA for engagement |
| `VideoScript` | multilineText | **VOICE TEXT** - Complete countdown script JSON |

### 📊 Analytics & Quality Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `SEOScore` | number | Overall SEO optimization score (1-100) |
| `TitleOptimizationScore` | number | Title quality score per platform |
| `KeywordDensity` | number | Keyword usage percentage |
| `EngagementPrediction` | number | Predicted engagement score |
| `PlatformReadiness` | multipleSelects | Which platforms are ready: Youtube, Instagram, TikTok, Website |

### 🔄 Workflow Control Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `TextControlStatus` | multilineText | Text validation status |
| `ContentValidationStatus` | singleSelect | Draft, Validated, Failed, Regenerating |
| `ValidationIssues` | multilineText | Any issues found during validation |
| `GenerationAttempts` | number | Workflow attempt counter (precision: 1) |
| `RegenerationCount` | number | How many times content was regenerated (precision: 1) |
| `LastOptimizationDate` | date | When content was last optimized |

### 🎬 Video Production Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `JSON2VideoProjectID` | singleLineText | JSON2Video project identifier |

### 📱 Social Media Integration

#### YouTube
| Field Name | Type | Description |
|------------|------|-------------|
| `YouTubeURL` | url | Published YouTube video URL |

#### TikTok
| Field Name | Type | Description |
|------------|------|-------------|
| `TikTokURL` | url | Published TikTok video URL |
| `TikTokVideoID` | singleLineText | TikTok video identifier |
| `TikTokPublishID` | singleLineText | TikTok publish identifier |
| `TikTokStatus` | singleSelect | Status: PROCESSING, PUBLISHED, FAILED |
| `TikTokCaption` | multilineText | TikTok caption text |
| `TikTokHashtags` | multilineText | TikTok hashtags |
| `TikTokUsername` | singleLineText | TikTok username |

---

## 📂 Content Categories Table (3 Fields)

| Field Name | Type | Description |
|------------|------|-------------|
| `Category Name` | singleLineText | Category identifier |
| `Description` | multilineText | Category description |
| `Related Video Titles` | multipleRecordLinks | Links back to Video Titles table |

---

## 🔗 Field Relationships

### Voice Field Mapping
```
Workflow Code          → Airtable Field
IntroVoiceURL         → IntroMp3
OutroVoiceURL         → OutroMp3  
ProductNo[X]VoiceURL  → Product[X]Mp3
IntroVoiceText        → IntroHook
OutroVoiceText        → OutroCallToAction
ProductNo[X]VoiceText → VideoScript (combined)
```

### Product Field Pattern
Each product (1-5) follows this pattern:
- `ProductNo[X]Title` - Product name
- `ProductNo[X]Description` - Product description  
- `ProductNo[X]Photo` - Product image URL
- `ProductNo[X]AffiliateLink` - Amazon affiliate link
- `ProductNo[X]Price` - Product price
- `ProductNo[X]Rating` - Star rating
- `ProductNo[X]Reviews` - Review count
- `ProductNo[X]TitleStatus` - Title approval status
- `ProductNo[X]DescriptionStatus` - Description approval status  
- `ProductNo[X]PhotoStatus` - Photo approval status
- `Product[X]Mp3` - Voice file URL

### Platform Integration Fields
- **YouTube**: `YouTubeURL`, `YouTubeTitle`, `YouTubeDescription`, `YouTubeKeywords`
- **TikTok**: `TikTokURL`, `TikTokTitle`, `TikTokDescription`, `TikTokKeywords`, `TikTokStatus`, etc.
- **Instagram**: `InstagramTitle`, `InstagramCaption`, `InstagramHashtags`
- **WordPress**: `WordPressTitle`, `WordPressContent`, `WordPressSEO`

### Status Tracking
- Main workflow: `Status` (Pending → Processing → Completed)
- Content validation: `ContentValidationStatus` (Draft → Validated)
- Platform readiness: `PlatformReadiness` (multi-select)
- Individual components: `*Status` fields for titles, descriptions, photos

---

## 🚀 Usage Notes

1. **Primary Key**: Record ID (auto-generated by Airtable)
2. **Main Entry Point**: `Title` field contains the original input
3. **Final Output**: `FinalVideo` contains the completed video URL
4. **Voice Integration**: Use `IntroMp3`, `OutroMp3`, `Product[X]Mp3` for voice URLs
5. **Multi-Platform**: Each platform has dedicated title/description/keyword fields
6. **Quality Control**: Multiple validation and status tracking fields

---

*This reference file is generated from live Airtable API data and reflects the current schema as of 2025-07-15.*