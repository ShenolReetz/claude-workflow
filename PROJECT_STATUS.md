# Claude Workflow Project Knowledge Base
*Last Updated: [DATE]*
*Version: [X.X]*

## 🎯 Project Overview
**Project Name:** Claude Workflow - Automated Video Content Pipeline
**Goal:** Automate creation of "Top 5" product videos with affiliate monetization
**Status:** 85% Complete - Social media integration pending

## 🏗️ Architecture Overview
```
Airtable → Content Generation → Images/Voice → Video → Google Drive → Social Media → Done
```

## 📁 Project Structure
```
/home/claude-workflow/
├── mcp_servers/
│   ├── airtable_server.py ✅
│   ├── content_generation_server.py ✅
│   ├── image_generation_server.py ✅ (disabled for testing)
│   ├── voice_generation_server.py ✅ (disabled for testing)
│   ├── amazon_affiliate_server.py ✅
│   ├── json2video_server.py ✅
│   └── scrapingdog_amazon_server.py 🔧 (rate limit issues)
├── src/
│   ├── workflow_runner.py ✅ (main orchestrator)
│   └── mcp/
│       ├── keywords_agent_mcp.py ✅
│       ├── amazon_affiliate_agent_mcp.py ✅
│       ├── text_generation_control_agent_mcp_v2.py ✅
│       ├── json2video_agent_mcp.py ✅
│       └── google_drive_agent_mcp.py ✅
└── config/
    └── api_keys.json
```

## 🔑 API Services & Status
| Service | Status | Notes |
|---------|---------|-------|
| Anthropic Claude | ✅ Working | Content generation |
| OpenAI DALL-E | ✅ Working | Image generation (disabled for testing) |
| ElevenLabs | ✅ Working | Voice generation (disabled for testing) |
| Airtable | ✅ Working | Database operations |
| JSON2Video | ✅ Working | Video creation |
| Google Drive | ✅ Working | Video storage |
| Amazon Affiliate | ✅ Structure OK | 503 errors expected |
| ScrapingDog | ⚠️ Rate Limited | 429 errors - need fix |

## 📊 Airtable Field Mappings
```
Video Titles Table:
- Title → Input topic
- Status → Pending/Processing/Done
- KeyWords → SEO keywords (20)
- VideoTitle → Optimized title
- VideoDescription → Video description
- ProductNo[1-5]Title → Product names
- ProductNo[1-5]Description → Product details
- ProductNo[1-5]AffiliateLink → Amazon links
- ProductNo[1-5]ImageURL → Product images (when enabled)
- ProductNo[1-5]AudioURL → Voice files (when enabled)
- FinalVideo → JSON2Video URL
- GoogleDriveURL → Drive storage link
- GenerationAttempts → Retry counter
```

## 🐛 Current Issues
1. **ScrapingDog 429 Errors**
   - Rate limit exceeded
   - Need to implement proper delays
   - API key: 685b2b45ce0d20b7a6a43a6f

2. **Missing Airtable Fields**
   - TextControlStatus (can be removed from code)
   - TextControlAttempts → Use GenerationAttempts instead

3. **Status Update**
   - Currently stays "Processing" 
   - Will change to "Done" after social media posting

## 🚀 Next Implementation Tasks
- [ ] Fix ScrapingDog rate limiting
- [ ] Implement social media posting
  - [ ] YouTube API integration
  - [ ] TikTok API integration
  - [ ] Instagram/Facebook Graph API
- [ ] Add retry logic for failed operations
- [ ] Enable image/voice generation for production
- [ ] Implement batch processing

## 💡 Quick Commands
```bash
# Test single record
cd /home/claude-workflow/src
python3 workflow_runner.py

# Check logs
tail -f /var/log/claude-workflow.log

# Test ScrapingDog
python3 test_scrapingdog.py
```

## 🔧 Recent Changes
- [DATE] Fixed Google Drive upload arguments
- [DATE] Added real Amazon product names to prompts
- [DATE] Implemented JSON2Video integration
- [DATE] Added product quality control validation

## 📝 Code Snippets for Common Tasks

### Fix ScrapingDog Rate Limiting
```python
# Add to amazon_affiliate_server.py
await asyncio.sleep(6)  # 10 requests per minute max
```

### Test Specific Record
```python
pending_title = {'record_id': 'rec0WHjB2sKcUmB1p', 'title': 'Test Product'}
```

## 🤝 Developer Notes
- Server: Ubuntu 24.04 LTS at 78.47.18.45
- Python 3.12+
- Using httpx for async requests
- Amazon Associate ID: reviewch3kr0d-20
- Test mode uses only Product #5 to save tokens

## 🔗 Important Links
- GitHub: https://github.com/ShenolReetz/claude-workflow
- Airtable Base: appTtNBJ8dAnjvkPP
- ScrapingDog Docs: https://docs.scrapingdog.com/amazon-scraper-api/
