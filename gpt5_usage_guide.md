# GPT-5 Model Usage Guide

## Available Models (August 2025)

### 🚀 gpt-5
- **Use for**: Complex reasoning, multi-step tasks, advanced content creation
- **Pricing**: $1.25/1M input tokens, $10/1M output tokens
- **Best for**: Script generation, complex analysis, creative writing

### ⚡ gpt-5-mini  
- **Use for**: General content generation, social media content, SEO optimization
- **Pricing**: $0.25/1M input tokens, $2/1M output tokens
- **Best for**: Platform content, product descriptions, keyword optimization

### 🏃 gpt-5-nano
- **Use for**: Simple tasks, validation, extraction, ultra-fast responses
- **Pricing**: $0.05/1M input tokens, $0.40/1M output tokens  
- **Best for**: Text validation, category extraction, quick classifications

### 💬 gpt-5-chat
- **Use for**: Advanced conversational applications, enterprise chat
- **Pricing**: Similar to gpt-5
- **Best for**: Customer service, advanced chat applications

## Current Workflow Configuration

| Component | Model Used | Reason |
|-----------|------------|---------|
| Content Generation | gpt-5-mini | Cost-effective for content |
| Text Validation | gpt-5-nano | Ultra-fast validation |
| Script Generation | gpt-5-nano | Quick script creation |
| Platform Content | gpt-5-mini | Balanced quality/cost |
| Category Extraction | gpt-5-nano | Simple extraction task |

## Cost Optimization

Using this configuration versus gpt-5 for everything:
- **Content Generation**: 80% cost reduction with gpt-5-mini
- **Validation Tasks**: 95% cost reduction with gpt-5-nano
- **Overall Savings**: ~70-80% reduction in AI costs

## Performance Benefits

- **Speed**: gpt-5-nano provides near-instant responses
- **Quality**: gpt-5-mini maintains high quality at lower cost
- **Reliability**: Proper fallback chain ensures workflow stability
