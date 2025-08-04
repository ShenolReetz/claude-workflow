# Complete Workflow Flow Diagram

## 🚀 **CLAUDE WORKFLOW - END-TO-END PROCESS MAP**

**Last Updated:** August 4, 2025  
**Status:** ✅ Flow continuation fixed, video quality improvements implemented

### **Recent Fixes (August 4, 2025):**
- ✅ **Flow Continuation:** Publishing steps now execute after video generation
- ✅ **Product Price Display:** Fallback logic prevents $0 prices in videos  
- ✅ **Outro Quality:** Using high-resolution OpenAI images for outro
- ✅ **Outro Text:** Custom message: "Thanks for watching and the affiliate links are in the video descriptions"

```mermaid
flowchart TD
    START([🎬 WORKFLOW START<br/>python3 src/workflow_runner.py]) --> INIT[🔧 Initialize Services<br/>- Airtable Server<br/>- Content Generation<br/>- Voice Generation<br/>-Product Optimizer<br/>- Amazon Validator<br/>- Google Drive]
    
    INIT --> SELECT[📋 SELECT TITLE<br/>Query: Status='Pending'<br/>ORDER BY ID ASC LIMIT 1]
    
    SELECT --> VALIDATE[🔍 AMAZON VALIDATION<br/>Minimum 5 products required]
    
    VALIDATE -->|❌ FAIL| SKIP[⏭️ Mark as Completed<br/>Skip to next title]
    VALIDATE -->|✅ PASS| CATEGORY[🏷️ EXTRACT CATEGORY<br/>Anthropic API Call]
    
    CATEGORY --> SCRAPE[🛒 AMAZON SCRAPING<br/>Get top 5 products with details]
    
    SCRAPE --> OPTIMIZE[🔧 PRODUCT OPTIMIZATION<br/>- Optimize titles<br/>- Generate 9-sec descriptions<br/>- Countdown formatting]
    
    %% AIRTABLE SAVES - PRODUCTS
    OPTIMIZE --> SAVE1[💾 SAVE TO AIRTABLE<br/>ProductNo1-5Title<br/>ProductNo1-5Description<br/>ProductNo1-5Price<br/>ProductNo1-5Rating<br/>ProductNo1-5Reviews<br/>ProductNo1-5AffiliateLink<br/>+ Status fields = 'Ready']
    
    SAVE1 --> KEYWORDS[🔑 GENERATE KEYWORDS<br/>Universal + Platform-specific]
    
    KEYWORDS --> SAVE2[💾 SAVE TO AIRTABLE<br/>UniversalKeywords<br/>YouTubeKeywords<br/>InstagramHashtags<br/>TikTokKeywords<br/>WordPressSEO]
    
    SAVE2 --> TITLES[🎯 PLATFORM TITLES<br/>SEO-optimized from keywords]
    
    TITLES --> DESCRIPTIONS[📝 PLATFORM DESCRIPTIONS<br/>With affiliate links]
    
    DESCRIPTIONS --> SAVE3[💾 SAVE TO AIRTABLE<br/>YouTubeTitle<br/>YouTubeDescription<br/>InstagramTitle<br/>InstagramCaption<br/>WordPressTitle<br/>WordPressContent]
    
    SAVE3 --> VIDEOTITLE[🎬 OPTIMIZE VIDEO TITLE<br/>Engagement optimization]
    
    VIDEOTITLE --> INTROMIDOUTRO[🎭 GENERATE INTRO/OUTRO<br/>Product Optimizer<br/>5-second timing each]
    
    INTROMIDOUTRO --> SCRIPT[📝 CREATE COUNTDOWN SCRIPT<br/>Using optimized descriptions<br/>Perfect timing validation]
    
    SCRIPT --> SAVE4[💾 SAVE TO AIRTABLE<br/>VideoTitle<br/>VideoDescription<br/>IntroHook<br/>OutroCallToAction<br/>VideoScript]
    
    SAVE4 --> TIMING[⏱️ TIMING SECURITY CHECK<br/>Total video < 60 seconds<br/>Each segment within limits]
    
    TIMING -->|❌ FAIL| REGENERATE[🔄 AUTO-REGENERATE<br/>Content that exceeds limits]
    REGENERATE --> TIMING
    TIMING -->|✅ PASS| VOICE[🎵 VOICE GENERATION]
    
    %% VOICE GENERATION FLOW
    VOICE --> GDRIVE1[📁 CREATE GOOGLE DRIVE STRUCTURE<br/>N8N Projects/VideoTitle/<br/>├── Video/<br/>├── Photos/<br/>└── Audio/]
    
    GDRIVE1 --> VOICEINTRO[🎤 GENERATE INTRO VOICE<br/>ElevenLabs API]
    VOICEINTRO --> UPLOADINTRO[☁️ UPLOAD TO GOOGLE DRIVE<br/>Audio/intro.mp3]
    UPLOADINTRO --> SAVEINTRO[💾 SAVE TO AIRTABLE<br/>IntroMp3 = Drive URL]
    
    SAVEINTRO --> VOICEPROD1[🎤 GENERATE PRODUCT 1 VOICE<br/>ElevenLabs API]
    VOICEPROD1 --> UPLOADPROD1[☁️ UPLOAD TO GOOGLE DRIVE<br/>Audio/product_1.mp3]
    UPLOADPROD1 --> SAVEPROD1[💾 SAVE TO AIRTABLE<br/>Product1Mp3 = Drive URL]
    
    SAVEPROD1 --> VOICEPROD2[🎤 GENERATE PRODUCT 2 VOICE]
    VOICEPROD2 --> UPLOADPROD2[☁️ UPLOAD TO GOOGLE DRIVE<br/>Audio/product_2.mp3]
    UPLOADPROD2 --> SAVEPROD2[💾 SAVE TO AIRTABLE<br/>Product2Mp3 = Drive URL]
    
    SAVEPROD2 --> VOICEPROD3[🎤 GENERATE PRODUCT 3 VOICE]
    VOICEPROD3 --> UPLOADPROD3[☁️ UPLOAD TO GOOGLE DRIVE<br/>Audio/product_3.mp3]
    UPLOADPROD3 --> SAVEPROD3[💾 SAVE TO AIRTABLE<br/>Product3Mp3 = Drive URL]
    
    SAVEPROD3 --> VOICEPROD4[🎤 GENERATE PRODUCT 4 VOICE]
    VOICEPROD4 --> UPLOADPROD4[☁️ UPLOAD TO GOOGLE DRIVE<br/>Audio/product_4.mp3]
    UPLOADPROD4 --> SAVEPROD4[💾 SAVE TO AIRTABLE<br/>Product4Mp3 = Drive URL]
    
    SAVEPROD4 --> VOICEPROD5[🎤 GENERATE PRODUCT 5 VOICE]
    VOICEPROD5 --> UPLOADPROD5[☁️ UPLOAD TO GOOGLE DRIVE<br/>Audio/product_5.mp3]
    UPLOADPROD5 --> SAVEPROD5[💾 SAVE TO AIRTABLE<br/>Product5Mp3 = Drive URL]
    
    SAVEPROD5 --> VOICEOUTRO[🎤 GENERATE OUTRO VOICE<br/>ElevenLabs API]
    VOICEOUTRO --> UPLOADOUTRO[☁️ UPLOAD TO GOOGLE DRIVE<br/>Audio/outro.mp3]
    UPLOADOUTRO --> SAVEOUTRO[💾 SAVE TO AIRTABLE<br/>OutroMp3 = Drive URL]
    
    %% IMAGE GENERATION FLOW
    SAVEOUTRO --> IMAGES[🎨 IMAGE GENERATION]
    
    IMAGES --> INTROIMGGEN[🖼️ GENERATE INTRO IMAGE<br/>OpenAI DALL-E 3<br/>Teaser silhouettes approach]
    INTROIMGGEN --> INTROIMGUP[☁️ UPLOAD TO GOOGLE DRIVE<br/>Photos/intro_image.jpg]
    INTROIMGUP --> INTROIMGSAVE[💾 SAVE TO AIRTABLE<br/>IntroPhoto = Drive URL]
    
    INTROIMGSAVE --> AMAZONIMG[📸 DOWNLOAD AMAZON IMAGES<br/>All 5 product photos]
    AMAZONIMG --> AMAZONIMGUP[☁️ UPLOAD TO GOOGLE DRIVE<br/>Photos/Product1-5_amazon.jpg<br/>🔍 Reference only]
    
    AMAZONIMGUP --> OPENAIIMG1[🎨 GENERATE OPENAI IMAGE 1<br/>Using Amazon as reference<br/>Professional studio style]
    OPENAIIMG1 --> OPENAIUP1[☁️ UPLOAD TO GOOGLE DRIVE<br/>Photos/Product1_OpenAI.jpg]
    OPENAIUP1 --> OPENAISAVE1[💾 SAVE TO AIRTABLE<br/>ProductNo1Photo = Drive URL]
    
    OPENAISAVE1 --> OPENAIIMG2[🎨 GENERATE OPENAI IMAGE 2]
    OPENAIIMG2 --> OPENAIUP2[☁️ UPLOAD TO GOOGLE DRIVE<br/>Photos/Product2_OpenAI.jpg]
    OPENAIUP2 --> OPENAISAVE2[💾 SAVE TO AIRTABLE<br/>ProductNo2Photo = Drive URL]
    
    OPENAISAVE2 --> OPENAIIMG3[🎨 GENERATE OPENAI IMAGE 3]
    OPENAIIMG3 --> OPENAIUP3[☁️ UPLOAD TO GOOGLE DRIVE<br/>Photos/Product3_OpenAI.jpg]
    OPENAIUP3 --> OPENAISAVE3[💾 SAVE TO AIRTABLE<br/>ProductNo3Photo = Drive URL]
    
    OPENAISAVE3 --> OPENAIIMG4[🎨 GENERATE OPENAI IMAGE 4]
    OPENAIIMG4 --> OPENAIUP4[☁️ UPLOAD TO GOOGLE DRIVE<br/>Photos/Product4_OpenAI.jpg]
    OPENAIUP4 --> OPENAISAVE4[💾 SAVE TO AIRTABLE<br/>ProductNo4Photo = Drive URL]
    
    OPENAISAVE4 --> OPENAIIMG5[🎨 GENERATE OPENAI IMAGE 5]
    OPENAIIMG5 --> OPENAIUP5[☁️ UPLOAD TO GOOGLE DRIVE<br/>Photos/Product5_OpenAI.jpg]
    OPENAIUP5 --> OPENAISAVE5[💾 SAVE TO AIRTABLE<br/>ProductNo5Photo = Drive URL]
    
    OPENAISAVE5 --> OUTROIMG[🖼️ SET OUTRO IMAGE<br/>Use ProductNo5Photo<br/>(#1 winner image)]
    OUTROIMG --> OUTROIMGSAVE[💾 SAVE TO AIRTABLE<br/>OutroPhoto = ProductNo5Photo URL]
    
    %% VIDEO CREATION FLOW
    OUTROIMGSAVE --> VIDEOWAIT[⏳ WAIT 3 SECONDS<br/>Airtable synchronization]
    
    VIDEOWAIT --> VERIFY[🔍 VERIFY AUDIO URLS<br/>Check all 7 audio fields<br/>IntroMp3, Product1-5Mp3, OutroMp3]
    
    VERIFY -->|❌ MISSING| ABORT[❌ ABORT VIDEO CREATION<br/>Missing audio URLs]
    VERIFY -->|✅ ALL FOUND| JSON2VIDEO[🎬 JSON2VIDEO CREATION<br/>Build complete schema<br/>All placeholders replaced]
    
    JSON2VIDEO --> MONITOR[⏰ STATUS MONITORING<br/>5-minute delay + 1-minute intervals<br/>Server-friendly polling]
    
    MONITOR -->|⏳ PROCESSING| WAIT[⏳ CONTINUE MONITORING]
    WAIT --> MONITOR
    MONITOR -->|❌ ERROR| SAVEERROR[💾 SAVE TO AIRTABLE<br/>Error status and details]
    MONITOR -->|✅ COMPLETED| SAVEVIDEO[💾 SAVE TO AIRTABLE<br/>FinalVideo = JSON2Video URL<br/>JSON2VideoProjectID]
    
    %% PUBLISHING FLOW
    SAVEVIDEO --> PUBLISH[📱 MULTI-PLATFORM PUBLISHING]
    
    PUBLISH --> YOUTUBE[📹 YOUTUBE PUBLISHING<br/>Video + SEO metadata<br/>Keywords + Description]
    YOUTUBE --> YOUTUBESAVE[💾 SAVE TO AIRTABLE<br/>YouTubeURL]
    
    YOUTUBESAVE --> INSTAGRAM[📸 INSTAGRAM PUBLISHING<br/>Private video upload<br/>Hashtags + Caption]
    INSTAGRAM --> INSTAGRAMSAVE[💾 SAVE TO AIRTABLE<br/>Instagram status]
    
    INSTAGRAMSAVE --> WORDPRESS[📝 WORDPRESS PUBLISHING<br/>Blog post on main page<br/>Video + Photos + Affiliate links]
    WORDPRESS --> WORDPRESSSAVE[💾 SAVE TO AIRTABLE<br/>WordPress post URL]
    
    WORDPRESSSAVE --> FINALSTATUS[✅ FINAL STATUS UPDATE<br/>Status = 'Completed'<br/>All StatusFields = 'Ready']
    
    FINALSTATUS --> COMPLETE[🎉 WORKFLOW COMPLETE<br/>Process next title]
    
    %% ERROR HANDLING
    ABORT --> ERRORLOG[📝 LOG ERROR<br/>Continue to next title]
    SAVEERROR --> ERRORLOG
    ERRORLOG --> COMPLETE
    
    SKIP --> COMPLETE
    COMPLETE --> SELECT
    
    %% STYLING
    classDef startEnd fill:#e1f5fe,stroke:#01579b,stroke-width:3px
    classDef process fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef save fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef generate fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef upload fill:#e0f2f1,stroke:#004d40,stroke-width:2px
    classDef error fill:#ffebee,stroke:#b71c1c,stroke-width:2px
    
    class START,COMPLETE startEnd
    class SELECT,VALIDATE,CATEGORY,SCRAPE,OPTIMIZE,KEYWORDS,TITLES,DESCRIPTIONS,VIDEOTITLE,INTROMIDOUTRO,SCRIPT,TIMING,VOICE,IMAGES,VIDEOWAIT,VERIFY,JSON2VIDEO,MONITOR,PUBLISH,YOUTUBE,INSTAGRAM,WORDPRESS,FINALSTATUS process
    class SAVE1,SAVE2,SAVE3,SAVE4,SAVEINTRO,SAVEPROD1,SAVEPROD2,SAVEPROD3,SAVEPROD4,SAVEPROD5,SAVEOUTRO,INTROIMGSAVE,OPENAISAVE1,OPENAISAVE2,OPENAISAVE3,OPENAISAVE4,OPENAISAVE5,OUTROIMGSAVE,SAVEVIDEO,YOUTUBESAVE,INSTAGRAMSAVE,WORDPRESSSAVE save
    class VOICEINTRO,VOICEPROD1,VOICEPROD2,VOICEPROD3,VOICEPROD4,VOICEPROD5,VOICEOUTRO,INTROIMGGEN,OPENAIIMG1,OPENAIIMG2,OPENAIIMG3,OPENAIIMG4,OPENAIIMG5,REGENERATE generate
    class GDRIVE1,UPLOADINTRO,UPLOADPROD1,UPLOADPROD2,UPLOADPROD3,UPLOADPROD4,UPLOADPROD5,UPLOADOUTRO,INTROIMGUP,AMAZONIMGUP,OPENAIUP1,OPENAIUP2,OPENAIUP3,OPENAIUP4,OPENAIUP5 upload
    class SKIP,ABORT,SAVEERROR,ERRORLOG error
```

