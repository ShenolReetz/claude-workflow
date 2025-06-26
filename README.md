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

## ✅ Current Status (June 26, 2025)

### Working Features
- ✅ **Content Generation** - SEO keywords, viral titles, product descriptions
- ✅ **Text Quality Control** - 9-second timing validation for future voice narration
- ✅ **Amazon Affiliate Integration** - Successfully finds products and generates affiliate links
- ✅ **Video Creation** - 8-second test videos via JSON2Video API
- ✅ **Google Drive Integration** - Automatic folder creation and video upload
- ✅ **Airtable Sync** - Full read/write integration with status tracking

### Recent Fixes Applied
- ✅ Fixed Amazon MCP product detection (`get_record_by_id` method)
- ✅ Fixed Airtable field name (`GenerationAttempts` as number type)
- ✅ Fixed Google Drive folder naming (special character handling)
- ✅ Improved error handling for workflow continuation

## 🏗 Architecture

Built using MCP (Model Context Protocol) microservices:
- **Content Generation MCP** - SEO keywords, titles, descriptions
- **Amazon Affiliate MCP** - Product search and affiliate link generation
- **JSON2Video MCP** - Video creation and rendering
- **Google Drive MCP** - Storage and organization
- **Airtable MCP** - Workflow management
- **Text Control MCP** - Content quality validation

## 📋 Prerequisites

- Ubuntu server with Python 3.12+
- API keys for all services (see Configuration)
- Airtable base with proper schema

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

  "anthropic_api_key": "your-claude-api-key",
  "openai_api_key": "your-openai-key",
  "airtable_api_key": "your-airtable-key",
  "airtable_base_id": "your-base-id",
  "airtable_table_name": "Video Titles",
  "elevenlabs_api_key": "your-elevenlabs-key",
  "json2video_api_key": "your-json2video-key",
  "amazon_associate_id": "your-amazon-id",
  "scrapingdog_api_key": "your-scrapingdog-key",
  "google_drive_credentials": "/path/to/credentials.json"
}
Airtable Schema
Required fields in your "Video Titles" table:

Title (Single line text) - Input topic
Status (Single select: Pending, Processing, Done)
Keywords (Long text) - SEO keywords
VideoTitle (Single line text) - Optimized title
VideoDescription (Long text)
ProductNo1Title through ProductNo5Title (Single line text)
ProductNo1Description through ProductNo5Description (Long text)
ProductNo1AffiliateLink through ProductNo5AffiliateLink (URL)
GenerationAttempts (Number) - Quality control attempts
VideoURL (URL) - JSON2Video URL
GoogleDriveURL (URL) - Final video location

🎮 Usage
Run Single Workflow
bashcd src
python3 workflow_runner.py
Test Individual Components
bash# Test Amazon affiliate generation
python3 src/mcp/amazon_affiliate_agent_mcp.py

# Test video creation
python3 src/mcp/json2video_agent_mcp.py
📊 Sample Output
Input: "Top 5 Gaming Laptops 2025"
Output:

SEO Title: "🔥 5 INSANE Gaming Laptops You Need in 2025! 🎮"
Products: 5 gaming laptops with descriptions
Affiliate Links: Amazon links for each product
Video: 8-second test video
Status: Updated in Airtable

🔄 Workflow Stages

Fetch - Get pending title from Airtable
Generate - Create SEO content and product descriptions
Validate - Check content timing for voice narration
Affiliate - Find products on Amazon and generate links
Video - Create test video with JSON2Video
Upload - Save to Google Drive
Update - Mark as Processing in Airtable

🚧 TODO / Next Steps
High Priority

 Full Video Production - Switch from 8-second test to 50-second full videos
 Add Product Images - Integrate DALL-E generated images into videos
 Voice Narration - Add ElevenLabs voice to videos
 Social Media Module - Auto-post to YouTube, TikTok, Instagram
 Webhook Integration - Update status to "Done" after social posting

Medium Priority

 Batch Processing - Handle multiple records in parallel
 Scheduled Automation - Cron job for hourly runs
 Error Recovery - Retry failed steps automatically
 Cost Tracking - Monitor API usage and costs
 Performance Metrics - Track video engagement

Low Priority

 A/B Testing - Test different title formats
 Multi-language - Support for non-English content
 Custom Templates - Different video styles
 Analytics Dashboard - Track performance metrics

🐛 Known Issues

Amazon 503 Errors - Normal rate limiting, ScrapingDog helps but not 100%
Title Truncation - Long titles get cut off in some places
Test Mode Only - Currently creates 8-second videos to save costs

📈 Success Metrics

Processing Speed: ~1 minute per video
Affiliate Success Rate: 60-100% (varies by product availability)
API Costs: Minimal in test mode (~$0.05 per video)
Automation Level: 95% (pending social media integration)

🤝 Contributing

Fork the repository
Create your feature branch (git checkout -b feature/AmazingFeature)
Commit your changes (git commit -m 'Add some AmazingFeature')
Push to the branch (git push origin feature/AmazingFeature)
Open a Pull Request

📝 License
This project is licensed under the MIT License - see the LICENSE file for details.
🙏 Acknowledgments

Claude AI for content generation
JSON2Video for video creation
ScrapingDog for Amazon scraping
All the open source libraries that made this possible

📞 Support
For issues or questions:

Check the logs in src/workflow.log
Review error messages in Airtable records
Open an issue on GitHub


Built with ❤️ by automation enthusiasts for content creators
