# 📋 TODO - Production Workflow Development Plan
**Last Updated**: September 5, 2025  
**Project**: Automated Amazon Affiliate Video Generation System  
**Status**: 🔴 CRITICAL FIXES NEEDED

## 🎯 PROJECT OVERVIEW
Automated content generation system that creates Amazon affiliate videos and publishes to multiple platforms (YouTube, WordPress, Instagram). Current workflow processes titles from Airtable, scrapes Amazon products, generates AI content/images, creates videos, and distributes in 3-5 minutes per video.

## 📊 CURRENT STATUS
- **Working**: Amazon scraping, voice generation, video rendering (Remotion & WOW), YouTube upload
- **Broken**: Image generation (Imagen 4 blocked), expired OAuth tokens
- **Missing**: Instagram integration, monitoring dashboard, auto-recovery

---

## 🚀 DEVELOPMENT STAGES

### 🔴 STAGE 1: CRITICAL FIXES (Days 1-3)
**Priority**: CRITICAL - System Non-Functional  
**Status**: NOT STARTED

#### Day 1: Fix Image Generation Pipeline
- [ ] **Enable fal.ai fallback** (already integrated)
  - [ ] Test fal.ai FLUX image-to-image with Amazon photos
  - [ ] Verify 85-90% product accuracy
  - [ ] Cost validation: $0.03/image vs $0.06 Imagen
- [ ] **Implement intelligent fallback chain**
  ```python
  # In production_imagen4_ultra_with_gpt4_vision.py
  # Primary: Imagen 4 Ultra → Fallback: fal.ai → Emergency: DALL-E 3
  ```
- [ ] **Update error handling** for graceful degradation
- [ ] **Test complete image generation flow**

#### Day 2: Token Management & API Fixes
- [ ] **Create token refresh utility**
  - [ ] Build `src/utils/token_refresh_manager.py`
  - [ ] Refresh YouTube OAuth token (expired Aug 18)
  - [ ] Refresh Google Drive token (expired Aug 18)
  - [ ] Add daily cron job for auto-refresh
- [ ] **Fix Airtable 422 errors**
  - [ ] Debug field validation issues
  - [ ] Ensure proper data type formatting
  - [ ] Test with direct MCP tool calls
- [ ] **Fix WordPress 400 errors**
  - [ ] Verify authentication headers
  - [ ] Check post data structure
  - [ ] Test media upload limits

#### Day 3: Workflow Stabilization
- [ ] **Run complete end-to-end test**
  - [ ] Process 3 videos consecutively
  - [ ] Verify all 18 workflow phases
  - [ ] Check media storage paths
  - [ ] Validate platform publishing
- [ ] **Performance validation**
  - [ ] Target: <5 minutes per video
  - [ ] Monitor memory usage
  - [ ] Check for resource leaks
- [ ] **Document critical fixes**

---

### 🟡 STAGE 2: INSTAGRAM INTEGRATION (Days 4-7)
**Priority**: HIGH - Major Platform Missing  
**Status**: NOT STARTED

#### Day 4: Instagram API Setup
- [ ] **Configure Instagram Graph API**
  - [ ] Verify Business Account access
  - [ ] Test API endpoints
  - [ ] Set up rate limiting
- [ ] **Create test upload script**
  - [ ] Video format validation (9:16)
  - [ ] Duration check (15-60 seconds)
  - [ ] Caption length limits

#### Day 5: Build Instagram MCP Agent
- [ ] **Create `production_instagram_reels_upload.py`**
  ```python
  class InstagramReelsUploader:
      - upload_reel(video_path, caption, hashtags)
      - create_media_container()
      - wait_for_processing()
      - publish_reel()
      - generate_hashtags() # 30 relevant tags
  ```
- [ ] **Implement hashtag optimization**
  - [ ] Category-based hashtag selection
  - [ ] Trending hashtag integration
  - [ ] Engagement tracking

#### Day 6: Workflow Integration
- [ ] **Add Instagram phase to production_flow.py**
  - [ ] New phase: `WorkflowPhase.PUBLISH_INSTAGRAM`
  - [ ] Update phase dependencies
  - [ ] Enable parallel publishing
