# 🖥️ Frontend Monitoring App Specification

**Project:** Claude Workflow - Automated Content Generation System  
**Purpose:** Real-time monitoring dashboard for complete workflow oversight  
**Last Updated:** August 3, 2025

---

## 📊 **DASHBOARD OVERVIEW**

### **Main Dashboard Layout:**
1. **System Status Overview** (Top bar)
2. **Workflow Progress** (Main center panel)
3. **API Status Panel** (Left sidebar)
4. **Content Generation Status** (Right sidebar)
5. **Error Logs & Alerts** (Bottom panel)
6. **Performance Metrics** (Floating widgets)

---

## 🔑 **1. API TOKEN MONITORING**

### **Authentication Status Dashboard**
**Location:** Left Sidebar - "API Tokens" section

#### **Critical API Tokens to Monitor:**

1. **Anthropic Claude API**
   - ✅/❌ Token validity
   - 💰 Remaining credits/usage
   - 📊 Requests per hour/day
   - ⚠️ Rate limit warnings
   - 📅 Last successful call
   - 🔄 Auto-refresh status

2. **OpenAI API**
   - ✅/❌ Token status
   - 💰 Credit balance
   - 📊 Image generation quota used
   - ⚠️ Daily limit warnings
   - 📈 Cost per image generated
   - 🖼️ Total images generated today

3. **ElevenLabs Voice API**
   - ✅/❌ Authentication status
   - 🎤 Character quota remaining
   - 📊 Voice generation usage
   - ⚠️ Monthly limit alerts
   - 🔊 Audio files generated today
   - 💰 Current billing cycle usage

4. **JSON2Video API**
   - ✅/❌ API connection status
   - 🎬 Video generation quota
   - 📊 Active projects count
   - ⏱️ Average processing time
   - 💰 Credits remaining
   - 🎥 Videos created today

5. **ScrapingDog API**
   - ✅/❌ Service availability
   - 📊 Requests made today
   - ⚠️ Rate limit status
   - 🔍 Successful scrape rate
   - 💰 API credits remaining
   - 🛒 Amazon products scraped

6. **Google Drive OAuth**
   - ✅/❌ Token validity
   - ⏰ Token expiry countdown
   - 🔄 Auto-refresh status
   - 📁 Storage quota used
   - 📊 Files uploaded today
   - ⚠️ Refresh token expiry warnings

7. **Airtable API**
   - ✅/❌ Connection status
   - 📊 API calls made today
   - ⚠️ Rate limit warnings
   - 🔄 Record update success rate
   - 📋 Total records processed
   - 💰 Monthly usage

### **Social Media Platform APIs:**

8. **YouTube API**
   - ✅/❌ Authentication status
   - 📊 Daily upload quota
   - 🎥 Videos uploaded today
   - ⚠️ Policy compliance status
   - 📈 Channel performance metrics

9. **Instagram API**
   - ✅/❌ Token validity
   - 📊 Daily posting limits
   - 📸 Content uploaded today
   - ⚠️ Privacy mode status
   - 🔄 Token refresh schedule

10. **WordPress API**
    - ✅/❌ Site connectivity
    - 📝 Posts published today
    - 🔗 Link functionality
    - 📊 Site performance status

---

## 🔄 **2. WORKFLOW PROGRESS MONITORING**

### **Real-Time Workflow Tracker**
**Location:** Main Center Panel - "Current Workflow" section

#### **Step-by-Step Progress Indicators:**

1. **Title Selection & Validation**
   - 📋 Current title being processed
   - 🆔 Airtable record ID
   - ⏰ Processing start time
   - ✅/❌ Amazon product validation status
   - 🔢 Products found count
   - ⭐ Average product rating
   - 👥 Average review count

2. **Content Generation Phase**
   - 🎯 Keyword generation status
   - 📝 Platform titles creation
   - 📄 Platform descriptions generation
   - 🎬 Video title optimization
   - 📊 SEO scores per platform
   - ⏱️ Content timing validation
   - 🔄 Regeneration attempts (if any)

3. **Timing Security Check**
   - 🛡️ Security agent status
   - ⏱️ IntroHook timing (≤5s)
   - ⏱️ OutroCallToAction timing (≤5s)
   - ⏱️ Product descriptions timing (≤9s each)
   - 🔄 Auto-regeneration count
   - ✅ Final validation status
   - 📊 Total estimated video time

4. **Media Asset Generation**
   - 🎤 Voice file generation progress (7 files)
   - 🎨 Intro image generation status
   - 🖼️ Outro image generation status
   - 📸 Product images download status
   - ☁️ Google Drive upload status
   - 📁 File organization completion

5. **Video Production**
   - 🎬 JSON2Video project creation
   - 📊 Project ID tracking
   - ⏱️ Processing time estimation
   - 🔍 Status monitoring (5min + 1min intervals)
   - ❌ Error detection and reporting
   - ✅ Video completion confirmation

