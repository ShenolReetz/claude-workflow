# Claude Workflow - Automated Video Content Pipeline

**Last Updated:** June 25, 2025  
**Project Status:** 85% Complete - Social Media Integration Pending  
**Production Ready:** No - Testing Phase

## 🎯 Project Overview

An automated content creation pipeline that generates YouTube-style "Top 5" product videos with affiliate monetization. The system takes topic ideas from Airtable and produces complete videos ready for multi-platform distribution.

### Business Model
- **Input:** Topic from Airtable (e.g., "Top 5 Gaming Laptops 2025")
- **Output:** Complete monetized video with affiliate links
- **Revenue:** Amazon affiliate commissions + ad revenue

### Core Workflow
```
Airtable → Content Generation → Quality Control → Affiliate Links → Image/Voice → Video → Google Drive → Social Media → Done
```

## 🏗️ System Architecture

### MCP (Model Context Protocol) Servers
1. **Airtable MCP** ✅ - Database operations and workflow management
2. **Content Generation MCP** ✅ - SEO keywords, titles, descriptions, scripts
3. **Text Control MCP** ✅ - Quality control and timing validation (9-second rule)
4. **Amazon Affiliate MCP** ✅ - Product search and affiliate link generation
5. **Image Generation MCP** ✅ - OpenAI DALL-E integration (disabled for testing)
6. **Voice Generation MCP** ✅ - ElevenLabs text-to-speech (disabled for testing)
7. **JSON2Video MCP** ✅ - Video compilation and rendering
8. **Google Drive MCP** ✅ - Storage and folder organization
9. **Social Media MCP** ❌ - Not implemented yet

### Project Structure
```
/home/claude-workflow/
├── config/
│   ├── api_keys.json                    # All API credentials
│   └── google_drive_credentials.json    # Google OAuth credentials
├── mcp_servers/
│   ├── airtable_server.py              ✅ Complete
│   ├── content_generation_server.py     ✅ Complete (uses REAL products)
│   ├── text_generation_control_server.py ✅ Complete (9-second validation)
│   ├── amazon_affiliate_server.py       ✅ Complete (503 errors normal)
│   ├── scrapingdog_amazon_server.py     🔧 Rate limit issues (429)
│   ├── image_generation_server.py       ✅ Complete (disabled for testing)
│   ├── voice_generation_server.py       ✅ Complete (disabled for testing)
│   └── json2video_server.py            ✅ Complete (8-second test videos)
├── src/
│   ├── workflow_runner.py              ✅ Main orchestrator
│   ├── load_config.py                  ✅ Configuration loader
│   └── mcp/
│       ├── keywords_agent_mcp.py       ✅ Complete
│       ├── amazon_affiliate_agent_mcp.py ✅ Complete
│       ├── text_generation_control_agent_mcp_v2.py ✅ v2 with regeneration
│       ├── json2video_agent_mcp.py     ✅ Complete
│       ├── google_drive_agent_mcp.py   ✅ Complete
│       └── optimized_amazon_mcp.py     🆕 To be implemented (June 25)
└── test files...
```

## 📊 Current Implementation Status

### ✅ FULLY WORKING Components

#### 1. Content Generation Pipeline
- **SEO Keywords:** Generates 20 keywords per topic
- **Title Optimization:** Creates engaging social media titles (e.g., "🔥 5 INSANE Products You Need!")
- **Countdown Scripts:** Generates 5 products with descriptions
- **Real Products:** Now uses ACTUAL Amazon products (Canon BG-R10, Nikon MB-N11, etc.)
- **Blog Generation:** Implemented but disabled for testing

#### 2. Text Quality Control
- **9-Second Rule:** Validates each product can be read in 9 seconds
- **Automatic Regeneration:** Re-generates non-compliant products (max 3 attempts)
- **Keyword Integration:** Ensures SEO keywords are included
- **Status:** Version 2 fully implemented

#### 3. Amazon Affiliate Integration
- **Structure:** ✅ Complete
- **Link Format:** `https://www.amazon.com/dp/ASIN/ref=nosim?tag=reviewch3kr0d-20`
- **Associate ID:** reviewch3kr0d-20
- **Known Issues:** Amazon 503 blocking (expected behavior)
- **ScrapingDog:** 429 rate limit errors (needs fix)

