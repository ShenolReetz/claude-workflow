# Production Workflow - Detailed Step-by-Step Documentation

## Overview
This document provides a comprehensive breakdown of the Production Content Pipeline Orchestrator V2, documenting each step, its triggers, actions, and Airtable column updates.

---

## Workflow Initialization

### Pre-Workflow Token Refresh
**Trigger**: Workflow startup  
**Actions**:
1. Check Google Drive token expiry status
2. If expired (< 1 hour remaining), refresh token automatically
3. Check YouTube token expiry status  
4. If expired (< 1 hour remaining), refresh token automatically

**Files Involved**:
- `/src/utils/google_drive_token_manager.py`
- `/src/utils/youtube_auth_manager.py`
- `/config/google_drive_token.json`
- `/config/youtube_token.json`

---

## Step 1: Credential Validation Checkpoint

**Trigger**: Workflow begins after token refresh  
**Module**: `Production_credential_validation_server.py`  
**Method**: `validate_all_credentials()`

**Actions**:
1. **API Key Validation**:
   - OpenAI API key (tests with gpt-4o model)
   - Airtable API key (tests base access)
   - ScrapingDog API key (checks remaining credits)
   - WordPress credentials (tests authentication)

2. **OAuth Token Validation**:
   - Google Drive OAuth (checks token validity and refresh capability)
   - YouTube OAuth (verifies channel access: "ReviewCh3kr")

3. **Service Credentials**:
   - JSON2Video API endpoint availability
   - Edge-TTS service availability

4. **File Credentials**:
   - Verifies `/config/api_keys.json` exists and is readable

**Output**: Health Score (98/100 in example)  
**Airtable Updates**: None  
**Failure Behavior**: Workflow stops if critical credentials fail

---

## Step 2: Fetch Pending Title from Airtable

**Trigger**: Successful credential validation  
**Module**: `Production_airtable_server.py`  
**Method**: `get_pending_title()`

**Actions**:
1. Query Airtable for records where `Status = "Pending"`
2. Retrieve first pending record
3. Extract record data including:
   - `record_id` (e.g., rec3zwkuTGvgQCoqD)
   - `Title` (e.g., "Top 5 Webcam Mounts Most Popular on Amazon 2025")
   - All empty fields to be populated

**Airtable Column Updates**:
- `Status`: "Pending" → "Processing"

**Failure Behavior**: Workflow exits if no pending titles found

---

## Step 3: Progressive Amazon Scraping with Variants

**Trigger**: Title retrieved from Airtable  
**Module**: `Production_progressive_amazon_scraper.py`  
**Method**: `search_with_variants()`

**Actions**:
1. **Generate Search Variants**:
   - Uses GPT-4o to create 5-10 search variations
   - Example: "Webcam Mounts" → ["Webcam Mounts", "Camera Mounts", "Webcam Holders", etc.]

2. **Progressive Testing**:
   - Tests each variant sequentially via ScrapingDog API
   - Stops when finding 5+ products with 10+ reviews
   - Ranks products by composite score (rating × log(reviews))

3. **Create Top 5 Countdown**:
   - Formats products in countdown order (No5 → No1)
   - Includes: title, rating, reviews, price, ASIN, affiliate link

**Airtable Column Updates**:
- `TextControlStatus`: "" → "Ready"

**Output**: 5 ranked Amazon products with full details  
**Failure Behavior**: Tries all variants; fails if none yield 5 products

---

## Step 4: Extract Product Category

**Trigger**: Successful Amazon scraping  
**Module**: `Production_product_category_extractor_server.py`  
**Method**: `extract_category()`

**Actions**:
1. Analyze product titles and descriptions
2. Use GPT-4o to determine category
3. Return standardized category (e.g., "Electronics")

**Airtable Column Updates**:
- `Category`: "General" → Extracted category (e.g., "Electronics")

---

## Step 5: Validate Scraped Products

**Trigger**: Products scraped and category extracted  
**Module**: `Production_amazon_product_validator.py`  
**Method**: `validate_amazon_products()`

**Actions**:
1. Verify all 5 products have required fields
2. Check affiliate links are properly formatted
3. Validate ratings and review counts
4. Ensure prices are present

**Output**: Validation success/failure  
**Failure Behavior**: Workflow stops if validation fails

---

## Step 6: Save Amazon Products to Airtable

**Trigger**: Successful product validation  
**Module**: `Production_airtable_server.py`  
**Method**: `save_amazon_products()`

**Actions**:
1. Save each product's details to respective columns
2. Mark all product statuses as "Ready"

