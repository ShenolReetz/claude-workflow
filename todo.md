# 📋 TODO - Production Workflow V2

## 🚨 CRITICAL - GO LIVE TONIGHT (August 14, 2025)

### 🎯 PHASE 1: FIX REMAINING ERRORS
- [ ] **Fix Airtable Update Error (422)**
  - [ ] Debug why "Invalid request: parameter validation failed" occurs
  - [ ] Check field data types being sent to Airtable
  - [ ] Ensure all field values are properly formatted
  - [ ] Test with mcp__airtable__update_records tool directly

- [ ] **Fix WordPress Publishing Error (400)**
  - [ ] Check WordPress authentication is valid
  - [ ] Verify post data format matches API requirements
  - [ ] Ensure content length is within limits
  - [ ] Test tag IDs are being converted correctly

- [ ] **Verify YouTube Upload Completion**
  - [ ] Confirm video URL is saved to Airtable
  - [ ] Check if video is set to public/unlisted correctly
  - [ ] Ensure thumbnail is uploaded if available

### 🚀 PHASE 2: FULL WORKFLOW VALIDATION
- [ ] **Run Complete End-to-End Test**
  - [ ] Start fresh with new pending title
  - [ ] Monitor all 14 workflow steps
  - [ ] Verify Remotion renders without JSON2Video
  - [ ] Confirm all media assets upload to Google Drive
  - [ ] Check all platform publishing works

- [ ] **Performance Validation**
  - [ ] Total time under 5 minutes ✅ (Currently 4m 35s)
  - [ ] Remotion renders in ~2 minutes ✅
  - [ ] Voice generation under 50 seconds ✅
  - [ ] All parallel phases execute correctly ✅

### 📱 PHASE 3: SOCIAL MEDIA INTEGRATION

#### ✅ Currently Working:
- [x] **YouTube** - Videos uploading successfully
- [x] **Google Drive** - All assets uploading with folder structure
- [x] **Remotion** - Video generation working (primary renderer)

#### 🔧 Need to Enable:
- [ ] **WordPress**
  - [ ] Fix 400 error on post creation
  - [ ] Verify featured image attachment
  - [ ] Test affiliate links in content
  - [ ] Confirm SEO metadata is included

- [ ] **Instagram** 
  - [ ] Enable Instagram Reels upload via API
  - [ ] Set up proper video format (9:16 vertical)
  - [ ] Test caption and hashtag posting
  - [ ] Verify account connection is active

#### ⏸️ On Hold:
- [ ] **TikTok** (Waiting for app approval)
  - [ ] Document API integration requirements
  - [ ] Prepare test content for when approved
  - [ ] Set up webhook for approval notification

### 🌙 PHASE 4: GO LIVE TONIGHT

#### Pre-Launch Checklist:
- [ ] **System Health**
  - [ ] All API credentials valid and refreshed
  - [ ] Redis cache operational
  - [ ] Circuit breakers reset and monitoring
  - [ ] Disk space sufficient for video rendering

- [ ] **Content Pipeline**
  - [ ] At least 10 pending titles in Airtable
  - [ ] All product categories mapped correctly
  - [ ] Voice styles configured for variety
  - [ ] Brand colors and themes set

- [ ] **Publishing Accounts**
  - [ ] YouTube channel ready with playlists
  - [ ] WordPress site live with proper theme
  - [ ] Instagram account in creator/business mode
  - [ ] Google Drive folder structure organized

#### Launch Configuration:
- [ ] **Set up automated scheduling**
  ```bash
  # Add to crontab for 3x daily runs (6am, 2pm, 10pm)
  0 6,14,22 * * * cd /home/claude-workflow && python3 run_ultra_optimized.py >> workflow_cron.log 2>&1
  ```

- [ ] **Enable monitoring**
  - [ ] Set up log rotation for workflow_optimized.log
  - [ ] Configure alerts for workflow failures
  - [ ] Create daily summary report script
  - [ ] Set up backup of successful videos

- [ ] **Final Testing**
  - [ ] Run 3 consecutive videos without intervention
  - [ ] Verify all platforms receive content
  - [ ] Check Airtable status updates correctly
  - [ ] Confirm no memory leaks or resource issues

### 📊 SUCCESS METRICS FOR TONIGHT

#### Minimum Requirements:
- [ ] 3 videos successfully created and published
- [ ] YouTube uploads working (100% success)
- [ ] WordPress posts created (after fix)
- [ ] Instagram posts scheduled (if enabled)
- [ ] Zero workflow crashes

#### Target Goals:
- [ ] 5+ videos processed
- [ ] All platforms except TikTok active
- [ ] Average processing time < 5 minutes
- [ ] 95%+ success rate across all steps
- [ ] Full automation without manual intervention

### 🛠️ QUICK FIXES REFERENCE

```bash
# Test Airtable field update
python3 -c "from mcp_servers.Production_airtable_server import *; import asyncio; server = ProductionAirtableMCPServer('KEY', 'BASE', 'TABLE'); asyncio.run(server.update_record_field('RECORD_ID', 'FinalVideo', 'URL'))"

# Test WordPress connection
python3 -c "from src.mcp.Production_wordpress_mcp_v2 import *; wp = ProductionWordPressMCP(config); wp.test_connection()"

# Monitor workflow in real-time
tail -f /home/claude-workflow/workflow_optimized.log | grep -E "✅|❌|ERROR|WARNING"

# Check circuit breaker status
python3 -c "from src.utils.circuit_breaker import get_circuit_breaker_manager; m = get_circuit_breaker_manager(); print(m.get_all_status())"

# Clear Redis cache if needed
redis-cli FLUSHDB
```

### 🎯 TONIGHT'S LAUNCH SEQUENCE

1. **6:00 PM** - Fix Airtable and WordPress errors
2. **7:00 PM** - Run full test workflow
3. **8:00 PM** - Enable all working platforms
4. **9:00 PM** - Set up cron jobs
5. **10:00 PM** - GO LIVE with first automated run
6. **10:30 PM** - Monitor and verify success
7. **11:00 PM** - Confirm overnight schedule is active

---
*Last Updated: August 14, 2025 @ 12:15 PM*  
*Priority: FIX ERRORS → TEST → GO LIVE TONIGHT*  
*Status: Remotion integration complete, 2 platform errors to fix*