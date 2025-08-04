# Airtable Column to Workflow Mapping Analysis

## 🔄 Complete Workflow Steps Based on Column Analysis

### Step 1: Title Selection & Initialization
**Trigger:** Select record where `Status` = "Pending" and `ID` is lowest

**Fields to Update:**
```
Status → "Processing"
GenerationAttempts → Increment by 1
```

---

### Step 2: Product Validation & Research
**Purpose:** Validate sufficient Amazon products exist

**Fields to Check:**
- `Title` - Use for Amazon search

**Fields to Update on Success:**
```
TextControlStatus → "Ready for Product Research"
```

**Fields to Update on Failure:**
```
Status → "Skiped" (if insufficient products)
ValidationIssues → "Insufficient products found: X/5"
```

---

### Step 3: Universal Keywords & SEO Generation (FIRST)
**Purpose:** Generate base keywords that will be used for all platform-specific content

**Fields to Update:**
```
UniversalKeywords → Base keywords for all platforms
KeyWords → General SEO keywords
```

---

### Step 4: Platform-Specific Keywords Generation (SECOND)
**Purpose:** Generate platform-optimized keywords BEFORE titles/descriptions

**Fields to Update (ORDER MATTERS):**
```
# YouTube Keywords FIRST
YouTubeKeywords → YouTube-specific tags and keywords

# TikTok Keywords FIRST  
TikTokKeywords → TikTok trending hashtags
TikTokHashtags → Full TikTok hashtag list

# Instagram Keywords FIRST
InstagramHashtags → Instagram-specific hashtags

# WordPress Keywords FIRST
WordPressSEO → WordPress SEO keywords
```

---

### Step 5: Platform-Specific Content Generation (THIRD)
**Purpose:** Generate titles and descriptions BASED ON platform keywords

**Dependencies:** Platform keywords must be generated first!

**Fields to Update (USING KEYWORDS):**
```
# YouTube Content (based on YouTubeKeywords)
YouTubeTitle → Generated using YouTubeKeywords for SEO
YouTubeDescription → Generated using YouTubeKeywords for optimization

# TikTok Content (based on TikTokKeywords/Hashtags)
TikTokTitle → Generated using TikTokKeywords for virality
TikTokDescription → Generated using TikTokKeywords
TikTokCaption → Full caption with TikTokHashtags integrated

# Instagram Content (based on InstagramHashtags)
InstagramTitle → Generated using InstagramHashtags context
InstagramCaption → Generated with InstagramHashtags integrated

# WordPress Content (based on WordPressSEO)
WordPressTitle → SEO-optimized using WordPressSEO keywords
WordPressContent → Long-form content optimized with WordPressSEO
```

---

### Step 6: Amazon Product Scraping & Affiliate Generation
**Purpose:** Get product details and generate affiliate links

**Fields to Update for Each Product (1-5):**
```
# CRITICAL: Products are numbered 1-5 but displayed as #5 to #1 (countdown)
ProductNo1Title → "#5 {Product Name}" (e.g., "#5 Sony WH-1000XM5")
ProductNo1Description → Product description (MAX 9 seconds audio)
ProductNo1Price → Product price
ProductNo1Rating → Product rating (e.g., 4.5)
ProductNo1Reviews → Review count
ProductNo1Photo → Product image URL
ProductNo1AffiliateLink → Generated affiliate link

ProductNo2Title → "#4 {Product Name}" (e.g., "#4 Bose QuietComfort 45")
ProductNo2Description → Product description (MAX 9 seconds audio)
[... continue for products 2-4 ...]

ProductNo5Title → "#1 {Product Name}" (e.g., "#1 Apple AirPods Max")
ProductNo5Description → Product description (MAX 9 seconds audio)
[... rest of Product 5 fields ...]

# Status fields
ProductNo{X}TitleStatus → "Ready"
ProductNo{X}DescriptionStatus → "Ready"
ProductNo{X}PhotoStatus → "Ready"
```

**⚠️ COUNTDOWN MAPPING:**
- ProductNo1 = #5 (Fifth best)
- ProductNo2 = #4 (Fourth best)
- ProductNo3 = #3 (Third best)
- ProductNo4 = #2 (Second best)
- ProductNo5 = #1 (BEST/WINNER)

---

### Step 7: Video Content Script Generation
**Purpose:** Generate video-specific content with STRICT timing requirements

