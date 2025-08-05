# Claude Workflow Project Documentation

## 📋 **Essential Self-Update Protocol**

**⚠️ CRITICAL:** Always start by reading these organized documentation files:

### 🎯 **Required Reading for Context Updates**
1. **`/home/claude-workflow/ORGANIZED_FILES_SUMMARY.md`** - Complete file organization overview
2. **`documentation/README.md`** - Documentation structure and quick access guide  
3. **`documentation/airtable_schema/Airtable_Column_Schema.md`** - Complete database schema (107 fields)
4. **`documentation/airtable_schema/Airtable_Workflow_Mapping.md`** - Workflow field mapping and timing requirements
5. **`documentation/go_live/GO_LIVE_CHECKLIST.md`** - Production readiness status

---

## Project Status: **Production Ready v5.2**

**Last Updated:** August 4, 2025  
**Current Version:** v5.2 Flow Continuation + Video Quality Fixes  
**Architecture:** Single Production Flow + JSON2Video Status Monitoring + Active Multi-Platform Publishing + Enhanced Video Quality

### **Recent v5.2 Improvements (August 4, 2025)**
- ✅ **Flow Continuation Fix** - Publishing steps now execute after video generation regardless of monitoring outcome
- ✅ **Product Price Display** - Fixed Product #1 showing $0, added fallback to Airtable price data  
- ✅ **Outro Quality Enhancement** - Reordered operations to use high-resolution OpenAI images for outro
- ✅ **Custom Outro Text** - Implemented user-preferred outro: "Thanks for watching and the affiliate links are in the video descriptions"
- ✅ **Instagram Integration** - Fixed FinalVideo field compatibility for proper data structure
- ✅ **Success Rate Improvement** - Increased from 58% to 85% component success rate

---

## 🎯 **Overview**

This project implements a comprehensive automated content generation workflow that processes titles from Airtable, generates Amazon affiliate content, creates professional videos, and publishes to multiple platforms (YouTube, Instagram, WordPress) with complete automation and real-time monitoring.

### **Key System Features**
- **📊 Airtable Integration** - Processes 4,188 titles with sequential ID-based selection
- **🎥 Video Generation** - Creates professional Top 5 countdown videos under 60 seconds
- **🚀 Multi-Platform Publishing** - YouTube, Instagram (private), WordPress (main page)
- **💰 Amazon Monetization** - Automatic affiliate link integration with product validation
- **🎤 AI Voice Generation** - ElevenLabs voices for intro, outro, and product segments
- **🖼️ AI Image Creation** - OpenAI-generated intro/outro images plus Amazon product photos
- **📈 SEO Optimization** - Keywords-first approach for maximum search visibility
- **🔍 Real-Time Monitoring** - JSON2Video status tracking with error detection

---

## 🏗️ **Current Architecture**

### **Core Pipeline Structure**
```
[Airtable Title Selection] → [Amazon Product Validation] → [Content Generation] 
            ↓                            ↓                           ↓
[Keywords → Titles → Descriptions] → [Voice Generation] → [Image Creation]
            ↓                            ↓                           ↓
[JSON2Video Creation] → [Status Monitoring] → [Multi-Platform Publishing]
```

### **Production Workflow Components**

#### **Entry Point**
- **`src/workflow_runner.py`** - Main production orchestrator (ContentPipelineOrchestrator)

#### **Core MCP Servers** (`mcp_servers/`)
- **`airtable_server.py`** - Database operations with 107-field schema
- **`amazon_product_validator.py`** - Ensures minimum 5 products per title
- **`content_generation_server.py`** - AI content creation (Anthropic Claude)
- **`voice_generation_server.py`** - Voice synthesis (ElevenLabs)
- **`google_drive_server.py`** - File storage and organization
- **`instagram_server.py`** - Instagram private video publishing
- **`amazon_category_scraper.py`** - Product data extraction
- **`product_category_extractor_server.py`** - Category classification
- **`text_generation_control_server.py`** - Content quality control
- **`amazon_affiliate_server.py`** - Affiliate link generation

#### **Core MCP Agents** (`src/mcp/`)
- **`json2video_agent_mcp.py`** - Video creation coordination
- **`platform_content_generator.py`** - Multi-platform content optimization
- **`amazon_drive_integration.py`** - Google Drive file management
- **`intro_image_generator.py`** - OpenAI intro image creation
- **`outro_image_generator.py`** - OpenAI outro image creation
- **`voice_timing_optimizer.py`** - Audio timing validation
- **`wordpress_mcp.py`** - WordPress blog publishing
- **`youtube_mcp.py`** - YouTube video publishing
- **`text_length_validation_with_regeneration_agent_mcp.py`** - Content validation with regeneration