- [ ] **Content adaptation**
  - [ ] Auto-generate Instagram captions
  - [ ] Add emojis and CTAs
  - [ ] Create bio link strategy

#### Day 7: Testing & Optimization
- [ ] **Full workflow test with Instagram**
- [ ] **Cross-posting features**
  - [ ] Stories preview generation
  - [ ] IGTV for longer content
  - [ ] Carousel posts for products
- [ ] **Analytics setup**

---

### 🟢 STAGE 3: RELIABILITY & MONITORING (Days 8-10)
**Priority**: MEDIUM - System Stability  
**Status**: NOT STARTED

#### Day 8: Monitoring Dashboard
- [ ] **Create `monitoring/production_dashboard.py`**
  - [ ] Real-time workflow status display
  - [ ] API usage tracking (costs/limits)
  - [ ] Success/failure metrics
  - [ ] Performance graphs
- [ ] **Implement logging aggregation**
  - [ ] Centralized log collection
  - [ ] Error categorization
  - [ ] Trend analysis

#### Day 9: Error Recovery System
- [ ] **Automatic retry mechanisms**
  - [ ] Exponential backoff implementation
  - [ ] Circuit breaker enhancements
  - [ ] Partial workflow recovery
- [ ] **State persistence**
  - [ ] Save workflow state to Redis
  - [ ] Enable resume from failure
  - [ ] Checkpoint system

#### Day 10: Alert System
- [ ] **Critical failure notifications**
  - [ ] Email alerts for failures
  - [ ] Slack/Discord integration
  - [ ] Daily summary reports
- [ ] **Predictive monitoring**
  - [ ] Token expiry warnings
  - [ ] Storage space alerts
  - [ ] API limit approaching

---

### 🔵 STAGE 4: PERFORMANCE OPTIMIZATION (Days 11-13)
**Priority**: MEDIUM - Efficiency Gains  
**Status**: NOT STARTED

#### Day 11: Parallel Processing
- [ ] **Optimize image generation**
  - [ ] Batch API calls
  - [ ] Concurrent processing
  - [ ] Smart caching
- [ ] **Voice generation improvements**
  - [ ] Pre-generate common phrases
  - [ ] Parallel voice synthesis
  - [ ] Audio compression

#### Day 12: Video Rendering
- [ ] **Remotion optimization**
  - [ ] Template caching
  - [ ] Asset preloading
  - [ ] Render queue management
- [ ] **WOW video enhancements**
  - [ ] Effect precomputation
  - [ ] Particle system optimization
  - [ ] Review data caching

#### Day 13: Storage & Cleanup
- [ ] **Enhance cleanup system**
  - [ ] Smart age-based deletion
  - [ ] Backup before cleanup option
  - [ ] Storage analytics
- [ ] **CDN integration**
  - [ ] CloudFlare for static assets
  - [ ] Video streaming optimization

---

### 🟣 STAGE 5: ADVANCED FEATURES (Days 14-20)
**Priority**: LOW - Future Enhancements  
**Status**: NOT STARTED

#### Days 14-16: Content Intelligence
- [ ] **AI-powered optimization**
  - [ ] Trend analysis system
  - [ ] Optimal posting time prediction
  - [ ] Title A/B testing
  - [ ] Thumbnail optimization
- [ ] **Engagement prediction**
  - [ ] ML model for view prediction
  - [ ] Content scoring algorithm
  - [ ] Recommendation engine

#### Days 17-19: Multi-Platform Expansion
- [ ] **TikTok integration** (pending approval)
  - [ ] API integration prep
  - [ ] Format adaptation
  - [ ] Sound trend integration
- [ ] **Additional platforms**
  - [ ] Pinterest video pins
  - [ ] LinkedIn video posts
  - [ ] Twitter/X threads
  - [ ] Facebook Reels

#### Day 20: Analytics & Reporting
- [ ] **Comprehensive analytics**
  - [ ] Cross-platform metrics
  - [ ] ROI calculation
  - [ ] Audience insights
  - [ ] Content performance

---

### ⚡ STAGE 6: SCALABILITY (Days 21-25)
**Priority**: LOW - Growth Preparation  
**Status**: NOT STARTED