**CRITICAL TIMING REQUIREMENTS:**
```
IntroHook → Engaging hook text (MAX 5 seconds audio)
  - Must grab attention immediately
  - Example: "These 5 gadgets will blow your mind - and #1 is unbelievable!"
  
VideoTitle → Video title for metadata (not for audio)

VideoDescription → Video description for metadata (not for audio)

OutroCallToAction → Call-to-action text (MAX 5 seconds audio)
  - Must drive action
  - Example: "Click below for exclusive deals - limited time only!"

VideoScript → Complete countdown script with timing:
  - Intro: 5 seconds (IntroHook)
  - Product #5: 9 seconds (ProductNo1Description)
  - Product #4: 9 seconds (ProductNo2Description)
  - Product #3: 9 seconds (ProductNo3Description)
  - Product #2: 9 seconds (ProductNo4Description)
  - Product #1: 9 seconds (ProductNo5Description)
  - Outro: 5 seconds (OutroCallToAction)
  - TOTAL: 50 seconds (under 60 second limit)

# Status fields
VideoTitleStatus → "Ready"
VideoDescriptionStatus → "Ready"
```

**Text Generation Requirements:**
```python
# IntroHook Generation
- Transform VideoTitle into engaging hook
- MAX 5 seconds when read aloud
- Must create curiosity/urgency
- Examples:
  "VideoTitle": "Top 5 Headphones 2025"
  "IntroHook": "The #1 headphone on this list has features that seem impossible!"

# OutroCallToAction Generation  
- Transform into compelling CTA
- MAX 5 seconds when read aloud
- Must drive clicks/engagement
- Examples:
  "OutroCallToAction": "Grab these deals now - prices won't last! Links below!"

# Product Descriptions
- Each MAX 9 seconds when read aloud
- Format: Brief feature + benefit + wow factor
- Example:
  "#3 Bose QuietComfort: Industry-leading noise cancellation meets 
   24-hour battery life. Perfect for long flights, and thousands 
   of 5-star reviews prove it!"
```

---

### Step 8: SEO & Optimization Scoring
**Purpose:** Calculate content quality metrics

**Fields to Update:**
```
SEOScore → Calculated SEO score (0-100)
TitleOptimizationScore → Title quality score (0-100)
KeywordDensity → Keyword density percentage
EngagementPrediction → Predicted engagement score
LastOptimizationDate → Current date
```

---

### Step 9: Voice Generation
**Purpose:** Generate AI voice narration with EXACT timing

**Fields to Update:**
```
IntroMp3 → Google Drive URL (5 seconds - IntroHook text)
OutroMp3 → Google Drive URL (5 seconds - OutroCallToAction text)
Product1Mp3 → Google Drive URL (9 seconds - ProductNo1Description)
Product2Mp3 → Google Drive URL (9 seconds - ProductNo2Description)
Product3Mp3 → Google Drive URL (9 seconds - ProductNo3Description)
Product4Mp3 → Google Drive URL (9 seconds - ProductNo4Description)
Product5Mp3 → Google Drive URL (9 seconds - ProductNo5Description)
```

**Voice Timing Validation:**
- MUST validate each audio file duration
- Reject and regenerate if over time limit
- Total video must be under 60 seconds

---

### Step 10: Image Generation
**Purpose:** Generate intro/outro images

**Fields to Update:**
```
IntroPhoto → Generated intro image URL
OutroPhoto → Generated outro image URL
```

---

### Step 11: Text Length Validation
**Purpose:** Validate all text fits timing requirements

**STRICT VALIDATION RULES:**
```
IntroHook → MUST be ≤ 5 seconds
OutroCallToAction → MUST be ≤ 5 seconds
ProductNo1Description → MUST be ≤ 9 seconds
ProductNo2Description → MUST be ≤ 9 seconds
ProductNo3Description → MUST be ≤ 9 seconds
ProductNo4Description → MUST be ≤ 9 seconds
ProductNo5Description → MUST be ≤ 9 seconds
```

**Fields to Update on Success:**
```
TextControlStatus → "Validated"
ContentValidationStatus → "Validated"
VideoProductionRDY → "Ready"
```

**Fields to Update on Failure/Retry:**
```
ContentValidationStatus → "Regenerating"
ValidationIssues → "IntroHook: 7s (FAILED), Product3: 11s (FAILED)"
RegenerationCount → Increment by 1
```

---

### Step 12: Video Creation (JSON2Video)
**Purpose:** Create video with countdown structure

**Video Structure:**
```
Scene 1: Intro (5 seconds)
  - Visual: IntroPhoto
  - Audio: IntroMp3
  - Text: IntroHook as subtitle
  
Scene 2: Product #5 (9 seconds)
  - Visual: ProductNo1Photo
  - Audio: Product1Mp3
  - Text: ProductNo1Title (#5) + ProductNo1Description
  
Scene 3: Product #4 (9 seconds)
  - Visual: ProductNo2Photo
  - Audio: Product2Mp3
  - Text: ProductNo2Title (#4) + ProductNo2Description
  
Scene 4: Product #3 (9 seconds)
  - Visual: ProductNo3Photo
  - Audio: Product3Mp3
  - Text: ProductNo3Title (#3) + ProductNo3Description
  
Scene 5: Product #2 (9 seconds)
  - Visual: ProductNo4Photo
  - Audio: Product4Mp3
  - Text: ProductNo4Title (#2) + ProductNo4Description
  
Scene 6: Product #1 - WINNER (9 seconds)
  - Visual: ProductNo5Photo
  - Audio: Product5Mp3
  - Text: ProductNo5Title (#1 🏆) + ProductNo5Description
  
Scene 7: Outro (5 seconds)
  - Visual: OutroPhoto
  - Audio: OutroMp3
  - Text: OutroCallToAction as subtitle
```

