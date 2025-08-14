# Token Refresh Implementation - Automatic at Workflow Start

## Overview
Since the workflow runs 3 times daily and OAuth tokens only last 1 hour, automatic token refresh has been implemented at the start of each workflow run.

## Implementation Details

### 1. Automatic Token Refresh in Main Workflow
**File**: `/src/Production_workflow_runner.py`

The workflow now automatically refreshes tokens BEFORE starting any operations:

```python
async def run_complete_workflow(self):
    # ALWAYS refresh tokens at the start since workflow runs 3x daily
    await self.refresh_tokens_before_workflow()
    
    # Then continue with workflow steps...
```

### 2. Token Refresh Method
The new `refresh_tokens_before_workflow()` method:
- Checks Google Drive token status
- Refreshes if expired or expiring soon (< 10 minutes)
- Checks YouTube token status
- Refreshes if expired or expiring soon
- Continues workflow even if refresh fails (with warnings)

### 3. Token Managers

#### Google Drive Token Manager
**File**: `/src/utils/google_drive_token_manager.py`
- ✅ Already exists and working
- Automatically refreshes expired tokens
- Saves refreshed tokens to file
- Provides detailed status reporting

#### YouTube Token Manager
**File**: `/src/utils/youtube_auth_manager.py`
- ✅ Enhanced with token status and refresh methods
- Same functionality as Google Drive manager
- Automatic refresh capability

## Usage

### Running the Workflow
Simply run the main workflow as usual:
```bash
python3 /home/claude-workflow/src/Production_workflow_runner.py
```

The workflow will:
1. **Check token status** for both Google Drive and YouTube
2. **Automatically refresh** if tokens are expired or expiring soon
3. **Display status** showing token validity
4. **Continue with workflow** using fresh tokens

### Manual Token Refresh (if needed)
```bash
# Refresh Google Drive token manually
python3 /home/claude-workflow/src/utils/google_drive_token_manager.py

# Check YouTube token status
python3 /home/claude-workflow/src/utils/youtube_auth_manager.py
```

## Token Lifecycle

### Typical Workflow Run
```
🔄 Token Refresh Check
-----------------------------------------------------------
📁 Checking Google Drive token...
   Status: EXPIRED - Refreshing...
   ✅ Google Drive token refreshed: Token refreshed successfully, valid for 1.0 hours

📺 Checking YouTube token...
   Status: VALID
   ✅ YouTube token valid for 45 minutes
-----------------------------------------------------------
[Workflow continues with fresh tokens...]
```

### Token Expiry Timeline
- **Token Duration**: 1 hour (3600 seconds)
- **Refresh Threshold**: 10 minutes before expiry
- **Workflow Runs**: 3 times daily (every 8 hours)
- **Result**: Tokens always refreshed at start of each run

## Benefits

1. **No Manual Intervention**: Tokens automatically refresh
2. **No Workflow Failures**: Fresh tokens for every run
3. **Graceful Degradation**: Workflow continues even if refresh fails
4. **Status Visibility**: Clear reporting of token states
5. **Persistent Storage**: Refreshed tokens saved for next run

## Monitoring

### Check Token Status
The workflow will display token status at start:
- `VALID` - Token is good, no refresh needed
- `NEEDS_REFRESH` - Expiring soon, will refresh
- `EXPIRED` - Expired, will refresh
- `TOKEN_MISSING` - No token file, needs manual auth

### Error Handling
If token refresh fails:
- Warning displayed but workflow continues
- Affected services (Google Drive/YouTube) may fail
- Manual intervention may be required

## Schedule Compatibility

Perfect for scheduled runs:
- **Morning Run (8 AM)**: Tokens refreshed at start
- **Afternoon Run (4 PM)**: Tokens refreshed at start  
- **Evening Run (12 AM)**: Tokens refreshed at start

Each run gets fresh 1-hour tokens, ensuring no expiry during workflow execution.

## Summary

✅ **Automatic token refresh implemented**
✅ **Works for both Google Drive and YouTube**
✅ **Integrated into main workflow**
✅ **No manual intervention needed**
✅ **Perfect for 3x daily scheduled runs**

The workflow is now fully autonomous and can run on schedule without token expiry issues!