#### **Monitoring System** (`src/expert_agents/`)
- **`json2video_status_monitor.py`** - Real-time video generation monitoring with 5-minute delay + 1-minute intervals

---

## 📊 **Airtable Database Integration**

### **Critical Database Information**
- **Table Name:** "Video Titles" (not "Content")
- **Total Fields:** 107 columns with complete schema documentation
- **Processing Method:** Sequential by lowest ID (1→4,188)
- **Product Structure:** ProductNo1-5 fields (Title, Description, Photo, Price, Rating, Reviews, AffiliateLink)
- **Status Tracking:** All fields use "Pending"/"Ready" status system

### **Workflow Field Dependencies**
Based on `documentation/airtable_schema/Airtable_Workflow_Mapping.md`:

```
1. ID Selection → Status='Pending', lowest ID
2. Amazon Validation → Minimum 5 products required
3. Keywords Generation → UniversalKeywords + Platform-specific keywords
4. Content Creation → SEO-optimized titles/descriptions FROM keywords
5. Voice Generation → IntroHook (5s) + Product segments (9s each) + OutroCallToAction (5s)
6. Image Creation → Intro (all 5 products) + Outro (#1 winner) + Product photos
7. Video Creation → JSON2Video with countdown structure
8. Status Monitoring → Real-time error detection and reporting
9. Publishing → YouTube + Instagram (private) + WordPress (main page)
```

### **Critical Timing Requirements**
- **Total Video Duration:** ≤60 seconds
- **IntroHook:** Maximum 5 seconds of speech
- **Product Descriptions:** Maximum 9 seconds each (5 products = 45s max)
- **OutroCallToAction:** Maximum 5 seconds of speech
- **Countdown Structure:** ProductNo1=#5, ProductNo2=#4, ProductNo3=#3, ProductNo4=#2, ProductNo5=#1🏆

---

## 🚀 **Production Workflow Process**

### **Step-by-Step Execution (Real Implementation)**

1. **Title Selection & Validation**
   - Get ONE pending title with lowest ID from Airtable
   - Validate minimum 5 Amazon products available
   - Mark failed titles as completed to skip

2. **Content Generation (SEO-First Approach)**
   - Generate UniversalKeywords for base SEO
   - Create platform-specific keywords (YouTube, Instagram, WordPress)
   - Generate platform titles FROM keywords (not generic titles)
   - Generate platform descriptions FROM keywords with affiliate links

3. **Video Content Creation**
   - Transform VideoTitle → IntroHook (5-second limit)
   - Generate OutroCallToAction (5-second limit)
   - Create product countdown descriptions (9-second limits)
   - Validate all timing requirements

4. **Media Asset Generation**
   - **Voice Files:** ElevenLabs generation for intro/outro/products → Google Drive Audio folder
   - **Intro Image:** OpenAI generation showing all 5 products in dynamic arrangement
   - **Outro Image:** OpenAI generation featuring #1 winner + social media logos + ReviewCh3kr.com
   - **Product Photos:** Amazon product images saved to Google Drive

