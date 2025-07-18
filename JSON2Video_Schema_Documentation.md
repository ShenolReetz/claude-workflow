# JSON2Video API v2 - Complete Schema Documentation

## Overview

This document provides comprehensive documentation for the JSON2Video API v2 schema based on official documentation research and successful testing.

## Working Schema Structure

### Basic Movie Structure
```json
{
  "scenes": [
    {
      "duration": 5,
      "elements": [
        // Element objects go here
      ]
    }
  ],
  "elements": [
    // Movie-level elements (like subtitles)
  ]
}
```

**Important Notes:**
- ❌ NO `"movie"` wrapper (v2 removed this)
- ❌ NO `"version"` field at root level
- ❌ NO `"type": "Scene"` in scenes
- ✅ Only `scenes` array and optional movie-level `elements`

## Element Types

### 1. Text Element ✅ TESTED & WORKING

```json
{
  "type": "text",
  "text": "Your text content here",
  "settings": {
    "font-family": "Roboto",
    "font-size": "48px",
    "font-color": "#FFFFFF",
    "text-align": "center",
    "vertical-position": "center",
    "horizontal-position": "center"
  }
}
```

**Key Requirements:**
- All styling must be in `settings` object
- Font size requires units (`"48px"` not `48`)
- Use `vertical-position`/`horizontal-position` instead of `x`/`y`
- Available positions: `top`, `center`, `bottom` / `left`, `center`, `right`

### 2. Image Element ✅ TESTED & WORKING

```json
{
  "type": "image",
  "src": "https://example.com/image.jpg",
  "resize": "cover",
  "position": "center-center"
}
```

**Properties:**
- `src`: Image URL (required)
- `resize`: `"cover"`, `"contain"`, `"fill"`, `"fit"`
- `position`: Controls image positioning
- `pan`: `"left"`, `"right"`, `"up"`, `"down"` for motion effects
- `zoom`: Number for zoom level (e.g., `1.5`)

### 3. Voice Element (TTS) ✅ DOCUMENTED

```json
{
  "type": "voice",
  "text": "Text to be spoken",
  "voice": "en-US-EmmaMultilingualNeural",
  "model": "azure"
}
```

**Models Available:**
- `"azure"` (default) - Free, wide language support
- `"elevenlabs"` - High quality (60 credits/minute)
- `"elevenlabs-flash"` - Fast synthesis (60 credits/minute)

**Popular Voices:**
- Azure: `"en-US-EmmaMultilingualNeural"`, `"en-US-BrianMultilingualNeural"`
- ElevenLabs: `"Daniel"`, `"Rachel"`, etc.

### 4. Audio Element ✅ DOCUMENTED

```json
{
  "type": "audio",
  "src": "https://example.com/audio.mp3",
  "volume": 1.0,
  "loop": 1
}
```

**Properties:**
- `src`: Audio file URL (MP3, WAV supported)
- `volume`: 0-10 (default 1)
- `loop`: Number of loops (-1 for infinite)
- `seek`: Start time in seconds
- `muted`: Boolean to mute audio

### 5. Subtitles Element ✅ DOCUMENTED

**Important:** Only works at movie level, not scene level!

```json
{
  "elements": [
    {
      "type": "subtitles",
      "language": "en",
      "model": "default",
      "settings": {
        "style": "classic-progressive",
        "font-family": "Roboto",
        "font-size": 100,
        "position": "bottom-center",
        "word-color": "#FFFF00",
        "line-color": "#FFFFFF"
      }
    }
  ]
}
```

**Subtitle Styles:**
- `"classic"` - Simple text overlay
- `"classic-progressive"` - Progressive text display
- `"boxed-line"` - Box behind entire line
- `"boxed-word"` - Box behind each word

### 6. Component Elements ✅ DOCUMENTED

```json
{
  "type": "component",
  "component": "basic/050",
  "settings": {
    "item-name": {
      "property": "value"
    }
  }
}
```

**Available Components:**
- `basic/000` - Simple card
- `basic/001` - Card with left bar
- `basic/050` - CNN-style lower-third
- `basic/051` - Avatar lower-third
- `basic/052` - One line lower-third
- `basic/100` - Elastic box
- `basic/120` - Profile image

## Working 7-Scene Schema Template

```json
{
  "scenes": [
    {
      "duration": 7,
      "elements": [
        {
          "type": "image",
          "src": "https://images.unsplash.com/photo-1604079628040-94301bb21b91?w=1920&h=1080",
          "resize": "cover",
          "position": "center-center"
        },
        {
          "type": "text",
          "text": "Scene Title",
          "settings": {
            "font-family": "Roboto",
            "font-size": "48px",
            "font-color": "#FFFFFF",
            "text-align": "center",
            "vertical-position": "center",
            "horizontal-position": "center"
          }
        },
        {
          "type": "voice",
          "text": "Narration for this scene",
          "voice": "en-US-EmmaMultilingualNeural",
          "model": "azure"
        }
      ]
    }
    // ... repeat for 7 scenes
  ],
  "elements": [
    {
      "type": "subtitles",
      "language": "en",
      "model": "default",
      "settings": {
        "style": "classic-progressive",
        "font-family": "Roboto",
        "font-size": 100,
        "position": "bottom-center"
      }
    }
  ]
}
```

