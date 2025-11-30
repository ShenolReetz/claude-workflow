# Airtable Integration Plan - Complete Workflow Mapping

## Overview

This document maps all Airtable interactions throughout the 17-phase agent workflow. Once you provide your Airtable schema (column names and types), we'll implement the full MCP integration.

---

## Current Workflow Phases (17 Total)

```
Phase 1:  FETCH_TITLE          - Get pending title from Airtable
Phase 2:  SCRAPE_PRODUCTS      - Search Amazon for products
Phase 3:  EXTRACT_CATEGORIES   - Extract product categories
Phase 4:  VALIDATE_PRODUCTS    - Validate product data
Phase 5:  SAVE_PRODUCTS        - Save products to Airtable
Phase 6:  GENERATE_IMAGES      - Generate 7 images (HuggingFace FLUX)
Phase 7:  SAVE_IMAGES          - Save image paths to Airtable
Phase 8:  GENERATE_SCRIPTS     - Generate 7 voice scripts (HuggingFace Llama)
Phase 9:  SAVE_SCRIPTS         - Save scripts to Airtable
Phase 10: GENERATE_VOICES      - Generate 7 voice files (ElevenLabs)
Phase 11: SAVE_VOICES          - Save voice paths to Airtable
Phase 12: GENERATE_CONTENT     - Generate platform content (YouTube, WordPress, Instagram)
Phase 13: SAVE_CONTENT         - Save content to Airtable
Phase 14: CREATE_VIDEO         - Create video with Remotion
Phase 15: SAVE_VIDEO           - Save video path to Airtable
Phase 16: PUBLISH_ALL          - Publish to YouTube, WordPress, Instagram (parallel)
Phase 17: UPDATE_FINAL         - Update Airtable with all URLs and mark Published
```

---

## Airtable Read/Write Points

### READ Operations (1 phase)

#### Phase 1: FETCH_TITLE
**Agent**: DataAcquisitionAgent → AirtableFetchSubAgent
**MCP Tool**: `mcp__airtable__search_records` or `mcp__airtable__list_records`
**Purpose**: Get one pending title to process

**Current Mock Implementation**:
```python
# agents/data_acquisition/airtable_fetch_subagent.py:66
return {
    'record_id': 'test_record_123',
    'title': 'Top 5 Wireless Headphones 2024',
    'notes': '',
    'created_time': '2024-01-01T00:00:00.000Z'
}
```

**Query Needed**:
- **Filter**: Status = "Pending" (or similar)
- **Sort**: CreatedTime ASC (oldest first)
- **Limit**: 1 record

**Fields to Read**:
```
[ ] Record ID (Airtable internal ID)
[ ] Title field name: _____________
[ ] Notes field name: _____________
[ ] Status field name: _____________
[ ] Created time field name: _____________
```

---

### WRITE Operations (7 phases)

#### Phase 5: SAVE_PRODUCTS
**Agent**: DataAcquisitionAgent → AirtableFetchSubAgent
**MCP Tool**: `mcp__airtable__update_records`
**Purpose**: Save scraped product data

**Fields to Update** (provide your column names):
```
Product 1:
[ ] Product1_Title: _____________
[ ] Product1_Price: _____________
[ ] Product1_OriginalPrice: _____________
[ ] Product1_Rating: _____________
[ ] Product1_ReviewCount: _____________
[ ] Product1_ImageURL: _____________
[ ] Product1_ProductURL: _____________
[ ] Product1_ASIN: _____________

Product 2-5: (same pattern)
[ ] Product2_Title: _____________
...
[ ] Product5_ASIN: _____________

Metadata:
[ ] Status: "Products Scraped" (or your value: _____________)
[ ] ProductCount: _____________
[ ] ScrapedAt: _____________
```

---

#### Phase 7: SAVE_IMAGES
**Agent**: ContentGenerationAgent
**MCP Tool**: `mcp__airtable__update_records`
**Purpose**: Save generated image paths

**Fields to Update**:
```
[ ] IntroImage: _____________
[ ] Product1_Image: _____________
[ ] Product2_Image: _____________
[ ] Product3_Image: _____________
[ ] Product4_Image: _____________
[ ] Product5_Image: _____________
[ ] OutroImage: _____________

[ ] Status: "Images Generated" (or: _____________)
[ ] ImagesGeneratedAt: _____________
```

**Image Path Format**: Will be local storage paths like:
```
/home/claude-workflow/local_storage/{record_id}/images/intro_flux.jpg
/home/claude-workflow/local_storage/{record_id}/images/product1_flux.jpg
...
```

---

#### Phase 9: SAVE_SCRIPTS
**Agent**: ContentGenerationAgent
**MCP Tool**: `mcp__airtable__update_records`
**Purpose**: Save voice scripts (intro, 5 products, outro)