## 📊 **DETAILED FIELD MAPPING**

### 🎯 **AIRTABLE FIELDS USED**

#### **Core Fields**
| Field | Type | When Saved | Value Source |
|-------|------|------------|--------------|
| `Status` | singleSelect | Start + End | 'Pending' → 'Completed' |
| `VideoTitle` | multilineText | Step 8 | Optimized engagement title |
| `VideoDescription` | richText | Step 10 | Generated description |

#### **Product Fields (1-5)**
| Field Pattern | Type | When Saved | Value Source |
|---------------|------|------------|--------------|
| `ProductNo{X}Title` | singleLineText | Step 3.5 | Optimized (Brand + Model only) |
| `ProductNo{X}Description` | richText | Step 3.5 | 9-second countdown description |
| `ProductNo{X}Photo` | url | Image Gen | OpenAI generated image URL |
| `ProductNo{X}Price` | number | Step 4 | Amazon scraped price |
| `ProductNo{X}Rating` | number | Step 4 | Amazon scraped rating |
| `ProductNo{X}Reviews` | number | Step 4 | Amazon scraped review count |
| `ProductNo{X}AffiliateLink` | url | Step 4 | Generated affiliate URL |
| `ProductNo{X}TitleStatus` | singleSelect | Multiple | 'Ready' when populated |
| `ProductNo{X}DescriptionStatus` | singleSelect | Multiple | 'Ready' when populated |