#### 4. Video Creation (JSON2Video)
- **Status:** Fully working
- **Test Mode:** 8-second videos (minimal cost)
- **Production Mode:** 50-second videos (not enabled)
- **Format:** 9:16 vertical for social media
- **API Key:** Configured and working

#### 5. Google Drive Integration
- **Folder Structure:** `/N8N Projects/[Video Title]/Video|Photos|Audio`
- **Video Upload:** Working
- **URL Storage:** Saves to Airtable
- **Authentication:** OAuth2 configured

### ⚠️ DISABLED FOR TESTING (But Implemented)
- **Image Generation:** OpenAI DALL-E (to save tokens)
- **Voice Generation:** ElevenLabs (to save credits)
- **Blog Posts:** Full articles (to save tokens)

### ❌ NOT IMPLEMENTED
- **Social Media Posting:** YouTube, TikTok, Instagram
- **Batch Processing:** Multiple records at once
- **Scheduling:** Automated runs
- **API Usage Monitoring:** Credit tracking across services

## 🔧 Current Issues & Solutions

### 1. ScrapingDog 429 Rate Limit Errors
**Problem:** Too many requests causing 429 errors  
**Current Status:** Using free tier (1,000 credits/month)  
**Solution Being Implemented (June 25):**
- Rate limiting to 5 requests/minute
- 12-second delays between requests
- 2-minute cooldown on 429 errors
- Will increase limits with paid plan

### 2. Amazon 503 Errors
**Status:** Expected behavior - Amazon blocks automated requests  
**Impact:** Some products won't get affiliate links  
**Workaround:** ScrapingDog API (when not rate limited)

### 3. Missing Airtable Fields
**Fixed Fields:**
- TextControlStatus → Not needed (can remove from code)
- TextControlAttempts → Use GenerationAttempts instead
- All ProductNo[1-5] fields exist

### 4. Status Updates
**Current:** Status stays "Processing" throughout workflow  
**Future:** Will change to "Done" only after social media posting

## 📋 Airtable Schema

### "Video Titles" Table
```
Input Fields:
- Title (Long text) - Main topic
- Status (Single select) - Pending/Processing/Done/Error
- Category (Single select) - Electronics/Gaming/etc.

Generated Content:
- KeyWords (Long text) - 20 SEO keywords
- VideoTitle (Single line) - Optimized for social media
- VideoDescription (Long text) - Video description

Products (1-5):
- ProductNo[1-5]Title - Product names
- ProductNo[1-5]Description - Product details
- ProductNo[1-5]AffiliateLink - Amazon affiliate URLs
- ProductNo[1-5]ImageURL - Generated product images
- ProductNo[1-5]AudioURL - Voice narration files

Media:
- FinalVideo - JSON2Video URL
- GoogleDriveURL - Drive video link
- MovieID - JSON2Video project ID
- GenerationAttempts - Retry counter
```

## 🚀 Next Implementation Priority (June 25, 2025)

### Enhanced Amazon Integration with Image Scraping
**File:** `/home/claude-workflow/src/mcp/optimized_amazon_mcp.py`

**Features to implement:**
1. Fix ScrapingDog rate limiting (5 req/min)
2. Generate proper affiliate links
3. Scrape one Amazon product photo per product
4. Save as: `OriginalPhoto_[Product-Name]_main.jpg`
5. Store in: `/N8N Projects/[Project Name]/Affiliate Photos/`
6. Use scraped photos as reference for AI generation
7. Create ultra-high quality 1:1 AI product images

**Implementation ready** - Code provided in conversation

## 🔮 Future Development Roadmap

### Phase 1: Complete Amazon Integration (Current)
- [x] Affiliate link generation
- [ ] Product photo scraping
- [ ] AI image generation with reference
- [ ] Rate limit handling

### Phase 2: Enable Full Media Generation
- [ ] Enable image generation for all products
- [ ] Enable voice generation (intro/outro/products)
- [ ] Test full 50-second video production

### Phase 3: Social Media Integration
- [ ] YouTube API integration
- [ ] TikTok API integration
- [ ] Instagram/Facebook Graph API
- [ ] Automated posting logic

### Phase 4: Production Automation
- [ ] Batch processing (multiple records)
- [ ] Scheduled runs (cron jobs)
- [ ] Error recovery and retry logic
- [ ] API usage monitoring MCP

### Phase 5: Scaling & Optimization
- [ ] Parallel processing optimization
- [ ] Cost optimization strategies
- [ ] Analytics and reporting
- [ ] A/B testing for content