**Fields to Update**:
```
Voice Scripts (7 total):
[ ] IntroScript: _____________
[ ] Product1_Script: _____________
[ ] Product2_Script: _____________
[ ] Product3_Script: _____________
[ ] Product4_Script: _____________
[ ] Product5_Script: _____________
[ ] OutroScript: _____________

[ ] Status: "Scripts Generated" (or: _____________)
[ ] ScriptsGeneratedAt: _____________
```

**Script Example**:
```
IntroScript: "Welcome to today's top 5 wireless headphones review!
              We've tested dozens to bring you the absolute best..."

Product1Script: "Starting at number 5, the Sony WH-1000XM5 offers
                 industry-leading noise cancellation..."
```

---

#### Phase 11: SAVE_VOICES
**Agent**: ContentGenerationAgent
**MCP Tool**: `mcp__airtable__update_records`
**Purpose**: Save voice file paths

**Fields to Update**:
```
[ ] IntroVoice: _____________
[ ] Product1_Voice: _____________
[ ] Product2_Voice: _____________
[ ] Product3_Voice: _____________
[ ] Product4_Voice: _____________
[ ] Product5_Voice: _____________
[ ] OutroVoice: _____________

[ ] Status: "Voices Generated" (or: _____________)
[ ] VoicesGeneratedAt: _____________
```

**Voice Path Format**:
```
/home/claude-workflow/local_storage/{record_id}/voice/intro_voice.mp3
/home/claude-workflow/local_storage/{record_id}/voice/product1_voice.mp3
...
```

---

#### Phase 13: SAVE_CONTENT
**Agent**: ContentGenerationAgent
**MCP Tool**: `mcp__airtable__update_records`
**Purpose**: Save platform-specific content

**Fields to Update**:
```
YouTube:
[ ] YouTubeTitle: _____________
[ ] YouTubeDescription: _____________
[ ] YouTubeTags: _____________

WordPress:
[ ] WordPressTitle: _____________
[ ] WordPressArticle: _____________
[ ] WordPressTags: _____________

Instagram:
[ ] InstagramCaption: _____________
[ ] InstagramHashtags: _____________

[ ] Status: "Content Generated" (or: _____________)
[ ] ContentGeneratedAt: _____________
```

**Content Examples**:
```
YouTubeTitle: "Top 5 Wireless Headphones 2024 - Tested & Reviewed!"
YouTubeDescription: "🎧 We tested 50+ headphones to find the best..."
YouTubeTags: "#headphones #review #tech #2024"

InstagramHashtags: "#headphones #tech #review #wireless #2024 #audio..."
```

---

#### Phase 15: SAVE_VIDEO
**Agent**: VideoProductionAgent
**MCP Tool**: `mcp__airtable__update_records`
**Purpose**: Save final video path

**Fields to Update**:
```
[ ] VideoPath: _____________
[ ] VideoType: _____________ (standard or wow)
[ ] VideoDuration: _____________
[ ] VideoSize: _____________
[ ] VideoCreatedAt: _____________

[ ] Status: "Video Created" (or: _____________)
```

**Video Path Format**:
```
/home/claude-workflow/local_storage/{record_id}/video/final_video.mp4
```

---

#### Phase 17: UPDATE_FINAL
**Agent**: PublishingAgent → AirtableUpdaterSubAgent
**MCP Tool**: `mcp__airtable__update_records`
**Purpose**: Mark workflow complete with all URLs

**Fields to Update**:
```
Publishing URLs:
[ ] YouTubeURL: _____________
[ ] YouTubeVideoID: _____________
[ ] YouTubePublishedAt: _____________

[ ] WordPressURL: _____________
[ ] WordPressPostID: _____________
[ ] WordPressPublishedAt: _____________

[ ] InstagramURL: _____________
[ ] InstagramMediaID: _____________
[ ] InstagramPublishedAt: _____________

Final Status:
[ ] Status: "Published" (or: _____________)
[ ] PublishedAt: _____________
[ ] WorkflowDuration: _____________

Analytics (optional):
[ ] TotalCost: _____________
[ ] ImagesCost: _____________
[ ] TextCost: _____________
[ ] VoicesCost: _____________
[ ] ScrapingCost: _____________
```

---

## Error Handling Updates

### Phase-Specific Error Status Updates

When errors occur, we update the Status field:

```
[ ] Error Status Value: _____________
[ ] ErrorMessage field: _____________
[ ] ErrorPhase field: _____________
[ ] ErrorTimestamp field: _____________
[ ] RetryCount field: _____________
```

**Example Error Updates**:
```
Phase 2 Failure (SCRAPE_PRODUCTS):
  Status: "Error - Scraping Failed"
  ErrorMessage: "Amazon scraping timed out after 60s"
  ErrorPhase: "SCRAPE_PRODUCTS"
  RetryCount: 1

Phase 14 Failure (CREATE_VIDEO):
  Status: "Error - Video Creation Failed"
  ErrorMessage: "Remotion render failed - missing audio file"
  ErrorPhase: "CREATE_VIDEO"
  RetryCount: 0
```