**Fields to Update:**
```
JSON2VideoProjectID → Project ID from JSON2Video
```

**After Video Completion:**
```
FinalVideo → Video URL from JSON2Video
```

---

### Step 13: Platform Publishing

### 13a: YouTube Publishing
**Uses:** `YouTubeTitle`, `YouTubeDescription`, `YouTubeKeywords`
**Fields to Update:**
```
YouTubeURL → Published YouTube video URL
PlatformReadiness → Add "YouTube" to array
```

### 13b: TikTok Publishing  
**Uses:** `TikTokTitle`, `TikTokCaption`, `TikTokHashtags`
**Fields to Update:**
```
TikTokURL → Published TikTok URL
TikTokVideoID → TikTok video identifier
TikTokPublishID → TikTok publish ID
TikTokStatus → "PUBLISHED" or "FAILED"
TikTokUsername → Account username
PlatformReadiness → Add "TikTok" to array
```

### 13c: Instagram Publishing
**Uses:** `InstagramTitle`, `InstagramCaption`, `InstagramHashtags`
**Fields to Update:**
```
PlatformReadiness → Add "Instagram" to array
```

### 13d: WordPress Publishing
**Uses:** `WordPressTitle`, `WordPressContent`, `WordPressSEO`
**Fields to Update:**
```
PlatformReadiness → Add "WordPress" to array
```

---

### Step 14: Final Status Update
**Purpose:** Mark record as complete

**Fields to Update:**
```
Status → "Completed"
```

---

## 🚨 CRITICAL VIDEO REQUIREMENTS

### Countdown Structure (MUST FOLLOW):
```
ProductNo1 → Display as "#5" (5th place)
ProductNo2 → Display as "#4" (4th place)
ProductNo3 → Display as "#3" (3rd place)
ProductNo4 → Display as "#2" (2nd place)
ProductNo5 → Display as "#1 🏆" (WINNER)
```

### Timing Requirements (STRICT):
```
IntroHook: MAX 5 seconds (engaging hook from VideoTitle)
Product Descriptions: MAX 9 seconds each
OutroCallToAction: MAX 5 seconds (compelling CTA)
Total Video: MUST be under 60 seconds
```

### Text Transformation Examples:

#### IntroHook (from VideoTitle):
```
VideoTitle: "Top 5 Wireless Headphones 2025"
IntroHook: "Warning: The #1 headphone beats $500 models at half the price!"

VideoTitle: "Best Gaming Laptops Under $1000"
IntroHook: "You won't believe which laptop crushed our tests!"
```

#### Product Titles (with countdown):
```
Product at position 1 → "#5 Sony WH-1000XM5"
Product at position 2 → "#4 Bose QuietComfort 45"
Product at position 3 → "#3 Apple AirPods Max"
Product at position 4 → "#2 Sennheiser Momentum 4"
Product at position 5 → "#1 🏆 Sony WH-1000XM6"
```

#### OutroCallToAction:
```
"Grab these deals NOW - links below! Which one will you choose?"
"Limited time prices! Click for exclusive discounts!"
"Don't miss out - see why thousands bought #1!"
```

---

## 📋 Implementation Checklist

### Required Text Generation Updates:

1. **IntroHook Generator:**
   - Input: VideoTitle
   - Output: 5-second engaging hook
   - Must create urgency/curiosity

2. **Product Title Formatter:**
   - Add countdown numbers (#5 to #1)
   - ProductNo1 = "#5", ProductNo5 = "#1 🏆"
   - Include product model/name

3. **Product Description Timer:**
   - Validate each description ≤ 9 seconds
   - Auto-trim or regenerate if too long

4. **OutroCallToAction Generator:**
   - Transform into 5-second CTA
   - Must drive engagement/clicks

### Validation Requirements:
- [ ] IntroHook ≤ 5 seconds audio
- [ ] Each ProductDescription ≤ 9 seconds audio
- [ ] OutroCallToAction ≤ 5 seconds audio
- [ ] Total video < 60 seconds
- [ ] Countdown order correct (#5→#1)
- [ ] Product #1 marked as winner (🏆)