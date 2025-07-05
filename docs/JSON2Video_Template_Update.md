# JSON2Video Template Update Documentation

## Overview

This document outlines the new JSON2Video template for creating professional countdown videos with Amazon review data, enhanced transitions, and interactive CTAs.

## Features

### 🎬 Video Structure
- **Duration**: 60 seconds total
- **Format**: 9:16 vertical (1080x1920) for social media
- **Scenes**: Intro (5s) + 5 Products (10s each) + Outro (5s)

### ✨ New Features Added
1. **Amazon Review Integration**
   - Review count counter component
   - 5-star rating display
   - Positioned above product descriptions

2. **Enhanced Transitions**
   - Wipe, slide, dissolve, and zoom effects
   - Smooth scene-to-scene flow
   - Special zoom effect for winner reveal

3. **Zoom Animations**
   - All titles use zoom-in animation
   - Dynamic entrance effects
   - Special scaling for #1 winner

4. **Interactive CTA Elements**
   - Animated follow button with cursor
   - Like and notification buttons
   - Pulsing and bounce animations

## Template Structure

```json
{
  "comment": "ReviewCh3kr Top 5 Countdown Video Template",
  "resolution": "vertical",
  "quality": "high",
  "fps": 30,
  "width": 1080,
  "height": 1920,
  "scenes": [
    // Intro, Product Scenes 1-5, Outro
  ]
}
```

## Variable Mapping

### Intro Variables
- `{{intro_background_image}}` - Brand/category image
- `{{intro_title}}` - From Airtable: VideoTitle
- `{{intro_description}}` - Static: "Let's count down the best products!"
- `{{intro_voice_text}}` - Same as intro_description

### Product Variables (Countdown Order)
Note: Products are shown in countdown order (5→1)

#### Product 1 (Shown as #5)
- `{{product1_image}}` - Product image URL
- `{{product1_title}}` - From Airtable: ProductNo5Title
- `{{product1_description}}` - From Airtable: ProductNo5Description (truncated)
- `{{product1_voice_text}}` - Full ProductNo5Description
- `{{product1_review_count}}` - From Airtable: ProductNo5ReviewCount
- `{{product1_rating}}` - From Airtable: ProductNo5Rating

#### Product 2-5 (Similar pattern)
- Follow same pattern with ProductNo4, ProductNo3, ProductNo2, ProductNo1

### Outro Variables
- `{{outro_background_image}}` - Brand logo/image
- `{{outro_title}}` - "Thanks for Watching!"
- `{{outro_description}}` - "Check the links below for the best deals!"
- `{{outro_voice_text}}` - Same as outro_description

### System Variables
- `{{voice_id}}` - ElevenLabs voice ID
- `{{background_music_url}}` - Background music file
- `{{google_drive_folder_id}}` - Storage folder
- `{{video_filename}}` - Output filename

## Implementation Steps

### 1. Update Airtable Schema
Add these fields to your Video Titles table:
```
- ProductNo1ReviewCount (Number)
- ProductNo1Rating (Number - decimal)
- ProductNo2ReviewCount (Number)
- ProductNo2Rating (Number - decimal)
- ProductNo3ReviewCount (Number)
- ProductNo3Rating (Number - decimal)
- ProductNo4ReviewCount (Number)
- ProductNo4Rating (Number - decimal)
- ProductNo5ReviewCount (Number)
- ProductNo5Rating (Number - decimal)
```

### 2. Update Amazon MCP
Enhance the Amazon scraping to capture review data:

```python
def extract_amazon_review_data(soup):
    """Extract review count and rating from Amazon product page"""
    
    # Review count
    review_element = soup.find('span', {'data-hook': 'total-review-count'})
    review_count = '0'
    if review_element:
        review_text = review_element.text.strip()
        review_count = re.findall(r'[\d,]+', review_text)[0].replace(',', '')
    
    # Rating
    rating_element = soup.find('span', {'class': 'a-icon-alt'})
    rating = '4.0'
    if rating_element:
        rating_match = re.search(r'(\d+\.?\d*)', rating_element.text)
        if rating_match:
            rating = rating_match.group(1)
    
    return {
        'review_count': review_count,
        'rating': float(rating)
    }
```

### 3. Update JSON2Video MCP