**Airtable Column Updates**:
- `ProductNo1Title`: Product 1 title
- `ProductNo1TitleStatus`: "" → "Ready"
- `ProductNo1Rating`: Product 1 rating
- `ProductNo1Reviews`: Product 1 review count
- `ProductNo1Price`: Product 1 price
- `ProductNo1Link`: Product 1 affiliate link
- `ProductNo1ASIN`: Product 1 ASIN
- (Repeated for Products 2-5)

---

## Step 5.5: Generate Enhanced Product Images

**Trigger**: Products saved to Airtable  
**Module**: Direct OpenAI DALL-E 3 API calls  
**Method**: `generate_enhanced_image()` (5 times)

**Actions**:
1. For each product (1-5):
   - Generate prompt preserving product details
   - Create 1024x1792 image (9:16 ratio for video)
   - Download and save locally
   - Update Airtable with image path

**Airtable Column Updates**:
- `ProductNo1Photo`: Path to generated image
- `ProductNo2Photo`: Path to generated image
- `ProductNo3Photo`: Path to generated image
- `ProductNo4Photo`: Path to generated image
- `ProductNo5Photo`: Path to generated image

**Time**: ~30-40 seconds per image

---

## Step 7: Generate Platform-Specific Content

**Trigger**: Product images generated  
**Module**: `Production_content_generation_server.py`  
**Method**: `generate_platform_content()`

**Actions**:
1. Generate content optimized for each platform using GPT-4o:
   - YouTube: Title (< 100 chars) + Description (2000-5000 chars)
   - Instagram: Caption (< 2200 chars) + Hashtags (30)
   - TikTok: Caption (< 150 chars) + Hashtags (5-8)
   - WordPress: SEO title + Long-form content (1500-3000 words)
   - Universal keywords for all platforms

**Airtable Column Updates**:
- `VideoTitle`: Generated video title
- `VideoTitleStatus`: "" → "Ready"
- `VideoDescription`: Generated description
- `VideoDescriptionStatus`: "" → "Ready"
- `YouTubeTitle`: Platform-specific title
- `YouTubeDescription`: Full YouTube description with timestamps
- `InstagramCaption`: Instagram-optimized caption
- `InstagramHashtags`: 30 relevant hashtags
- `TikTokCaption`: Short, engaging caption
- `TikTokHashtags`: 5-8 trending hashtags
- `WordPressTitle`: SEO-optimized title
- `WordPressContent`: Full article with HTML formatting
- `UniversalKeywords`: Keywords for all platforms

---

## Step 6.5: Generate Video Scripts (Currently Failing)

**Trigger**: Platform content generated  
**Module**: `Production_text_generation_control_agent_mcp_v2.py`  
**Method**: `production_run_text_control_with_regeneration()`

**Intended Actions**:
1. Generate intro script (15 seconds)
2. Generate 5 product scripts (25-30 seconds each)
3. Generate outro script (10 seconds)
4. Validate script lengths
5. Regenerate if needed for timing

**Expected Airtable Updates**:
- `IntroScript`: 15-second intro narration
- `ProductNo1Script`: Product 1 narration
- `ProductNo2Script`: Product 2 narration
- `ProductNo3Script`: Product 3 narration
- `ProductNo4Script`: Product 4 narration
- `ProductNo5Script`: Product 5 narration
- `OutroScript`: 10-second outro with CTA

**Current Issue**: OpenAI API key not passed to environment variable

---

## Step 8: Generate Voice Narration (Not Reached)

**Trigger**: Scripts generated  
**Module**: `Production_voice_generation_server.py`  
**Method**: `generate_voice_for_record()`

**Expected Actions**:
1. Convert each script to MP3 using Edge-TTS
2. Use voice: "en-US-ChristopherNeural"
3. Optimize timing and pacing
4. Save MP3 files locally

**Expected Airtable Updates**:
- `IntroMp3`: Path to intro audio
- `ProductNo1Mp3`: Path to product 1 audio
- `ProductNo2Mp3`: Path to product 2 audio
- `ProductNo3Mp3`: Path to product 3 audio
- `ProductNo4Mp3`: Path to product 4 audio
- `ProductNo5Mp3`: Path to product 5 audio
- `OutroMp3`: Path to outro audio

---

## Step 9: Generate Intro/Outro Images (Not Reached)

**Trigger**: Voice narration complete  
**Modules**: 
- `Production_intro_image_generator.py`
- `Production_outro_image_generator.py`

**Expected Actions**:
1. Generate branded intro image (1080x1920)
2. Generate call-to-action outro image (1080x1920)
3. Apply consistent branding

