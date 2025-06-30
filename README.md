# Claude Workflow - Automated Video Content Creation Pipeline 🚀

An automated content creation pipeline that generates YouTube-style "Top 5" product videos with affiliate monetization using AI and web scraping.

## 🎯 Project Overview

This system automatically:
- Reads topic ideas from Airtable (e.g., "Top 5 Gaming Laptops 2025")
- Generates SEO-optimized content using Claude AI
- Creates product countdown scripts with viral titles
- Fetches Amazon affiliate links for monetization
- Produces test videos using JSON2Video API (8-second demos)
- Uploads to Google Drive with organized folder structure
- Updates Airtable with video URLs and affiliate links
- **NEW**: Publishes blog posts to WordPress automatically
- **NEW**: Ready for multi-platform social media distribution

## ✅ Current Status (June 28, 2025)

### Working Features
- ✅ **Content Generation** - SEO keywords, viral titles, product descriptions
- ✅ **Text Quality Control** - 9-second timing validation for future voice narration
- ✅ **Amazon Affiliate Integration** - Successfully finds products and generates affiliate links
- ✅ **Video Creation** - 8-second test videos via JSON2Video API (99% complete)
- ✅ **Google Drive Integration** - Automatic folder creation and video upload
- ✅ **Airtable Sync** - Full read/write integration with status tracking
- ✅ **WordPress Blog** - Fully configured and live at https://reviewch3kr.com
- ✅ **Social Media Accounts** - YouTube, TikTok, Instagram all created and linked

### Today's Achievements (June 28, 2025)
- ✅ **WordPress Homepage** - Professional landing page with ReviewCh3kr banner
- ✅ **Clean Design** - Removed header for single-page focus
- ✅ **Social Media Integration** - Added proper icons with hover effects
- ✅ **YouTube Channel** - https://www.youtube.com/@ReviewCh3kr
- ✅ **TikTok Account** - https://www.tiktok.com/@reviewch3kr_
- ✅ **Instagram Profile** - https://www.instagram.com/reviewch3kr/
- ✅ **All Platforms Connected** - Social links active on website

### Infrastructure Complete
- ✅ Domain: reviewch3kr.com (SSL active)
- ✅ WordPress: GeneratePress theme, optimized for affiliate marketing
- ✅ Social Media: All platforms created and branded
- ✅ Ready for content automation

## 🏗 Architecture

Built using MCP (Model Context Protocol) microservices:
- **Content Generation MCP** - SEO keywords, titles, descriptions ✅
- **Amazon Affiliate MCP** - Product search and affiliate link generation ✅
- **JSON2Video MCP** - Video creation and rendering (99% complete)
- **Google Drive MCP** - Storage and organization ✅
- **Airtable MCP** - Workflow management ✅
- **Text Control MCP** - Content quality validation ✅
- **WordPress MCP** - Blog post publishing (created, needs integration)

## 🌐 Infrastructure

### Servers
- **Main VPS**: Hetzner (78.47.18.45)
  - Ubuntu 24.04 LTS
  - 4GB RAM
  - Python 3.12+
  - Docker installed

### Web Stack
- **Web Server**: Caddy (with automatic SSL)
- **PHP**: PHP 8.3-FPM
- **Database**: MySQL 8.0.42
- **CMS**: WordPress (latest)
- **Domain**: reviewch3kr.com (active with SSL)

### WordPress Configuration
- **Site URL**: https://reviewch3kr.com
- **Theme**: GeneratePress (free version)
- **Design**: Clean landing page, no header
- **Key Features**: 
  - ReviewCh3kr banner
  - Popular Blogs section
  - Social media integration
  - Ready for automated posts