#### **Audio Fields**
| Field | Type | When Saved | Value Source |
|-------|------|------------|--------------|
| `IntroMp3` | url | Voice Gen | Google Drive audio URL |
| `Product1Mp3` | url | Voice Gen | Google Drive audio URL |
| `Product2Mp3` | url | Voice Gen | Google Drive audio URL |
| `Product3Mp3` | url | Voice Gen | Google Drive audio URL |
| `Product4Mp3` | url | Voice Gen | Google Drive audio URL |
| `Product5Mp3` | url | Voice Gen | Google Drive audio URL |
| `OutroMp3` | url | Voice Gen | Google Drive audio URL |

#### **Image Fields**
| Field | Type | When Saved | Value Source |
|-------|------|------------|--------------|
| `IntroPhoto` | url | Image Gen | OpenAI intro image URL |
| `OutroPhoto` | url | Image Gen | ProductNo5Photo (winner) |

#### **Platform Fields**
| Field | Type | When Saved | Value Source |
|-------|------|------------|--------------|
| `YouTubeTitle` | singleLineText | Step 6 | SEO optimized |
| `YouTubeDescription` | multilineText | Step 6 | With affiliate links |
| `YouTubeKeywords` | multilineText | Step 5 | Generated keywords |
| `YouTubeURL` | url | Publishing | Published video URL |
| `InstagramTitle` | singleLineText | Step 6 | Platform optimized |
| `InstagramCaption` | multilineText | Step 6 | With hashtags |
| `InstagramHashtags` | multilineText | Step 5 | Generated hashtags |
| `WordPressTitle` | singleLineText | Step 6 | SEO optimized |
| `WordPressContent` | multilineText | Step 6 | Full blog post |
| `WordPressSEO` | multilineText | Step 5 | SEO keywords |