## 🔑 API Services & Configuration

### Required Services
| Service | Purpose | Status | Notes |
|---------|---------|---------|-------|
| Anthropic Claude | Content generation | ✅ Working | Need credits |
| OpenAI | Image generation | ✅ Working | Disabled for testing |
| ElevenLabs | Voice synthesis | ✅ Working | Disabled for testing |
| Airtable | Database | ✅ Working | Base: appTtNBJ8dAnjvkPP |
| JSON2Video | Video creation | ✅ Working | 8-sec test mode |
| Google Drive | Storage | ✅ Working | OAuth configured |
| Amazon Associates | Affiliate links | ✅ Working | ID: reviewch3kr0d-20 |
| ScrapingDog | Amazon scraping | ⚠️ Rate limited | Free tier: 1k/month |

### Configuration File
```json
{
    "anthropic_api_key": "sk-ant-api03-...",
    "openai_api_key": "sk-proj-...",
    "airtable_api_key": "patuus6XXiHK6EP8j...",
    "airtable_base_id": "appTtNBJ8dAnjvkPP",
    "airtable_table_name": "Video Titles",
    "elevenlabs_api_key": "sk_97bbe6a3ba3f7861...",
    "json2video_api_key": "s9gn6aT4AS...FJKd",
    "amazon_associate_id": "reviewch3kr0d-20",
    "scrapingdog_api_key": "685b2b45ce0d20b7a6a43a6f",
    "google_drive_credentials": "/app/config/google_drive_credentials.json"
}
```

## 💻 Development Environment

- **Server:** Ubuntu 24.04 LTS
- **IP:** 78.47.18.45
- **Python:** 3.12+
- **Key Libraries:** httpx, beautifulsoup4, anthropic, openai, google-api-python-client

## 🧪 Testing Strategy

### Current Test Mode
- Single product processing (Product #5 only)
- 8-second test videos
- Disabled image/voice generation
- Blog generation disabled

### Production Mode (Future)
- All 5 products
- Full 50-second videos
- Complete media generation
- Blog post creation

## 📝 Common Commands

```bash
# Run workflow for next pending title
cd /home/claude-workflow/src
python3 workflow_runner.py

# Test mode (if implemented)
python3 workflow_runner.py --test

# Check specific MCP
python3 /home/claude-workflow/mcp_servers/amazon_affiliate_server.py

# Monitor logs
tail -f /var/log/claude-workflow.log

# Check Airtable updates
# Visit: https://airtable.com/appTtNBJ8dAnjvkPP
```

## 🐛 Troubleshooting

### ScrapingDog 429 Errors
- Reduce requests per minute
- Add longer delays
- Check credit usage
- Upgrade plan if needed

### Amazon 503 Errors
- Normal behavior
- Use ScrapingDog instead
- Manual ASIN mapping as fallback

### Missing Airtable Fields
- Check field names match exactly
- Ensure field types are correct
- Add any missing fields

### Google Drive Issues
- Check OAuth credentials
- Verify folder permissions
- Ensure API is enabled

## 📞 Support & Resources

- **ScrapingDog Docs:** https://docs.scrapingdog.com/amazon-scraper-api/
- **Anthropic API:** https://docs.anthropic.com/
- **JSON2Video:** Contact support for documentation
- **Amazon Associates:** https://affiliate-program.amazon.com/

## 🎯 Success Metrics

- **Workflow Completion Rate:** Currently ~80% (Amazon blocking)
- **Video Generation Success:** 100%
- **Google Drive Upload:** 100%
- **Average Processing Time:** ~3 minutes per video
- **API Costs:** Minimal in test mode

## 📌 Critical Notes for Next Session

1. **Priority:** Implement optimized_amazon_mcp.py with rate limiting
2. **ScrapingDog:** Currently on free tier, will upgrade after testing
3. **Test First:** Always test with single record before batch processing
4. **Token Saving:** Keep image/voice disabled until Amazon integration complete
5. **Folder Structure:** Must be `/N8N Projects/[Project]/Affiliate Photos/`
6. **Image Quality:** AI images must be 1:1 photorealistic matches

---

**Project maintained by:** Shenol Reetz  
**Role:** Automation Developer  
**Approach:** AI agents, Claude MCPs, scalable content pipelines
# Temporary change