### Social Media Presence
- **YouTube**: [@ReviewCh3kr](https://www.youtube.com/@ReviewCh3kr)
- **TikTok**: [@reviewch3kr_](https://www.tiktok.com/@reviewch3kr_)
- **Instagram**: [@reviewch3kr](https://www.instagram.com/reviewch3kr/)

## 📋 Prerequisites

- Ubuntu server with Python 3.12+
- API keys for all services (see Configuration)
- Airtable base with proper schema
- Domain name with DNS configured ✅
- WordPress installation ✅
- Social media accounts ✅

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/ShenolReetz/claude-workflow.git
cd claude-workflow

# Install dependencies
pip install --break-system-packages httpx beautifulsoup4 lxml anthropic openai google-api-python-client airtable-python-wrapper

# Copy and configure API keys
cp config/api_keys.example.json config/api_keys.json
nano config/api_keys.json

# Set up Google Drive credentials
cp config/google_drive_credentials.example.json config/google_drive_credentials.json
```

## ⚙️ Configuration

### Required API Keys
```json
{
  "anthropic_api_key": "your-claude-api-key",
  "openai_api_key": "your-openai-key",
  "airtable_api_key": "your-airtable-key",
  "airtable_base_id": "your-base-id",
  "airtable_table_name": "Video Titles",
  "elevenlabs_api_key": "your-elevenlabs-key",
  "json2video_api_key": "your-json2video-key",
  "amazon_associate_id": "your-amazon-id",
  "scrapingdog_api_key": "your-scrapingdog-key",
  "google_drive_credentials": "/path/to/credentials.json",
  "wordpress_url": "https://reviewch3kr.com",
  "wordpress_user": "automation",
  "wordpress_password": "YOUR_APPLICATION_PASSWORD",
  "wordpress_enabled": true
}
```

### Airtable Schema
Required fields in your "Video Titles" table:
- `Title` (Single line text) - Input topic
- `Status` (Single select: Pending, Processing, Done)
- `Keywords` (Long text) - SEO keywords
- `VideoTitle` (Single line text) - Optimized title
- `VideoDescription` (Long text)
- `ProductNo1Title` through `ProductNo5Title` (Single line text)
- `ProductNo1Description` through `ProductNo5Description` (Long text)
- `ProductNo1AffiliateLink` through `ProductNo5AffiliateLink` (URL)
- `GenerationAttempts` (Number) - Quality control attempts
- `VideoURL` (URL) - JSON2Video URL
- `GoogleDriveURL` (URL) - Final video location
- `BlogURL` (URL) - WordPress post URL
- `BlogPostID` (Single line text) - WordPress post ID

## 🎮 Usage

### Run Single Workflow
```bash
cd src
python3 workflow_runner.py
```

### Test Individual Components
```bash
# Test Amazon affiliate generation
python3 src/mcp/amazon_affiliate_agent_mcp.py

# Test video creation
python3 src/mcp/json2video_agent_mcp.py

# Test WordPress integration
python3 src/mcp/wordpress_mcp.py
```

## 📊 Sample Output

**Input**: "Top 5 Gaming Laptops 2025"

**Output**:
- **SEO Title**: "🔥 5 INSANE Gaming Laptops You Need in 2025! 🎮"
- **Products**: 5 gaming laptops with descriptions
- **Affiliate Links**: Amazon links for each product
- **Video**: 8-second test video
- **Blog Post**: Ready to be auto-published to WordPress
- **Social Ready**: Content formatted for YouTube, TikTok, Instagram
- **Status**: Updated in Airtable

## 🔄 Workflow Stages

1. **Fetch** - Get pending title from Airtable
2. **Generate** - Create SEO content and product descriptions
3. **Validate** - Check content timing for voice narration
4. **Affiliate** - Find products on Amazon and generate links
5. **Video** - Create test video with JSON2Video
6. **Upload** - Save to Google Drive
7. **Blog** - Publish to WordPress (next to implement)
8. **Social** - Distribute to YouTube, TikTok, Instagram (manual for now)
9. **Update** - Mark as Done in Airtable

## 🚧 TODO / Next Steps

### Immediate Priority (Next Session - June 29)
- [ ] **WordPress MCP Integration** - Connect to workflow_runner.py - DONE!
- [ ] **Complete JSON2Video** - Fix remaining 1% (template format)
- [ ] **Test Full Pipeline** - Airtable → Video → Blog → Social Ready

### Phase 2: Enhanced Automation
- [ ] **Parallel Processing** - Speed up workflow execution
- [ ] **Retry Logic** - Handle API failures gracefully
- [ ] **Control Keywords Agent** - Implement decision flow
- [ ] **Batch Processing** - Handle multiple records

### Phase 3: Full Production
- [ ] **Full Videos** - 50-second videos with all products
- [ ] **Voice Integration** - Add ElevenLabs narration
- [ ] **Image Generation** - DALL-E product images
- [ ] **Auto Social Posting** - Direct upload to platforms

### Phase 4: Scale & Monitor
- [ ] **Scheduled Runs** - Cron job automation
- [ ] **Cost Tracking** - API usage monitoring
- [ ] **Analytics Dashboard** - Performance metrics
- [ ] **A/B Testing** - Title optimization

## 🐛 Known Issues

1. **Amazon 503 Errors** - Normal rate limiting, ScrapingDog helps
2. **JSON2Video Template** - 99% complete, needs final format adjustment
3. **WordPress MCP** - Created but not integrated with workflow
4. **Manual Social Posting** - Automation pending API setup

## 📈 Success Metrics

- **Infrastructure**: 100% complete (Domain, WordPress, Social)
- **Automation Pipeline**: 85% complete
- **Content Generation**: 100% working
- **Video Creation**: 99% working
- **Publishing**: Ready for integration

## 🛠️ Server Management

### WordPress Management
```bash
# Access WordPress files
cd /var/www/wordpress

# View Caddy logs
sudo journalctl -u caddy -f

# WP-CLI commands
wp plugin list
wp theme list
wp option get siteurl
```

### Workflow Management
```bash
# Run workflow
cd /home/claude-workflow/src
python3 workflow_runner.py

# Check logs
tail -f workflow.log
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Claude AI for content generation
- JSON2Video for video creation
- WordPress community
- All open source contributors

## 📞 Support

For issues or questions:
- Check logs: `src/workflow.log`
- WordPress: https://reviewch3kr.com/wp-admin
- GitHub Issues: https://github.com/ShenolReetz/claude-workflow/issues

---

**Built with ❤️ by automation enthusiasts for content creators**

## 📅 Progress Log

### June 28, 2025
- Completed WordPress homepage design
- Added ReviewCh3kr banner
- Configured social media icons with hover effects
- Created YouTube channel @ReviewCh3kr
- Created TikTok account @reviewch3kr_
- Created Instagram profile @reviewch3kr
- Linked all social media on website
- Infrastructure 100% complete

### June 27, 2025
- Configured domain DNS via Namecheap
- Set up SSL with Let's Encrypt and Caddy
- Fixed WordPress URL configuration
- Installed GeneratePress theme
- Added essential plugins (SEO, Cache, SSL)
- Created site structure and categories

### June 26, 2025
- WordPress installation completed
- Fixed various workflow bugs
- Amazon affiliate integration working
- Video creation pipeline functional

### Previous
- Initial workflow setup
- MCP architecture implementation
- Airtable integration
- Basic automation pipeline
