# 📋 TODO - Production Workflow V2

## 🚨 IMMEDIATE ACTION REQUIRED (August 12, 2025)

### 1. **TEST COMPLETE WORKFLOW WITH LIVE TERMINAL OUTPUT**
- [ ] Run full Production workflow end-to-end
- [ ] Monitor live terminal output for all 14 steps
- [ ] Verify async voice generation performance (should be 5-7x faster)
- [ ] Confirm video rendering polling works (5 min timeout, 30 sec intervals)
- [ ] Check if YouTube upload succeeds with fixed FinalVideo field
- [ ] Validate all URLs are saved to Airtable correctly

### 2. **PUSH CHANGES TO REPOSITORY**
Once testing confirms all fixes work:
- [ ] Commit all fixed files with clear message
- [ ] Push to main branch
- [ ] Document the fixes in commit message:
  - Fixed field mismatches (title vs name)
  - Fixed OpenAI API parameters
  - Added video rendering polling
  - Implemented async voice generation
  - Fixed YouTube 403 error

## 🔧 TESTING CHECKLIST

### Pre-Test Verification:
- [ ] Confirm all API keys are valid
- [ ] Check Airtable has pending titles
- [ ] Verify Google Drive token is refreshed
- [ ] Ensure YouTube auth is current

### During Test - Monitor These Steps:
1. [ ] **Step 1**: Credential validation passes
2. [ ] **Step 2**: Title fetched from Airtable
3. [ ] **Step 3**: Amazon products scraped successfully
4. [ ] **Step 4**: Category extraction works
5. [ ] **Step 5**: Product validation passes
6. [ ] **Step 6**: Products saved to Airtable
7. [ ] **Step 7**: Content generation completes
8. [ ] **Step 8**: Voice generation runs in PARALLEL (watch for timing)
9. [ ] **Step 9**: Images generated in parallel
10. [ ] **Step 10**: Content validation passes
11. [ ] **Step 11**: Video creation starts
12. [ ] **Step 11b**: Video polling waits for rendering (up to 5 min)
13. [ ] **Step 12**: Google Drive upload succeeds
14. [ ] **Step 13**: YouTube upload works (no 403 error)
15. [ ] **Step 14**: WordPress publishes successfully

### Post-Test Validation:
- [ ] Check Airtable record has all URLs:
  - [ ] FinalVideo URL exists
  - [ ] YouTubeURL saved
  - [ ] WordPressURL saved
  - [ ] All audio URLs (IntroMp3, OutroMp3, Product1-5Mp3)
  - [ ] All image URLs (IntroPhoto, OutroPhoto, ProductNo1-5Photo)
- [ ] Verify video plays correctly from CloudFront URL
- [ ] Confirm YouTube video is uploaded and public
- [ ] Check WordPress post is published with correct content

## 🐛 POTENTIAL ISSUES TO WATCH FOR

### If Video Polling Fails:
- Check JSON2Video API status
- Verify project ID is correct
- Ensure API key has proper permissions
- Check if 5-minute timeout is sufficient

### If YouTube Still Gets 403:
- Verify FinalVideo field has correct CloudFront URL
- Check if video is fully rendered before download attempt
- Ensure video URL is publicly accessible
- Test manual download of video URL

### If Airtable Updates Fail:
- Check field names match exactly
- Verify data types (strings vs numbers)
- Ensure field values are within limits
- Check for required field constraints

## 📊 EXPECTED PERFORMANCE IMPROVEMENTS

### After All Fixes:
- **Voice Generation**: ~35s → ~5-7s (5-7x faster)
- **Total Workflow**: Should complete in under 5 minutes
- **Success Rate**: Should be 100% for all steps
- **API Calls**: Reduced by 6x for video polling (10 calls vs 60)

## 🚀 DEPLOYMENT READINESS

### Before Production Deployment:
- [ ] All 14 steps complete successfully
- [ ] No errors in terminal output
- [ ] All URLs saved to Airtable
- [ ] Video quality verified
- [ ] Platform publishing confirmed
- [ ] Performance metrics meet expectations

### Ready for Automated Runs:
- [ ] Workflow can run unattended
- [ ] Error handling prevents crashes
- [ ] All async operations work correctly
- [ ] Rate limits are respected
- [ ] Tokens auto-refresh as needed

---
*Last Updated: August 12, 2025*  
*Priority: TEST FULL WORKFLOW WITH LIVE OUTPUT → PUSH TO REPO*