5. **Video Production**
   - JSON2Video API call with complete schema
   - Countdown structure implementation (#5 to #1)
   - Real-time status monitoring with 5-minute delay
   - Error detection and Airtable status updates

6. **Multi-Platform Publishing** (3/4 platforms ready)
   - **YouTube:** Video upload with SEO-optimized metadata
   - **Instagram:** Private video upload with hashtags
   - **WordPress:** Blog post on main page with photos/video/affiliate links
   - **TikTok:** Code ready but commented out (pending API approval)

7. **Completion & Tracking**
   - Update all status fields to "Ready"
   - Mark record Status as "Completed" 
   - Generate success/failure reports

---

## 📁 **File Organization**

The project follows a clean organized structure documented in `ORGANIZED_FILES_SUMMARY.md`:

```
/home/claude-workflow/
├── documentation/                       # All documentation organized
│   ├── README.md                       # Documentation index
│   ├── airtable_schema/                # Database documentation
│   │   ├── Airtable_Column_Schema.md   # Complete 107-field schema
│   │   ├── Airtable_Workflow_Mapping.md # Field usage guide
│   │   ├── airtable_schema_inspector.py # Schema analysis tool
│   │   ├── column_population_audit.py   # Coverage audit
│   │   └── column_classification_analysis.py # Importance analysis
│   ├── go_live/                        # Production readiness
│   │   └── GO_LIVE_CHECKLIST.md        # Launch checklist
│   └── project_overview/               # Project documentation
│       ├── CLAUDE.md                   # This file
│       └── TODO.md                     # Project roadmap
├── src/                                # Source code
│   ├── workflow_runner.py              # Main production entry point
│   ├── expert_agents/                  # Monitoring systems
│   │   └── json2video_status_monitor.py # Video status tracking
│   └── mcp/                           # MCP agents (workflow coordination)
├── mcp_servers/                        # MCP servers (core functions)
├── config/                            # Configuration files
│   ├── api_keys.json                  # API credentials
│   └── google_drive_audio_config.py   # Drive file mapping
└── ORGANIZED_FILES_SUMMARY.md          # File organization guide
```

---

## ⚙️ **Configuration Requirements**

### **Required API Keys** (`config/api_keys.json`)
```json
{
    "airtable_api_key": "pat_xxx",
    "airtable_base_id": "appXXX", 
    "airtable_table_name": "Video Titles",
    "anthropic_api_key": "sk-ant-xxx",
    "elevenlabs_api_key": "xxx",
    "openai_api_key": "sk-xxx",
    "scrapingdog_api_key": "xxx",
    "json2video_api_key": "xxx",
    "google_drive_service_account": "credentials.json",
    "youtube_api_credentials": "youtube_credentials.json",
    "instagram_api_credentials": "instagram_credentials.json",
    "wordpress_api_credentials": "wordpress_credentials.json"
}
```

### **Platform Configuration Status**
- ✅ **YouTube:** Fully configured and tested
- ✅ **Instagram:** Private upload mode configured  
- ✅ **WordPress:** Main page publishing configured
- ⏳ **TikTok:** Code ready, awaiting API approval (commented out)

---

## 🔧 **Development & Testing**

### **Running the Production Workflow**
```bash
cd /home/claude-workflow
python3 src/workflow_runner.py
```

### **Analysis Tools**
```bash
# Check Airtable schema
cd documentation/airtable_schema
python3 airtable_schema_inspector.py

# Audit field coverage
python3 column_population_audit.py

# Analyze field importance
python3 column_classification_analysis.py
```

### **Code Quality Verification**
```bash
# Verify production files compile
for file in mcp_servers/*.py src/mcp/*.py; do
  [[ "$file" != *"Test_"* ]] && python3 -m py_compile "$file" && echo "✅ $file"
done

# Test workflow import
python3 -c "import src.workflow_runner; print('✅ Production workflow OK')"
```

---

## 📈 **Current Production Status**

### **✅ Fully Operational Systems**
- **Content Generation Pipeline:** 100% functional with real APIs
- **Airtable Integration:** Complete 107-field schema management
- **Amazon Product Validation:** Minimum 5 products per title
- **Voice Generation:** ElevenLabs integration with Google Drive storage
- **Image Generation:** OpenAI intro/outro + Amazon product photos
- **Video Creation:** JSON2Video with real-time monitoring
- **Multi-Platform Publishing:** 3/4 platforms ready (75% complete)

### **⏳ Pending Items**
- **TikTok Integration:** Awaiting API approval (code implemented but commented out)
- **Advanced Analytics:** Enhanced performance tracking (future enhancement)

### **🎯 Performance Metrics (v5.2)**
- **Processing Speed:** ~45 seconds per title (excluding video rendering)
- **Success Rate:** 85%+ for component execution (improved from 58%)
- **Flow Continuation:** 100% - Publishing steps always execute after video generation
- **Video Quality:** Enhanced with high-resolution OpenAI images and accurate pricing
- **Field Coverage:** 90%+ for essential workflow fields
- **Platform Reach:** 3 major platforms (YouTube, Instagram, WordPress)

---

## 🛡️ **VideoProductionRDY Prerequisite Security System**

### **Security Gate Overview**
The VideoProductionRDY system implements a comprehensive prerequisite validation security gate that prevents incomplete video generation:

- **🔒 Single Select Control:** VideoProductionRDY column with options "Pending" and "Ready"
- **🚦 Initial State:** Set to "Pending" when title is first selected
- **✅ Approval Gate:** Only set to "Ready" when ALL 31 prerequisites are validated
- **🚫 Video Blocking:** Video generation blocked until VideoProductionRDY = "Ready"

### **Prerequisite Requirements (31 Total)**

#### **Status Columns (17 Required) - Must be "Ready":**
```
VideoTitleStatus, VideoDescriptionStatus
ProductNo1TitleStatus, ProductNo1DescriptionStatus, ProductNo1PhotoStatus
ProductNo2TitleStatus, ProductNo2DescriptionStatus, ProductNo2PhotoStatus  
ProductNo3TitleStatus, ProductNo3DescriptionStatus, ProductNo3PhotoStatus
ProductNo4TitleStatus, ProductNo4DescriptionStatus, ProductNo4PhotoStatus
ProductNo5TitleStatus, ProductNo5DescriptionStatus, ProductNo5PhotoStatus
```

#### **URL Fields (14 Required) - Must be populated:**
```
Audio Files: IntroMp3, OutroMp3, Product1Mp3, Product2Mp3, Product3Mp3, Product4Mp3, Product5Mp3
Photo Files: IntroPhoto, OutroPhoto
OpenAI Reference Links: ProductNo1Photo, ProductNo2Photo, ProductNo3Photo, ProductNo4Photo, ProductNo5Photo
```

### **Implementation Files**

#### **Production System:**
- **`mcp_servers/video_prerequisite_control_server.py`** - Core production server
- **`src/mcp/video_prerequisite_control_agent_mcp.py`** - Production MCP agent

#### **Test System:**  
- **`mcp_servers/Test_video_prerequisite_control_server.py`** - Test server with scenarios
- **`src/mcp/Test_video_prerequisite_control_agent_mcp.py`** - Test MCP agent

#### **Test Runner:**
- **`test_prerequisite_system.py`** - Complete system demonstration

### **Security Workflow**
```
[Title Selected] → VideoProductionRDY: "Pending"
       ↓
[Content Generation] → Status columns updated to "Ready"
       ↓
[Media Generation] → URL fields populated
       ↓
[Prerequisite Check] → Validate all 31 requirements
       ↓
[ALL Complete?] → VideoProductionRDY: "Ready" → Video Generation APPROVED
       ↓
[Missing Items?] → VideoProductionRDY: "Pending" → Video Generation BLOCKED
```

---

## 🔍 **JSON2Video Monitoring System**

### **Real-Time Status Tracking**
The `json2video_status_monitor.py` implements:
- **🚨 Real API Integration:** Calls actual JSON2Video status endpoint
- **⏰ Server-Friendly Timing:** 5-minute initial delay + 1-minute check intervals  
- **📊 Error Detection:** Identifies real errors like "Source URL required"
- **📝 Airtable Updates:** Updates record status with detailed error messages
- **🔄 Continuous Monitoring:** Tracks until completion or failure

### **API Endpoint**
```
GET https://api.json2video.com/v2/movies?project={projectId}
```

---

## 🚦 **Go-Live Configuration**

### **Production Ready Features**
- **✅ TikTok Code Commented Out:** Ready for 3-platform launch
- **✅ Instagram Private Mode:** Configured for private video uploads
- **✅ WordPress Main Page:** Blog posts published to main page
- **✅ JSON2Video Monitoring:** 5-minute + 1-minute server-friendly polling
- **✅ Error Handling:** Comprehensive failure detection and reporting
- **✅ Sequential Processing:** Ordered title processing by ID

### **Launch Checklist Reference**
Complete pre-launch verification available in:
**`documentation/go_live/GO_LIVE_CHECKLIST.md`**

---

## 🔄 **Maintenance & Updates**

### **Regular Maintenance Tasks**
- **Daily:** Monitor workflow execution and success rates via Airtable
- **Weekly:** Review field coverage and schema alignment
- **Monthly:** Update documentation and optimize performance  
- **Quarterly:** Assess new platform integrations

### **Documentation Updates**
When making changes:
1. Update relevant documentation in `documentation/` folder
2. Run analysis tools to verify field coverage
3. Update this CLAUDE.md if architectural changes occur
4. Maintain organized file structure per `ORGANIZED_FILES_SUMMARY.md`

---

## 🎯 **Key Implementation Notes**

### **Critical Success Factors**
1. **SEO-First Approach:** Keywords generated BEFORE titles and descriptions
2. **Timing Validation:** Strict 60-second video limit with component timing
3. **Status Field Management:** All status fields MUST be set to "Ready" when populated
4. **VideoProductionRDY Security:** Video generation blocked until ALL 31 prerequisites validated
5. **Sequential Processing:** Ordered by ID to ensure predictable execution
6. **Error Recovery:** Failed titles marked as completed to prevent infinite loops

### **Common Pitfalls Avoided**
- ❌ Generic title generation (now uses keywords-first SEO approach)
- ❌ Missing affiliate links (now integrated in all platform content)  
- ❌ Incorrect field names (ProductNoXTitle confirmed to exist in schema)
- ❌ API rate limiting issues (implemented server-friendly timing)
- ❌ File organization chaos (implemented organized documentation structure)

---

## 🚀 **Future Roadmap**

### **Immediate Priorities**
- TikTok API approval and integration activation
- Enhanced analytics dashboard
- Performance optimization for faster processing

### **Long-term Vision**
- Advanced AI content optimization
- Additional platform integrations (Pinterest, Facebook, Twitter)
- Automated A/B testing for content performance
- Advanced monetization strategies

---

*This documentation reflects the actual current state of the Claude Workflow project as of August 3, 2025. All references to outdated "16 expert agents" and other deprecated systems have been removed to ensure accuracy.*