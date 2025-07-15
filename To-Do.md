# To-Do List - Voice Generation Integration v2.6

## 🔧 Critical Issues to Fix

### 1. **Airtable Voice MP3 Fields** (HIGH PRIORITY)
**Status:** ⚠️ Missing required fields
**Action Required:** Create 7 new Airtable fields

**New Fields to Create:**
- `IntroMp3` (type: URL) - Google Drive link for intro voice
- `OutroMp3` (type: URL) - Google Drive link for outro voice
- `Product1Mp3` (type: URL) - Google Drive link for product 1 voice
- `Product2Mp3` (type: URL) - Google Drive link for product 2 voice
- `Product3Mp3` (type: URL) - Google Drive link for product 3 voice
- `Product4Mp3` (type: URL) - Google Drive link for product 4 voice
- `Product5Mp3` (type: URL) - Google Drive link for product 5 voice

### 2. **Code Field Mapping Update** (HIGH PRIORITY)
**Status:** ⚠️ Code uses wrong field names
**File:** `/home/claude-workflow/src/workflow_runner.py`

**Changes needed in `generate_voice_narration()` method:**
```python
# CHANGE FROM:
results['airtable_updates']['IntroVoiceURL'] = intro_url
results['airtable_updates']['OutroVoiceURL'] = outro_url
results['airtable_updates'][f'ProductNo{i}VoiceURL'] = product_url

# CHANGE TO:
results['airtable_updates']['IntroMp3'] = intro_url
results['airtable_updates']['OutroMp3'] = outro_url
results['airtable_updates'][f'Product{i}Mp3'] = product_url
```

### 3. **Google Drive OAuth2 Authentication** (HIGH PRIORITY)
**Status:** 🚨 Service account quota exceeded
**Error:** `Service Accounts do not have storage quota. Leverage shared drives or use OAuth delegation instead.`

**Solutions:**
1. **Option A - OAuth2 User Account:** Switch from service account to OAuth2 user authentication (like YouTube integration)
2. **Option B - Shared Drive:** Create a Google Shared Drive and upload voice files there
3. **Option C - Alternative Storage:** Use AWS S3 or other cloud storage

**Recommended:** Use OAuth2 user authentication (similar to YouTube integration)

## 📋 Complete Airtable Field Structure (53 Fields)

### Core Fields (4)
- `Title` (Single line text)
- `Status` (Single select: Processing, Done, Failed)
- `VideoTitle` (Single line text)
- `FinalVideo` (URL - Google Drive video link)

### Multi-Platform Keywords (5)
- `YouTubeHashtags` (Long text)
- `InstagramHashtags` (Long text)
- `TikTokHashtags` (Long text)
- `WordPressHashtags` (Long text)
- `UniversalHashtags` (Long text)

### Voice Generation Fields (12)
**Text Fields (existing):**
- `IntroVoiceText` (Long text)
- `OutroVoiceText` (Long text)
- `ProductNo1VoiceText` → `ProductNo5VoiceText` (Long text)

**MP3 URL Fields (⚠️ NEED TO CREATE):**
- `IntroMp3` (URL)
- `OutroMp3` (URL)
- `Product1Mp3` → `Product5Mp3` (URL)

### Product Fields (30 - 6 fields × 5 products)
- `ProductNo1Title` → `ProductNo5Title` (Single line text)
- `ProductNo1Description` → `ProductNo5Description` (Long text)
- `ProductNo1Price` → `ProductNo5Price` (Number)
- `ProductNo1Rating` → `ProductNo5Rating` (Single line text)
- `ProductNo1Reviews` → `ProductNo5Reviews` (Single line text)
- `ProductNo1Score` → `ProductNo5Score` (Single line text)
- `ProductNo1AffiliateLink` → `ProductNo5AffiliateLink` (URL)
- `ProductNo1Photo` → `ProductNo5Photo` (URL)

### Platform URLs (4)
- `YouTubeURL` (URL)
- `InstagramURL` (URL)
- `TikTokURL` (URL)
- `WordPressURL` (URL)

### Control Fields (1)
- `TextControlStatus` (Single line text)

## 🧪 Testing After Changes

### 1. Test Voice Generation
```bash
python3 src/test_voice_workflow_integration.py
```

### 2. Test Complete Workflow
```bash
python3 src/workflow_runner.py
```

### 3. Test Credit Monitoring
```bash
python3 src/test_credit_monitoring.py
```

## 📊 Current Status Summary

### ✅ Working Components
- **Voice Text Generation:** Creates intro/outro/product narration text
- **ElevenLabs Integration:** Successfully generates voice files (tested with €32.32 credits)
- **Product Category Extraction:** Converts marketing titles to clean search terms
- **Amazon Scraping:** Fixed price conversion and title extraction
- **Multi-platform Keywords:** 90+ keywords across 5 platforms
- **Flow Control:** Validation and retry logic
- **Credit Monitoring:** Fixed API response parsing

### ⚠️ Needs Immediate Attention
- **Airtable Fields:** Missing 7 voice MP3 URL fields
- **Google Drive:** OAuth2 authentication for voice uploads
- **Field Mapping:** Code uses wrong field names

### 🔄 Ready for Production After Fixes
- Complete end-to-end workflow with voice generation
- JSON2Video integration with voice files
- Multi-platform publishing (YouTube, Instagram, TikTok)
- WordPress blog post creation
- API credit monitoring with email alerts

## 📅 Next Steps

1. **Create Airtable fields** (7 voice MP3 fields)
2. **Update code field mapping** (3 line changes)
3. **Fix Google Drive OAuth2** (switch from service account)
4. **Test complete workflow** with voice generation
5. **Deploy to production** 🚀

## 💡 Notes
- Voice generation core functionality is complete
- ElevenLabs API tested and working
- Google Drive quota issue is expected with service accounts
- All other workflow components are functioning correctly
- Total cost per video: ~€1.10 (including voice generation)