---

## Status Field Values

### Recommended Status Flow

Please provide your preferred status values for each phase:

```
Initial:
[ ] Initial status: _____________ (e.g., "Pending")

Phase 1 - Fetched:
[ ] After fetch: _____________ (e.g., "Processing")

Phase 5 - Products Saved:
[ ] After products: _____________ (e.g., "Products Scraped")

Phase 7 - Images Saved:
[ ] After images: _____________ (e.g., "Images Generated")

Phase 9 - Scripts Saved:
[ ] After scripts: _____________ (e.g., "Scripts Generated")

Phase 11 - Voices Saved:
[ ] After voices: _____________ (e.g., "Voices Generated")

Phase 13 - Content Saved:
[ ] After content: _____________ (e.g., "Content Generated")

Phase 15 - Video Saved:
[ ] After video: _____________ (e.g., "Video Created")

Phase 17 - Published:
[ ] Final status: _____________ (e.g., "Published")

Error:
[ ] Error status: _____________ (e.g., "Error")
```

---

## Airtable Configuration Needed

### 1. Base & Table Information

```
[ ] Airtable Base ID: _____________ (format: appXXXXXXXXXXXXXX)
[ ] Table Name: _____________ (e.g., "Video Titles")
[ ] Table ID: _____________ (format: tblXXXXXXXXXXXXXX)
```

### 2. View Configuration (Optional)

```
[ ] View Name for Pending Records: _____________ (e.g., "Pending")
[ ] View ID: _____________ (optional)
```

### 3. Field Types

For each field above, specify the Airtable field type:

```
Common Types:
- singleLineText
- longText
- number
- date
- singleSelect
- multipleSelects
- url
- attachment
- checkbox
```

**Example**:
```
Title: singleLineText
Status: singleSelect (values: Pending, Processing, Published, Error)
YouTubeURL: url
ProductCount: number
PublishedAt: date
```

---

## Implementation Files to Update

Once you provide the schema, we'll implement:

### 1. Airtable Fetch SubAgent
**File**: `agents/data_acquisition/airtable_fetch_subagent.py`
**Changes**:
- Remove mock data
- Add `mcp__airtable__search_records` call
- Map your field names
- Filter by Status = "Pending"

### 2. Airtable Updater SubAgent
**File**: `agents/publishing/airtable_updater_subagent.py`
**Changes**:
- Remove mock updates
- Add `mcp__airtable__update_records` calls
- Map all your field names for each phase
- Add error handling with Status updates

### 3. ContentGenerationAgent
**File**: `agents/content_generation/agent.py`
**Changes**:
- Add Airtable update calls after Phase 7, 9, 11, 13
- Map image/script/voice/content field names

### 4. VideoProductionAgent
**File**: `agents/video_production/agent.py`
**Changes**:
- Add Airtable update call after Phase 15
- Map video field names

### 5. DataAcquisitionAgent
**File**: `agents/data_acquisition/agent.py`
**Changes**:
- Add Airtable update call after Phase 5
- Map product field names

---

## Template to Fill Out Tomorrow

### Quick Schema Template