## Review Stars & Ratings

❌ **No dedicated star rating component found in documentation**

**Workaround:** Use text elements with star unicode characters:
```json
{
  "type": "text",
  "text": "⭐⭐⭐⭐⭐ 4.8/5",
  "settings": {
    "font-family": "Roboto",
    "font-size": "36px",
    "font-color": "#FFD700"
  }
}
```

## Scene Transitions

❌ **No scene transition documentation found**

Current research suggests transitions may not be available in the public API v2, or may be handled automatically by the system.

## Common Issues & Solutions

### 1. Schema Validation Errors
- ❌ `"Property 'movie' is not allowed"` → Remove movie wrapper
- ❌ `"Property 'version' is not allowed"` → Remove version field
- ❌ `"Property 'type' is not allowed in scenes"` → Remove type from scenes

### 2. Text Element Errors
- ❌ `"Object does not match schema: Text"` → Use `settings` object
- ❌ Font size errors → Use string with units (`"48px"`)
- ❌ Position errors → Use `vertical-position`/`horizontal-position`

### 3. Image Errors
- ❌ `"Failed to download"` → Check image URL accessibility
- ❌ Use reliable image sources (avoid broken URLs)

### 4. Audio/Voice Errors
- ❌ Check voice name spelling and model compatibility
- ❌ Verify audio file URLs are accessible

## API Request Format

```python
import requests
import json

url = "https://api.json2video.com/v2/movies"
headers = {
    "Content-Type": "application/json",
    "x-api-key": "YOUR_API_KEY"  # lowercase x-api-key
}

response = requests.post(url, headers=headers, data=json.dumps(payload))

# Check for immediate errors
if response.status_code == 200:
    data = response.json()
    if data["success"] == True:
        project_id = data["project"]
        print(f"Success: {project_id}")
    else:
        print(f"Error: {data.get('message')}")
```

## Status Checking

```python
# Check project status
status_resp = requests.get(
    f"https://api.json2video.com/v2/movies?project={project_id}",
    headers={"x-api-key": API_KEY}
)

if status_resp.status_code == 200:
    movie_info = status_resp.json()["movie"]
    print(f"Status: {movie_info['status']}")
    print(f"Success: {movie_info['success']}")
    if movie_info['success']:
        print(f"Video URL: {movie_info['url']}")
```

## Testing Results

✅ **Successfully Tested:**
- Empty 5-second scene
- Text element with settings object
- Image backgrounds with resize and position properties
- Voice narration with Azure TTS
- Complete movie generation
- **Subtitle elements with progressive highlighting** ✨
- **Real Google Drive photo integration** ✨
- **5-scene video with automatic subtitles** ✨

❌ **Issues Found:**
- Image URL 404 errors break rendering
- No built-in star rating components
- No transition documentation available
- ✅ **SOLVED: Google Drive permissions for external API access**

## Latest Breakthrough: Subtitle Integration ✅

**Successful Test Results (July 18, 2025):**
- **Video URL**: https://assets.json2video.com/clients/Apiha4SJJk/renders/2025-07-18-46883.mp4
- **Project ID**: Vc3OBByKDThC8PJ7
- **Duration**: 48 seconds across 5 scenes
- **Features**: Progressive subtitle highlighting, real Airtable photos, voice narration

**Proven Schema Formula:**
```json
{
  "scenes": [
    {
      "duration": 8,
      "elements": [
        {
          "type": "image",
          "src": "https://drive.google.com/uc?id=XXXXX&export=download",
          "resize": "cover",
          "position": "center-center"
        },
        {
          "type": "text",
          "text": "Scene Title",
          "settings": {
            "font-family": "Roboto",
            "font-size": "48px",
            "font-color": "#FFFFFF",
            "text-align": "center",
            "vertical-position": "top",
            "horizontal-position": "center"
          }
        },
        {
          "type": "voice",
          "text": "Narration text here",
          "voice": "en-US-EmmaMultilingualNeural",
          "model": "azure"
        }
      ]
    }
  ],
  "elements": [
    {
      "type": "subtitles",
      "model": "default",
      "language": "en",
      "settings": {
        "style": "classic-progressive",
        "font-family": "Roboto",
        "font-size": 32,
        "position": "bottom-center",
        "word-color": "#FFFF00",
        "line-color": "#FFFFFF",
        "outline-width": 2,
        "outline-color": "#000000",
        "max-words-per-line": 5
      }
    }
  ]
}
```

## Recommendations

1. **Always test image URLs** before using in production
2. **Use reliable image sources** (not random Unsplash URLs)
3. **Implement star ratings** using text elements with unicode stars
4. **Start simple** and add complexity gradually
5. **Monitor quota usage** when using voice synthesis

---

*Documentation based on JSON2Video API v2 official docs and extensive testing - Last updated: July 18, 2025*