6. **Multi-Platform Publishing**
   - 📺 YouTube upload status
   - 📸 Instagram posting status
   - 📝 WordPress blog publication
   - 🎵 TikTok status (commented out)
   - 📊 Publishing success rates
   - 🔗 Generated content links

---

## 📊 **3. AIRTABLE COLUMN POPULATION TRACKING**

### **Database Field Monitor**
**Location:** Right Sidebar - "Database Status" section

#### **107 Fields Organized by Category:**

1. **Core Title Fields**
   - ✅ Title (populated on selection)
   - ✅ ID (sequential processing)
   - ✅ Status (Pending → Processing → Completed)
   - ⏰ Last update timestamp

2. **Video Content Fields**
   - ✅ VideoTitle
   - ✅ VideoTitleStatus (Pending → Ready)
   - ✅ VideoDescription  
   - ✅ VideoDescriptionStatus (Pending → Ready)
   - ✅ IntroHook (≤5s validation)
   - ✅ OutroCallToAction (≤5s validation)
   - ✅ VideoScript (complete countdown)

3. **Product Fields (ProductNo1-5)**
   - ✅ ProductNoXTitle (5 products)
   - ✅ ProductNoXTitleStatus (Pending → Ready)
   - ✅ ProductNoXDescription (≤9s each)
   - ✅ ProductNoXDescriptionStatus (Pending → Ready)
   - ✅ ProductNoXPhoto (Amazon URLs)
   - ✅ ProductNoXPhotoStatus (Pending → Ready)
   - ✅ ProductNoXPrice (numeric values)
   - ✅ ProductNoXRating (4.0-5.0 scale)
   - ✅ ProductNoXReviews (review counts)
   - ✅ ProductNoXAffiliateLink (Amazon links)

4. **Audio Files Fields**
   - ✅ IntroMp3 (Google Drive URL)
   - ✅ OutroMp3 (Google Drive URL)
   - ✅ Product1Mp3 → Product5Mp3 (5 files)
   - 📊 Audio generation success rate

5. **Image Fields**
   - ✅ IntroPhoto (OpenAI generated)
   - ✅ OutroPhoto (OpenAI generated)
   - 📊 Image generation success rate
   - ☁️ Google Drive storage status

6. **Video Production Fields**
   - ✅ JSON2VideoProjectID
   - ✅ FinalVideo (completion URL)
   - ✅ GenerationAttempts (retry count)
   - ⏱️ Video processing status

7. **Platform Content Fields**
   - ✅ YouTubeTitle, YouTubeDescription, YouTubeKeywords
   - ✅ InstagramTitle, InstagramCaption, InstagramHashtags
   - ✅ WordPressTitle, WordPressContent, WordPressSEO
   - ✅ TikTokTitle, TikTokDescription, TikTokKeywords
   - ✅ UniversalKeywords

8. **Publishing Status Fields**
   - ✅ YouTubeURL (published video link)
   - ✅ TikTokURL, TikTokVideoID, TikTokPublishID
   - ✅ TikTokStatus (PROCESSING/PUBLISHED/FAILED)
   - ✅ VideoProductionRDY (Ready status)

9. **Analytics & SEO Fields**
   - ✅ SEOScore (optimization rating)
   - ✅ TitleOptimizationScore (title quality)
   - ✅ KeywordDensity (SEO density)
   - ✅ EngagementPrediction (expected performance)
   - ✅ RegenerationCount (content improvements)

10. **Quality Control Fields**
    - ✅ ContentValidationStatus (Draft/Validated/Failed)
    - ✅ ValidationIssues (error descriptions)
    - ✅ TextControlStatus (timing validation)
    - ✅ LastOptimizationDate (last update)

---

## 🎯 **4. CONTENT GENERATION MONITORING**

### **AI Content Quality Dashboard**
**Location:** Right Sidebar - "Content Quality" section

#### **Content Generation Metrics:**

1. **Text Generation Quality**
   - 📝 Content originality score
   - 🎯 Keyword optimization rating
   - ⏱️ Timing compliance rate
   - 🔄 Regeneration frequency
   - 📊 SEO effectiveness score

2. **Voice Generation Status**
   - 🎤 Voice quality rating
   - ⏱️ Audio duration accuracy
   - 🔊 Volume consistency
   - 📊 Generation success rate
   - 💰 Cost per audio file

3. **Image Generation Quality**
   - 🎨 Image generation success rate
   - 📐 Resolution compliance (1080x1920)
   - 🖼️ Content relevance score
   - 💰 Cost per image
   - 🔄 Regeneration attempts

4. **Video Assembly Status**
   - 🎬 Scene composition success
   - ⏱️ Total video duration (≤60s)
   - 🔄 Processing retries
   - ✅ Quality validation score
   - 📊 Completion success rate

---

## ⚠️ **5. ERROR MONITORING & ALERTS**

### **Real-Time Error Dashboard**
**Location:** Bottom Panel - "System Alerts" section

