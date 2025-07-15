# Instagram Integration - Complete Setup Guide

## ✅ Current Status
- **Integration**: Fully implemented and ready
- **Token Status**: Valid until September 12, 2025 (59 days)
- **Username**: @reviewch3kr
- **User ID**: 24054868760841403
- **Platform**: Enabled in workflow

## 🚀 What's Been Implemented

### 1. **Instagram MCP Server** (`mcp_servers/instagram_server.py`)
- Full Instagram API integration
- Reels upload functionality
- Long-lived token support
- Business account integration

### 2. **Workflow Integration** (`src/mcp/instagram_workflow_integration.py`)
- Automatic Reel uploads from workflow
- Platform-specific caption generation
- Hashtag optimization (30 hashtags)
- Cover image selection

### 3. **Token Management** (`src/instagram_token_manager.py`)
- Long-lived token generation
- Token refresh functionality
- Expiry tracking
- Validation tools

### 4. **Auto-Refresh Script** (`src/instagram_token_refresh.py`)
- Automatic token refresh before expiry
- Can be scheduled via cron
- Logging and monitoring

## 📊 Integration Features

### Caption Generation
- Visual storytelling format
- Product countdown (5️⃣ to 1️⃣)
- Call-to-action elements
- Platform-specific hashtags

### Hashtag Strategy
- 30 Instagram-specific hashtags
- Category-based tagging
- Engagement-focused tags
- Stored in Airtable field: `InstagramHashtags`

### Upload Process
1. Video is created by JSON2Video
2. Uploaded to Google Drive
3. Instagram Reel created with video URL
4. Caption and hashtags applied
5. URL saved back to Airtable

## 🔧 Management Commands

### Check Token Status
```bash
python3 src/test_instagram_token.py
```

### Manual Token Refresh
```bash
python3 src/instagram_token_manager.py refresh
```

### Validate Token
```bash
python3 src/instagram_token_manager.py validate
```

### Setup Auto-Refresh (Cron)
```bash
python3 src/instagram_token_refresh.py --setup-cron
```

## 📅 Token Expiry Schedule

- **Current Token**: Valid until **September 12, 2025**
- **Days Remaining**: 59 days
- **Auto-Refresh**: Will trigger when < 30 days remain
- **Next Refresh**: Around August 13, 2025

## 🔗 Workflow Integration Points

### Airtable Fields Used
- `InstagramHashtags` - Platform-specific hashtags
- `InstagramURL` - Posted Reel URL
- `ProductNo1-5ImageURL` - Cover images
- `VideoURL` or `GoogleDriveURL` - Video source

### Workflow Step
- **Step 15**: Instagram Reel Upload
- Runs after YouTube upload
- Only if `instagram_enabled: true`
- Handles errors gracefully

## 🚨 Important Notes

1. **API Limits**
   - 200 API calls/hour
   - ~25 uploads/day
   - Respect Instagram content policies

2. **Token Security**
   - Tokens stored in config files
   - Not committed to version control
   - Refresh tokens before expiry

3. **Business Account Required**
   - Instagram must be linked to Facebook Page
   - Must be Business/Creator account
   - Proper permissions needed

## 📝 Testing

Run test upload:
```bash
python3 src/test_instagram_validation.py
```

This will:
- Verify token is valid
- Test caption generation
- Check integration readiness
- Not actually upload (dry run)

## ✅ Checklist

- [x] Instagram MCP server implemented
- [x] Workflow integration complete
- [x] Long-lived token obtained
- [x] Token management tools created
- [x] Auto-refresh script ready
- [x] Documentation complete
- [x] Integration enabled in config
- [x] Token valid for 59 days

## 🎉 Ready for Production!

Instagram integration is fully operational and will automatically:
- Upload Reels for each video
- Generate optimized captions
- Apply 30 relevant hashtags
- Track URLs in Airtable
- Refresh tokens automatically

No further action needed until token refresh in ~30 days!