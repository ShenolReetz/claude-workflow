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

## ✅ Current Status (June 27, 2025)

### Working Features
- ✅ **Content Generation** - SEO keywords, viral titles, product descriptions
- ✅ **Text Quality Control** - 9-second timing validation for future voice narration
- ✅ **Amazon Affiliate Integration** - Successfully finds products and generates affiliate links
- ✅ **Video Creation** - 8-second test videos via JSON2Video API
- ✅ **Google Drive Integration** - Automatic folder creation and video upload
- ✅ **Airtable Sync** - Full read/write integration with status tracking
- ✅ **WordPress Blog** - Installed, configured, and accessible at https://reviewch3kr.com

### Today's Achievements (June 27, 2025)
- ✅ **Domain Configuration** - reviewch3kr.com DNS configured via Namecheap
- ✅ **SSL Certificate** - Let's Encrypt SSL auto-configured with Caddy
- ✅ **WordPress Setup** - Fresh installation with proper URL configuration
- ✅ **Theme Installation** - GeneratePress theme for fast, affiliate-friendly design
- ✅ **Essential Plugins** - Yoast SEO, WP Super Cache, Really Simple SSL, Classic Editor
- ✅ **Site Structure** - Categories, pages, and menu created
- ✅ **Admin Access** - Fully functional at https://reviewch3kr.com/wp-admin

### Recent Updates
- ✅ Fixed Amazon MCP product detection (`get_record_by_id` method)
- ✅ Fixed Airtable field name (`GenerationAttempts` as number type)
- ✅ Fixed Google Drive folder naming (special character handling)
- ✅ Improved error handling for workflow continuation
- ✅ **NEW**: WordPress installed on Hetzner VPS with Caddy web server
- ✅ **NEW**: Domain and SSL fully configured
- ✅ **NEW**: Basic affiliate site structure ready

## 🏗 Architecture

Built using MCP (Model Context Protocol) microservices:
- **Content Generation MCP** - SEO keywords, titles, descriptions
- **Amazon Affiliate MCP** - Product search and affiliate link generation
- **JSON2Video MCP** - Video creation and rendering
- **Google Drive MCP** - Storage and organization
- **Airtable MCP** - Workflow management
- **Text Control MCP** - Content quality validation
- **WordPress MCP** - Blog post publishing (ready for integration)

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
- **Admin URL**: https://reviewch3kr.com/wp-admin
- **Theme**: GeneratePress (free version)
- **Key Plugins**: Yoast SEO, WP Super Cache, Really Simple SSL
- **Categories**: Gaming Laptops, Car Amplifiers, Smart Home, Electronics, Home & Garden
- **Pages**: Home, About Us, Privacy Policy, Affiliate Disclosure

## 📋 Prerequisites

- Ubuntu server with Python 3.12+
- API keys for all services (see Configuration)
- Airtable base with proper schema
- Domain name with DNS configured
- WordPress installation (completed)

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/claude-workflow.git
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
- **Status**: Updated in Airtable

## 🔄 Workflow Stages

1. **Fetch** - Get pending title from Airtable
2. **Generate** - Create SEO content and product descriptions
3. **Validate** - Check content timing for voice narration
4. **Affiliate** - Find products on Amazon and generate links
5. **Video** - Create test video with JSON2Video
6. **Upload** - Save to Google Drive
7. **Blog** - Publish to WordPress (next to implement)
8. **Update** - Mark as Done in Airtable

## 🚧 TODO / Next Steps

### High Priority (Next Session)
- [ ] **WordPress MCP Integration** - Connect WordPress MCP to workflow_runner.py
- [ ] **Homepage Design** - Create professional affiliate-focused landing page
- [ ] **Blog Post Template** - Design automated post structure with affiliate links
- [ ] **Workflow Connection** - Test full pipeline with WordPress publishing

### Phase 2: Enhanced Main Flow MCP
- [ ] Implement parallel processing for faster workflow
- [ ] Add retry logic with exponential backoff
- [ ] Create Control Keywords Agent MCP
- [ ] Complete JSON2Video integration (from 99% to 100%)

### Phase 3: Full Production
- [ ] **Full Video Production** - Switch from 8-second test to 50-second full videos
- [ ] **Add Product Images** - Integrate DALL-E generated images into videos
- [ ] **Voice Narration** - Add ElevenLabs voice to videos
- [ ] **Social Media Module** - Auto-post to YouTube, TikTok, Instagram

### Phase 4: Automation & Scale
- [ ] **Batch Processing** - Handle multiple records in parallel
- [ ] **Scheduled Automation** - Cron job for hourly runs
- [ ] **Error Recovery** - Automatic retry for failed steps
- [ ] **Cost Tracking** - Monitor API usage and costs
- [ ] **Performance Metrics** - Track video engagement and conversions

### Phase 5: Advanced Features
- [ ] **A/B Testing** - Test different title formats
- [ ] **Multi-language** - Support for non-English content
- [ ] **Custom Templates** - Different video styles
- [ ] **Analytics Dashboard** - Track performance metrics
- [ ] **Email Notifications** - Alert on workflow completion/errors

## 🐛 Known Issues

1. **Amazon 503 Errors** - Normal rate limiting, ScrapingDog helps but not 100%
2. **Title Truncation** - Long titles get cut off in some places
3. **Test Mode Only** - Currently creates 8-second videos to save costs
4. **WordPress Integration** - MCP created but not yet connected to workflow

## 📈 Success Metrics

- **Processing Speed**: ~1 minute per video
- **Affiliate Success Rate**: 60-100% (varies by product availability)
- **API Costs**: Minimal in test mode (~$0.05 per video)
- **Automation Level**: 90% (pending WordPress integration)
- **WordPress Setup**: 100% complete, ready for integration

## 🛠️ Server Management

### WordPress Management
```bash
# Access WordPress files
cd /var/www/wordpress

# View Caddy logs
sudo journalctl -u caddy -f

# MySQL access
mysql -u wp_user -p wordpress_db

# PHP-FPM status
sudo systemctl status php8.3-fpm

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

# View logs
tail -f workflow.log

# Check Airtable sync
python3 src/mcp/airtable_mcp.py
```

### Domain & SSL
```bash
# Check SSL certificate
sudo caddy trust

# Reload Caddy after config changes
sudo systemctl reload caddy

# View Caddy config
cat /etc/caddy/Caddyfile
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
- ScrapingDog for Amazon scraping
- Caddy for modern web serving
- WordPress community for the CMS platform
- All the open source libraries that made this possible

## 📞 Support

For issues or questions:
- Check the logs in `src/workflow.log`
- Review error messages in Airtable records
- Check WordPress at https://reviewch3kr.com/wp-admin
- View server logs with `sudo journalctl -u caddy -f`
- Open an issue on GitHub

---

**Built with ❤️ by automation enthusiasts for content creators**

## 📅 Progress Log

### June 27, 2025
- Configured domain DNS via Namecheap
- Set up SSL with Let's Encrypt and Caddy
- Fixed WordPress URL configuration
- Installed GeneratePress theme
- Added essential plugins (SEO, Cache, SSL)
- Created site structure and categories
- Ready for WordPress MCP integration

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