#### **SEO & Control Fields**
| Field | Type | When Saved | Value Source |
|-------|------|------------|--------------|
| `UniversalKeywords` | multilineText | Step 5 | Base SEO keywords |
| `IntroHook` | multilineText | Step 9 | 5-second intro script |
| `OutroCallToAction` | multilineText | Step 9 | 5-second outro script |
| `VideoScript` | multilineText | Step 10 | Complete countdown script |

#### **Final Output Fields**
| Field | Type | When Saved | Value Source |
|-------|------|------------|--------------|
| `FinalVideo` | url | Video Creation | JSON2Video final URL |
| `JSON2VideoProjectID` | singleLineText | Video Creation | Project tracking ID |

### 🗂️ **GOOGLE DRIVE STRUCTURE**

```
N8N Projects/
└── [Optimized Video Title]/
    ├── Video/
    │   └── final_video.mp4 (from JSON2Video)
    ├── Photos/
    │   ├── intro_image.jpg (OpenAI generated)
    │   ├── Product1_amazon.jpg (reference only)
    │   ├── Product1_OpenAI.jpg (for video)
    │   ├── Product2_amazon.jpg (reference only)
    │   ├── Product2_OpenAI.jpg (for video)
    │   ├── Product3_amazon.jpg (reference only)
    │   ├── Product3_OpenAI.jpg (for video)
    │   ├── Product4_amazon.jpg (reference only)
    │   ├── Product4_OpenAI.jpg (for video)
    │   ├── Product5_amazon.jpg (reference only)
    │   └── Product5_OpenAI.jpg (for video + outro)
    └── Audio/
        ├── intro.mp3 (ElevenLabs)
        ├── product_1.mp3 (ElevenLabs)
        ├── product_2.mp3 (ElevenLabs)
        ├── product_3.mp3 (ElevenLabs)
        ├── product_4.mp3 (ElevenLabs)
        ├── product_5.mp3 (ElevenLabs)
        └── outro.mp3 (ElevenLabs)
```

### ⚡ **API CALLS MADE**

1. **Anthropic Claude (4-6 calls)**
   - Category extraction
   - Product optimization
   - Intro/outro generation
   - Content regeneration (if needed)

2. **Amazon/ScrapingDog (1-2 calls)**
   - Product validation
   - Product details scraping

3. **ElevenLabs (7 calls)**
   - 1 intro + 5 products + 1 outro

4. **OpenAI DALL-E 3 (6 calls)**
   - 1 intro + 5 products (outro uses Product 5)

5. **JSON2Video (2+ calls)**
   - 1 create + multiple status checks

6. **Google Drive (13+ operations)**
   - Folder creation + 7 audio + 6 image uploads

7. **Platform APIs (3 calls)**
   - YouTube, Instagram, WordPress publishing

### 🎯 **CRITICAL SUCCESS POINTS**

1. **Audio URL Verification** - All 7 audio fields must have URLs before video creation
2. **Timing Validation** - Total video must be <60 seconds
3. **Product Optimization** - Titles must be clean (Brand + Model only)
4. **Field Name Alignment** - All saves use existing Airtable fields only
5. **Image Flow** - OpenAI images saved to ProductNoXPhoto, not non-existent fields

---

*This diagram represents the complete, current workflow as of your latest fixes.*