#### **Critical Error Categories:**

1. **API Failures**
   - 🔴 Token expiration alerts
   - 🟡 Rate limit warnings
   - 🔵 Service downtime notifications
   - 💰 Credit depletion alerts
   - 🔄 Auto-recovery attempts

2. **Content Generation Errors**
   - ❌ Text generation failures
   - 🎤 Voice synthesis errors
   - 🖼️ Image generation failures
   - 🎬 Video assembly errors
   - 🔄 Retry attempt tracking

3. **Database Errors**
   - 📊 Airtable connection issues
   - 🔄 Update failure alerts
   - 📋 Field validation errors
   - 🔒 Permission denied warnings
   - 📈 Query performance issues

4. **Storage Errors**
   - ☁️ Google Drive upload failures
   - 📁 File organization errors
   - 💾 Storage quota warnings
   - 🔗 Broken file links
   - 🔄 Sync failure alerts

5. **Publishing Errors**
   - 📺 YouTube upload failures
   - 📸 Instagram posting errors
   - 📝 WordPress publishing issues
   - 🚫 Platform policy violations
   - 🔗 Link generation failures

---

## 📈 **6. PERFORMANCE METRICS**

### **System Performance Dashboard**
**Location:** Floating Widgets - "Performance" section

#### **Key Performance Indicators:**

1. **Processing Speed Metrics**
   - ⏱️ Average workflow completion time
   - 🚀 Step-by-step timing breakdown
   - 📊 Processing efficiency trends
   - 🔄 Queue processing speed
   - 📈 Daily throughput rates

2. **Success Rate Tracking**
   - ✅ Overall workflow success rate (target: 95%+)
   - 📊 Step-specific success rates
   - 🔄 Retry success rates
   - 📈 Weekly/monthly trends
   - 🎯 Quality assurance metrics

3. **Resource Utilization**
   - 💰 API cost tracking per workflow
   - 📊 Token consumption rates
   - ☁️ Storage utilization
   - 🔋 System resource usage
   - 📈 Cost optimization opportunities

4. **Content Quality Metrics**
   - 🎯 SEO score averages
   - ⭐ Content engagement predictions
   - 📊 Platform-specific performance
   - 🔄 Content improvement trends
   - 📈 Optimization effectiveness

---

## 🔔 **7. ALERT SYSTEM SPECIFICATIONS**

### **Multi-Level Alert System**

#### **Alert Priority Levels:**

1. **🔴 CRITICAL (Immediate Action Required)**
   - Workflow complete failure
   - Multiple API token expirations
   - Google Drive token refresh failures
   - Airtable database connectivity loss
   - JSON2Video project failures

2. **🟡 WARNING (Attention Needed)**
   - API tokens expiring within 24 hours
   - High retry rates (>20%)
   - Performance degradation (>2x normal time)
   - Storage quota >80% full
   - Individual step failures

3. **🔵 INFO (Monitoring)**
   - Workflow completion notifications
   - Daily performance summaries
   - Token refresh successes
   - New content published
   - System health checks

4. **🟢 SUCCESS (Positive Feedback)**
   - Successful workflow completions
   - Performance improvements
   - Token refreshes completed
   - Content quality improvements
   - Cost optimizations achieved

---

## 📱 **8. DASHBOARD FEATURES**

### **Interactive Elements:**

1. **Real-Time Updates**
   - WebSocket connections for live data
   - Auto-refresh every 30 seconds
   - Live progress bars
   - Dynamic status indicators
   - Real-time error notifications

2. **Historical Data Views**
   - 24-hour performance graphs
   - Weekly success rate trends
   - Monthly cost analysis
   - Quarterly improvement metrics
   - Annual performance reports

3. **Control Panel Features**
   - Manual workflow trigger buttons
   - Emergency stop functionality
   - Token refresh initiation
   - Error acknowledgment
   - System maintenance mode

4. **Export & Reporting**
   - CSV export of all metrics
   - PDF performance reports
   - Error log downloads
   - Custom date range reports
   - Automated daily summaries

---

## 🎯 **9. MONITORING ENDPOINTS**

### **API Endpoints to Monitor:**

#### **System Status Endpoints:**
- `GET /api/system/status` - Overall system health
- `GET /api/tokens/status` - All API token statuses
- `GET /api/workflow/current` - Current workflow progress
- `GET /api/errors/recent` - Recent error log
- `GET /api/performance/metrics` - Performance data

#### **Detailed Monitoring Endpoints:**
- `GET /api/airtable/field-status` - Field population status
- `GET /api/google-drive/token-status` - Drive token detailed status
- `GET /api/content/quality-metrics` - Content generation quality
- `GET /api/publishing/status` - Platform publishing status
- `GET /api/costs/tracking` - Real-time cost tracking

---

This specification provides a comprehensive framework for monitoring every aspect of the Claude Workflow system. The frontend app should provide real-time visibility into all these components, enabling proactive management and quick issue resolution.