**Expected Airtable Updates**:
- `IntroPhoto`: Path to intro image
- `OutroPhoto`: Path to outro image

---

## Step 10: Create Video with JSON2Video (Not Reached)

**Trigger**: All assets generated  
**Module**: `Production_json2video_agent_mcp.py`  
**Method**: `production_run_video_creation()`

**Expected Actions**:
1. Compile all assets into JSON2Video schema
2. Submit to JSON2Video API
3. Poll for completion (2-3 minutes)
4. Download finished video

**Expected Airtable Updates**:
- `VideoURL`: JSON2Video result URL
- `VideoCreatedDate`: Timestamp

---

## Step 11: Upload to Google Drive (Not Reached)

**Trigger**: Video created  
**Module**: `Production_enhanced_google_drive_agent_mcp.py`  
**Method**: `production_upload_all_assets_to_google_drive()`

**Expected Actions**:
1. Create folder structure in Google Drive
2. Upload video file
3. Upload all images
4. Upload all audio files
5. Upload metadata JSON

**Expected Airtable Updates**:
- `GoogleDriveVideoID`: Drive file ID
- `GoogleDriveFolder`: Folder URL

---

## Step 12: Publish to YouTube (Not Reached)

**Trigger**: Google Drive upload complete  
**Module**: `Production_youtube_mcp.py`  
**Method**: `upload_video()`

**Expected Actions**:
1. Download video from Google Drive
2. Upload to YouTube with metadata
3. Set thumbnail
4. Apply tags and category

**Expected Airtable Updates**:
- `YouTubeURL`: Published video URL
- `YouTubeVideoID`: YouTube video ID
- `PublishStatus`: "Published"

---

## Step 13: Publish to WordPress (Not Reached)

**Trigger**: YouTube published  
**Module**: `Production_wordpress_mcp_v2.py`  
**Method**: `publish_post()`

**Expected Actions**:
1. Create WordPress post with content
2. Embed YouTube video
3. Add featured image
4. Apply categories and tags

**Expected Airtable Updates**:
- `WordPressURL`: Published post URL
- `WordPressPostID`: WordPress post ID

---

## Step 14: Final Status Update (Not Reached)

**Trigger**: All publishing complete  
**Module**: `Production_airtable_server.py`  
**Method**: `update_record_field()`

**Expected Actions**:
1. Mark workflow as complete
2. Update completion timestamp
3. Calculate total processing time

**Expected Airtable Updates**:
- `Status`: "Processing" → "Completed"
- `CompletedDate`: Current timestamp
- `ProcessingTime`: Total minutes

---

## Error Handling & Recovery

### Checkpoint System
- Saves progress after each major step
- Located at: `/home/claude-workflow/workflow_checkpoints.json`
- Allows resuming from last successful step

### API Resilience
- Exponential backoff with jitter for retries
- Circuit breakers for API health monitoring
- Dead letter queue for failed items
- Managed by: `/src/utils/api_resilience_manager.py`

### Token Management
- Automatic refresh at workflow start
- 1-hour expiry handled gracefully
- Manual refresh fallback available

---

## Performance Metrics

**Average Step Timings**:
- Credential Validation: 18 seconds
- Fetch Title: 3 seconds
- Amazon Scraping: 60-90 seconds
- Category Extraction: 2 seconds
- Product Validation: 1 second
- Save to Airtable: 3 seconds
- Image Generation: 150-200 seconds (5 images)
- Content Generation: 15 seconds
- Script Generation: 10-15 seconds
- Voice Generation: 20-30 seconds
- Video Creation: 120-180 seconds
- Upload/Publishing: 30-60 seconds

**Total Workflow Time**: 10-15 minutes per video

---

## Airtable Schema Summary

### Input Fields (Must be present)
- `Title`: The video title to process
- `Status`: Must be "Pending" to be picked up

### Status Tracking Fields (17 total)
- `Status`: Pending → Processing → Completed
- `TextControlStatus`: Tracks script generation
- `VideoTitleStatus`: Tracks title generation
- `VideoDescriptionStatus`: Tracks description generation
- `ProductNo1TitleStatus` through `ProductNo5TitleStatus`: Product statuses

### Content Fields
- Video metadata (title, description)
- Platform-specific content (YouTube, Instagram, TikTok, WordPress)
- Product details (5 products × 7 fields each)
- Scripts (intro, 5 products, outro)

### Asset URLs (14 fields)
- Audio files (7 MP3s)
- Images (7 photos)
- Video URL
- Google Drive links
- Platform publication URLs

### Metadata Fields
- Category
- Keywords
- Timestamps
- Processing metrics