#### Days 21-23: Architecture Enhancement
- [ ] **Queue-based processing**
  - [ ] RabbitMQ/Celery integration
  - [ ] Worker pool management
  - [ ] Load balancing
- [ ] **Microservices migration**
  - [ ] Service separation
  - [ ] API gateway
  - [ ] Container orchestration

#### Days 24-25: Enterprise Features
- [ ] **Multi-tenant support**
  - [ ] Account management
  - [ ] Usage quotas
  - [ ] Billing integration
- [ ] **API exposure**
  - [ ] REST API endpoints
  - [ ] Webhook system
  - [ ] Developer documentation

---

## 📈 SUCCESS METRICS

### Technical KPIs
- ✅ **Reliability**: >95% success rate (Current: ~70%)
- ✅ **Performance**: <5 min/video (Current: 3-5 min ✅)
- ✅ **Cost**: <$0.25/video (Current: ~$0.21 ✅)
- ⏳ **Scalability**: 100+ videos/day capacity
- ⏳ **Uptime**: 99.9% availability

### Business KPIs
- ✅ **Platforms**: 3 active (YouTube ✅, WordPress ⚠️, Instagram ❌)
- ⏳ **Engagement**: 40% increase with WOW videos
- ⏳ **Automation**: 100% hands-off operation
- ⏳ **ROI**: 3x reach for same cost

---

## 🛠️ QUICK REFERENCE

### Critical Commands
```bash
# Main production workflow
python3 /home/claude-workflow/run_local_storage.py

# Test production flow
python3 /home/claude-workflow/test_production_flow.py

# Refresh OAuth tokens
python3 /home/claude-workflow/src/utils/token_refresh_manager.py

# Weekly cleanup (Sunday 7AM)
python3 /home/claude-workflow/cleanup_all_storage.py

# Monitor logs
tail -f /home/claude-workflow/workflow_local_storage.log
```

### API Status
- ✅ OpenAI GPT-4o - Working
- ✅ fal.ai - Working (fallback ready)
- ❌ Imagen 4 Ultra - Blocked (billing required)
- ✅ ElevenLabs - Working
- ✅ ScrapingDog - Working
- ✅ Airtable - Partial (update errors)
- ⚠️ YouTube OAuth - Expired (needs refresh)
- ⚠️ Google Drive - Expired (needs refresh)
- ❌ WordPress - Connection errors
- ❓ Instagram - Not implemented

### File Locations
```
/home/claude-workflow/
├── run_local_storage.py          # Main entry point
├── src/production_flow.py        # Workflow orchestrator
├── src/mcp/                      # MCP agents
├── mcp_servers/                  # MCP servers
├── config/                       # API keys & tokens
├── media_storage/                # Local media files
└── cleanup_reports/              # Cleanup logs
```

---

## 🚨 IMMEDIATE ACTIONS FOR TOMORROW

### Morning (9 AM)
1. [ ] Enable fal.ai fallback for image generation
2. [ ] Test image generation with sample product
3. [ ] Verify fallback chain works

### Afternoon (2 PM)
1. [ ] Create token refresh script
2. [ ] Refresh YouTube OAuth token
3. [ ] Refresh Google Drive token
4. [ ] Test token validity

### Evening (6 PM)
1. [ ] Fix Airtable field update errors
2. [ ] Debug WordPress connection
3. [ ] Run complete test workflow
4. [ ] Document fixes and results

---

## 📞 RESOURCES & SUPPORT

- **Google Cloud Billing**: https://console.cloud.google.com/billing
- **fal.ai Documentation**: https://fal.ai/docs
- **Instagram Graph API**: https://developers.facebook.com/docs/instagram-api
- **Airtable API**: https://airtable.com/api
- **Project Repository**: /home/claude-workflow/
- **Logs Location**: /home/claude-workflow/workflow_local_storage.log

---

**Development Start Date**: September 6, 2025  
**Target Completion**: September 30, 2025  
**Total Duration**: 25 days  
**Current Phase**: STAGE 1 - CRITICAL FIXES

## Notes
- Always run workflow with NO timeout or 30min minimum when testing
- Weekly cleanup runs automatically Sunday 7AM (deletes ALL files)
- WOW videos have 40% higher engagement but take 1-2 min longer
- Instagram integration is highest priority after critical fixes