```markdown
## My Airtable Schema

**Base ID**: appXXXXXXXXXXXXXX
**Table Name**: Video Titles
**Table ID**: tblXXXXXXXXXXXXXX

### Core Fields

| Field Purpose | Your Field Name | Field Type | Notes |
|---------------|-----------------|------------|-------|
| Title | Title | singleLineText | Main video title |
| Status | Status | singleSelect | Values: Pending, Processing, Published, Error |
| Notes | Notes | longText | Optional notes |

### Product Fields (5 products × 8 fields = 40 fields)

| Field Purpose | Your Field Name | Field Type |
|---------------|-----------------|------------|
| Product 1 Title | Product1_Title | singleLineText |
| Product 1 Price | Product1_Price | singleLineText |
| Product 1 Rating | Product1_Rating | number |
| ... | ... | ... |

### Image Fields (7 images)

| Field Purpose | Your Field Name | Field Type |
|---------------|-----------------|------------|
| Intro Image | IntroImage | attachment OR url |
| Product 1 Image | Product1_Image | attachment OR url |
| ... | ... | ... |

### Script Fields (7 scripts)

| Field Purpose | Your Field Name | Field Type |
|---------------|-----------------|------------|
| Intro Script | IntroScript | longText |
| Product 1 Script | Product1_Script | longText |
| ... | ... | ... |

### Voice Fields (7 voices)

| Field Purpose | Your Field Name | Field Type |
|---------------|-----------------|------------|
| Intro Voice | IntroVoice | attachment OR url |
| Product 1 Voice | Product1_Voice | attachment OR url |
| ... | ... | ... |

### Content Fields

| Field Purpose | Your Field Name | Field Type |
|---------------|-----------------|------------|
| YouTube Title | YouTubeTitle | singleLineText |
| YouTube Description | YouTubeDescription | longText |
| YouTube Tags | YouTubeTags | longText |
| WordPress Title | WordPressTitle | singleLineText |
| WordPress Article | WordPressArticle | longText |
| Instagram Caption | InstagramCaption | longText |
| Instagram Hashtags | InstagramHashtags | longText |

### Video Fields

| Field Purpose | Your Field Name | Field Type |
|---------------|-----------------|------------|
| Video Path | VideoPath | attachment OR url |
| Video Type | VideoType | singleSelect |

### Publishing Fields

| Field Purpose | Your Field Name | Field Type |
|---------------|-----------------|------------|
| YouTube URL | YouTubeURL | url |
| WordPress URL | WordPressURL | url |
| Instagram URL | InstagramURL | url |
| Published At | PublishedAt | date |

### Error Fields (optional)

| Field Purpose | Your Field Name | Field Type |
|---------------|-----------------|------------|
| Error Message | ErrorMessage | longText |
| Error Phase | ErrorPhase | singleLineText |
| Retry Count | RetryCount | number |

### Status Values

List all possible values for your Status field:
- [ ] Pending
- [ ] Processing
- [ ] Products Scraped
- [ ] Images Generated
- [ ] Scripts Generated
- [ ] Voices Generated
- [ ] Content Generated
- [ ] Video Created
- [ ] Published
- [ ] Error
```

---

## Next Steps

Tomorrow, please provide:

1. ✅ **Airtable Plan Details** (subscription confirmed)
2. ✅ **Filled Template Above** (all field names and types)
3. ✅ **Status Flow Preferences** (what status values to use)
4. ✅ **Field Type Clarifications** (especially for images/videos/voices - attachment vs url)

Once you provide this information, I will:

1. ✅ Update all 7 Airtable interaction points in the agents
2. ✅ Replace all mock data with real MCP calls
3. ✅ Map your exact field names
4. ✅ Implement proper error handling with status updates
5. ✅ Test the full workflow end-to-end
6. ✅ Push all changes to GitHub

**Estimated Implementation Time**: 1-2 hours after receiving your schema

---

## Questions to Consider

1. **File Storage**: Do you want to store images/videos/voices as:
   - Attachments in Airtable (uploaded files)
   - URLs pointing to local storage paths
   - URLs pointing to cloud storage (Google Drive, S3, etc.)

2. **Status Granularity**: Do you want detailed status for each phase, or fewer status values?

3. **Error Recovery**: Should we auto-retry failed phases, or just mark as Error and stop?

4. **Notifications**: Do you want email/Slack notifications when videos are published or errors occur?

5. **Analytics**: Do you want cost tracking and performance metrics saved to Airtable?

---

## Example: Complete Workflow with Your Schema

Once you provide the field names, the workflow will look like this:

```
Phase 1: FETCH_TITLE
  READ from Airtable:
    - Filter: Status = "Pending"
    - Get: Title, Notes, RecordID
    - Update Status → "Processing"

Phase 5: SAVE_PRODUCTS
  UPDATE Airtable:
    - Product1_Title = "Sony WH-1000XM5"
    - Product1_Price = "$349.99"
    - ... (40 product fields)
    - Status → "Products Scraped"

Phase 7: SAVE_IMAGES
  UPDATE Airtable:
    - IntroImage = "/path/to/intro.jpg"
    - ... (7 image fields)
    - Status → "Images Generated"

Phase 9: SAVE_SCRIPTS
  UPDATE Airtable:
    - IntroScript = "Welcome to..."
    - ... (7 script fields)
    - Status → "Scripts Generated"

Phase 11: SAVE_VOICES
  UPDATE Airtable:
    - IntroVoice = "/path/to/intro.mp3"
    - ... (7 voice fields)
    - Status → "Voices Generated"

Phase 13: SAVE_CONTENT
  UPDATE Airtable:
    - YouTubeTitle = "Top 5..."
    - YouTubeDescription = "..."
    - ... (7 content fields)
    - Status → "Content Generated"

Phase 15: SAVE_VIDEO
  UPDATE Airtable:
    - VideoPath = "/path/to/video.mp4"
    - Status → "Video Created"

Phase 17: UPDATE_FINAL
  UPDATE Airtable:
    - YouTubeURL = "https://youtube.com/watch?v=..."
    - WordPressURL = "https://yoursite.com/post/..."
    - InstagramURL = "https://instagram.com/p/..."
    - Status → "Published"
    - PublishedAt = "2024-01-01T12:00:00Z"
```

---

**Looking forward to implementing the complete Airtable integration tomorrow!** 🚀
