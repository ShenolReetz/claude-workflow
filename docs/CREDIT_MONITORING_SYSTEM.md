# API Credit Monitoring System

## Overview 💰

This system monitors API credits/tokens for all paid services in your workflow and sends email alerts when credits drop below €10. It runs automatically at the end of each workflow to ensure you never run out of credits unexpectedly.

## Monitored Services 📊

### 1. **OpenAI** 🤖
- **Usage**: DALL-E image generation, GPT text generation
- **Monitoring**: Monthly usage tracking
- **Threshold**: €10 remaining estimated credits
- **Top-up**: https://platform.openai.com/account/billing

### 2. **ElevenLabs** 🎤
- **Usage**: Voice generation (when enabled)
- **Monitoring**: Character count remaining
- **Pricing**: ~€0.00018 per character
- **Top-up**: https://elevenlabs.io/subscription
- **Status**: ✅ Working (€32.32 remaining)

### 3. **JSON2Video** 🎬
- **Usage**: Video creation
- **Monitoring**: Credits remaining
- **Pricing**: ~€0.20 per credit/video
- **Top-up**: https://json2video.com/pricing
- **Status**: 🚨 Alert (€0.00 remaining - needs top-up)

### 4. **ScrapingDog** 🔍
- **Usage**: Amazon product scraping
- **Monitoring**: API requests remaining
- **Pricing**: ~€0.001 per request
- **Top-up**: https://scrapingdog.com/pricing
- **Status**: 🚨 Alert (€0.00 remaining - needs top-up)

### 5. **Anthropic** 🧠
- **Usage**: Claude content generation
- **Monitoring**: Not yet available (API limitation)
- **Top-up**: https://console.anthropic.com/settings/billing

### 6. **Airtable** 📊
- **Usage**: Database operations
- **Monitoring**: Free tier (generous limits)
- **Top-up**: https://airtable.com/pricing

## Configuration 🔧

### Email Settings
Add to `config/api_keys.json`:
```json
{
  "email_sender": "your-email@gmail.com",
  "email_password": "your-app-password",
  "email_recipient": "your-email@gmail.com",
  "email_smtp_server": "smtp.gmail.com",
  "email_smtp_port": 587,
  "credit_monitoring_enabled": true,
  "credit_threshold_eur": 10.0
}
```

### Gmail App Password Setup
1. Enable 2-factor authentication on Gmail
2. Go to Google Account settings
3. Generate App Password for "Mail"
4. Use this password (not your regular Gmail password)

## How It Works 🔄

### Workflow Integration
```python
# Runs automatically at end of workflow
credit_result = await monitor_api_credits(config)

if credit_result.get('alerts'):
    # Email sent automatically with:
    # - Service with low credits
    # - Remaining amount in EUR
    # - Direct top-up links
    # - Detailed HTML report
```

### Alert Triggers
- **Threshold**: €10 or less remaining
- **Check Frequency**: End of each workflow run
- **Email**: Sent immediately when threshold breached
- **Content**: HTML email with top-up links

### Email Alert Contains
1. **Summary**: Number of services with low credits
2. **Service Table**: Status, remaining value, details
3. **Direct Links**: One-click top-up URLs
4. **Recommendations**: Specific actions needed
5. **Report Details**: Timestamp and workflow info

## Current Status 📈

Based on latest test:
- **Total Services**: 6 monitored
- **Services Below Threshold**: 2 (JSON2Video, ScrapingDog)
- **Email Alerts**: 2 generated
- **Total Estimated Value**: €32.32 active credits

### Immediate Actions Needed 🚨
1. **JSON2Video**: Add credits (0 remaining)
2. **ScrapingDog**: Add credits (0 remaining)

## Testing Commands 🧪

```bash
# Test credit monitoring system
python3 src/test_credit_monitoring.py

# Check specific service
python3 -c "
from mcp_servers.credit_monitor_server import CreditMonitorMCPServer
import asyncio, json
async def test():
    with open('config/api_keys.json') as f:
        config = json.load(f)
    monitor = CreditMonitorMCPServer(config)
    result = await monitor._check_elevenlabs_credits()
    print(result)
    await monitor.close()
asyncio.run(test())
"

# Test workflow integration
python3 src/workflow_runner.py
```

## Error Handling 🛡️

### Workflow Continuity
- **Credit monitoring failure**: Workflow continues
- **Email failure**: Logged but doesn't stop workflow
- **API unavailable**: Marked as not available, no alert

### Common Issues
1. **Email authentication**: Use app password, not regular password
2. **API rate limits**: Monitoring respects API limits
3. **Network issues**: Timeout handled gracefully

## Pricing Estimates 💶

### Per Workflow Run Costs
- **ScrapingDog**: ~€0.005 (5 products × 1 request)
- **JSON2Video**: ~€0.20 (1 video)
- **ElevenLabs**: ~€0.50 (when enabled, ~2800 characters)
- **OpenAI DALL-E**: ~€0.35 (5 images)
- **Total per video**: ~€1.10

### Monthly Estimates (30 videos)
- **Total monthly cost**: ~€33
- **Recommended top-up**: €50-100 per service
- **Monitoring threshold**: €10 (gives ~9 video buffer)

## Manual Credit Checks 🔍

### Quick Status Check
```bash
# All services summary
python3 src/test_credit_monitoring.py

# Individual service check
curl -H "xi-api-key: YOUR_KEY" https://api.elevenlabs.io/v1/user/subscription
```

### Top-up Links
- **OpenAI**: https://platform.openai.com/account/billing
- **ElevenLabs**: https://elevenlabs.io/subscription
- **JSON2Video**: https://json2video.com/pricing
- **ScrapingDog**: https://scrapingdog.com/pricing
- **Anthropic**: https://console.anthropic.com/settings/billing

## Customization Options ⚙️

### Adjust Threshold
```json
{
  "credit_threshold_eur": 20.0  // Alert at €20 instead of €10
}
```

### Disable Monitoring
```json
{
  "credit_monitoring_enabled": false
}
```

### Add New Services
Extend `CreditMonitorMCPServer` with new `_check_*_credits()` methods.

## Future Enhancements 🚀

### Planned Features
1. **Weekly summary emails** (even if no alerts)
2. **Trend analysis** (usage patterns)
3. **Auto top-up integration** (when APIs support it)
4. **Slack/Discord notifications** (alternative to email)
5. **Cost prediction** (based on usage patterns)

### API Improvements Needed
1. **OpenAI**: Better usage API (current has auth issues)
2. **Anthropic**: Usage API when available
3. **Real-time pricing**: Dynamic pricing updates

## Support 🆘

### Troubleshooting
1. **No emails received**: Check spam folder, verify app password
2. **High false alerts**: Adjust threshold in config
3. **API errors**: Check API key validity and permissions

### Contact Points
- **Email issues**: Gmail app password documentation
- **API issues**: Respective service documentation
- **System issues**: Check logs in workflow output

---

**Status**: Active and monitoring
**Last Updated**: July 13, 2025
**Next Review**: Check monthly for API changes
**Priority**: Critical (prevents workflow interruption)