```python
# src/mcp/json2video_agent_mcp.py

def prepare_video_json(airtable_record):
    """Convert Airtable record to JSON2Video format with review data"""
    
    # Load template
    with open('templates/countdown_video_template.json', 'r') as f:
        template = json.load(f)
    
    # Prepare variables (countdown order: 5→1)
    variables = {
        # Intro
        "intro_background_image": get_category_image(airtable_record),
        "intro_title": airtable_record['VideoTitle'],
        "intro_description": "Let's count down the best products!",
        "intro_voice_text": "Let's count down the best products!",
        
        # Products (shown in countdown order)
        # Product 1 shown as #5
        "product1_image": airtable_record.get('ProductNo5ImageURL', DEFAULT_IMAGE),
        "product1_title": airtable_record['ProductNo5Title'],
        "product1_description": truncate_text(airtable_record['ProductNo5Description'], 15),
        "product1_voice_text": airtable_record['ProductNo5Description'],
        "product1_review_count": airtable_record.get('ProductNo5ReviewCount', '0'),
        "product1_rating": airtable_record.get('ProductNo5Rating', 4.0),
        
        # ... repeat for products 2-5 ...
        
        # Outro
        "outro_background_image": BRAND_LOGO_URL,
        "outro_title": "Thanks for Watching!",
        "outro_description": "Check the links below for the best deals!",
        "outro_voice_text": "Check the links below for the best deals!",
        
        # System
        "voice_id": ELEVENLABS_VOICE_ID,
        "background_music_url": COUNTDOWN_MUSIC_URL,
        "google_drive_folder_id": get_folder_id(airtable_record),
        "video_filename": generate_filename(airtable_record)
    }
    
    # Replace variables in template
    json_string = json.dumps(template)
    for key, value in variables.items():
        json_string = json_string.replace(f"{{{{{key}}}}}", str(value))
    
    return json.loads(json_string)
```

### 4. Integration with Workflow Runner

```python
# src/workflow_runner.py

async def generate_video_with_template(record_id):
    """Generate video using new template"""
    
    # Get record with review data
    record = await airtable_mcp.get_record(record_id)
    
    # Ensure review data exists
    if not record.get('ProductNo1ReviewCount'):
        logger.warning("No review data found, using defaults")
    
    # Prepare JSON with template
    video_json = prepare_video_json(record)
    
    # Send to JSON2Video
    result = await json2video_mcp.create_video(video_json)
    
    return result
```

## Transition Effects

### Scene Transitions Used
1. **Intro**: Fade from black (1.0s)
2. **Intro → Product #5**: Wipe-up (0.8s)
3. **Products #5-#3**: Slide-left (0.6s)
4. **Product #3 → #2**: Cross-dissolve (0.8s)
5. **Product #2 → #1**: Zoom-in (0.8s)
6. **Winner → Outro**: Cross-dissolve (1.0s)

## Component Details

### Review Counter (advanced/060)
```json
{
  "component": "advanced/060",
  "settings": {
    "counter": {
      "value": "{{product_review_count}}",
      "suffix": " Reviews",
      "animation_duration": 2,
      "format": "comma"
    }
  }
}
```

### Rating Stars (advanced/070)
```json
{
  "component": "advanced/070",
  "settings": {
    "rating": {
      "value": {{product_rating}},
      "max_value": 5,
      "star_size": 36,
      "star_color": "#FFD700"
    }
  }
}
```

### Interactive Button (advanced/051)
```json
{
  "component": "advanced/051",
  "settings": {
    "button": {
      "text": "FOLLOW FOR MORE!",
      "animation": {
        "type": "pulse",
        "repeat": "infinite"
      }
    },
    "cursor": {
      "animation": {
        "type": "move-and-click"
      }
    }
  }
}
```

## Testing

### Test Mode Variables
For testing with minimal API costs:
```python
TEST_VARIABLES = {
    "product1_review_count": "12,345",
    "product1_rating": 4.5,
    "product2_review_count": "8,921",
    "product2_rating": 4.3,
    # ... etc
}
```

### Validation Checklist
- [ ] All product images load correctly
- [ ] Review counts display with commas
- [ ] Ratings show correct star count
- [ ] Transitions flow smoothly
- [ ] Voice narration syncs with text
- [ ] Total duration = 60 seconds
- [ ] Outro buttons animate properly

## Template File Location

Save the complete JSON template to:
```
/home/claude-workflow/templates/countdown_video_template.json
```

## Next Steps

1. Implement review data scraping in Amazon MCP
2. Update Airtable schema with review fields
3. Test with single product video
4. Deploy to production workflow
5. Monitor video performance metrics

## Notes

- Button components are visual only (not clickable in video)
- Review data should be cached to avoid repeated scraping
- Consider platform-specific variations for optimal engagement
- Background music should be royalty-free for commercial use

---

*Last Updated: January 2025*
*Version: 1.0*
