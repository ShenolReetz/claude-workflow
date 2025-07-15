# Instagram Token Management Guide

## Overview
This guide explains how to manage Instagram access tokens for the automated video upload workflow. Instagram uses OAuth 2.0 for authentication and requires long-lived tokens for automated posting.

## Token Types

### 1. Short-Lived Token
- **Duration**: 1 hour
- **Usage**: Initial authentication only
- **Not suitable for**: Automated workflows

### 2. Long-Lived Token
- **Duration**: 60 days
- **Usage**: Automated posting workflows
- **Refresh**: Can be refreshed before expiry

## Setup Process

### Step 1: Initial Authentication

1. **Generate Authentication URL**:
   ```bash
   python3 src/instagram_token_manager.py auth-url
   ```

2. **Visit the URL** in your browser and authorize the app

3. **Copy the authorization code** from the redirect URL:
   - You'll be redirected to: `http://localhost:8080/callback?code=YOUR_CODE`
   - Copy the `YOUR_CODE` part

4. **Exchange code for token**:
   ```bash
   python3 src/instagram_token_manager.py authenticate --code YOUR_CODE
   ```

### Step 2: Check Token Status

```bash
python3 src/instagram_token_manager.py status
```

This shows:
- Whether you have a token
- When it expires
- If it needs refresh

### Step 3: Validate Token

```bash
python3 src/instagram_token_manager.py validate
```

This verifies the token works by making a test API call.

### Step 4: Refresh Token (When Needed)

```bash
python3 src/instagram_token_manager.py refresh
```

**Note**: Refresh when token has less than 30 days remaining.

## Integration Testing

Run the comprehensive test:
```bash
python3 src/test_instagram_token.py
```

This will:
1. Check current token status
2. Validate the token
3. Refresh if needed
4. Verify integration readiness

## Token Storage

Tokens are stored in two locations:

1. **Main Config** (`config/api_keys.json`):
   - `instagram_access_token`: Current active token

2. **Token Cache** (`config/instagram_token_cache.json`):
   - Token metadata
   - Expiration dates
   - Refresh history

## Automated Token Management

The workflow automatically:
- Uses the stored long-lived token
- Checks token validity before uploads
- Logs warnings when token is expiring

## Troubleshooting

### "No token found"
- Run the initial authentication process

### "Token expired"
- Re-authenticate using Step 1

### "Token invalid"
- Check if Instagram app is still approved
- Verify app hasn't been suspended
- Re-authenticate if needed

### "Upload failed: Not authenticated"
- Ensure `instagram_enabled: true` in config
- Verify token is valid
- Check Instagram Business Account is properly linked

## Best Practices

1. **Regular Checks**: Run token status check weekly
2. **Proactive Refresh**: Refresh tokens when < 30 days remain
3. **Monitor Logs**: Watch for token-related warnings in workflow logs
4. **Backup Tokens**: Keep a secure backup of working tokens

## Security Notes

- Never commit tokens to version control
- Keep `instagram_token_cache.json` secure
- Rotate tokens if compromised
- Use environment variables for production

## API Limits

Instagram API has these limits:
- **Rate Limit**: 200 calls/hour per user
- **Daily Upload**: ~25 media items/day
- **Content**: Must comply with Instagram policies

## Required Permissions

The app needs these Instagram permissions:
- `user_profile`: Read profile info
- `user_media`: Post media content

For business features:
- Link Instagram account to Facebook Page
- Convert to Instagram Business Account
- Connect in Facebook Business Manager