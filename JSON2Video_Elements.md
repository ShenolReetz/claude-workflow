# JSON2Video Elements - Complete Documentation

## Overview

This document provides comprehensive documentation for all JSON2Video elements available in the API v2. Each element is documented with its properties, examples, and use cases based on the project's implementation and testing.

## Table of Contents

1. [Basic Elements](#basic-elements)
   - [Text Element](#text-element)
   - [Image Element](#image-element)
   - [Voice Element (TTS)](#voice-element-tts)
   - [Audio Element](#audio-element)
   - [Subtitles Element](#subtitles-element)
2. [Component Elements](#component-elements)
3. [Scene Structure](#scene-structure)
4. [Transitions](#transitions)
5. [Animations](#animations)
6. [Visual Effects](#visual-effects)
7. [Best Practices](#best-practices)

## Basic Elements

### Text Element

The text element displays text content on the screen with customizable styling and positioning.

#### Properties

| Property | Type | Required | Description | Example |
|----------|------|----------|-------------|---------|
| `type` | string | Yes | Must be `"text"` | `"text"` |
| `text` | string | Yes | The text content to display | `"Welcome to our review!"` |
| `settings` | object | Yes | Styling configuration object | See below |

#### Settings Object Properties

| Property | Type | Description | Values/Example |
|----------|------|-------------|----------------|
| `font-family` | string | Font family | `"Roboto"`, `"Montserrat"`, `"Open Sans"`, `"Bebas Neue"` |
| `font-size` | string | Font size with units | `"48px"`, `"64px"`, `"36px"` |
| `font-color` | string | Text color | `"#FFFFFF"`, `"#FFD700"`, `"#000000"` |
| `font-weight` | string | Font weight | `"normal"`, `"bold"`, `"light"` |
| `text-align` | string | Text alignment | `"left"`, `"center"`, `"right"` |
| `vertical-position` | string | Vertical position | `"top"`, `"center"`, `"bottom"` |
| `horizontal-position` | string | Horizontal position | `"left"`, `"center"`, `"right"` |
| `line-height` | number | Line height multiplier | `1.4`, `1.5` |

#### Legacy Properties (v1 compatibility)

| Property | Type | Description | Example |
|----------|------|-------------|---------|
| `x` | string/number | X position | `"center"`, `540`, `100` |
| `y` | number | Y position | `150`, `800`, `1200` |
| `width` | number | Text container width | `900`, `600`, `950` |
| `start` | number | Start time in scene | `0`, `0.5`, `1` |
| `duration` | number | Display duration | `5`, `8.5`, `9` |

#### Examples

**Modern Format (Recommended):**
```json
{
  "type": "text",
  "text": "Top 5 Kitchen Gadgets",
  "settings": {
    "font-family": "Montserrat",
    "font-size": "64px",
    "font-color": "#FFFFFF",
    "font-weight": "bold",
    "text-align": "center",
    "vertical-position": "center",
    "horizontal-position": "center"
  }
}
```

**Legacy Format (Still Supported):**
```json
{
  "type": "text",
  "text": "#1. Smart Coffee Maker - $129",
  "font-family": "Montserrat",
  "font-weight": "bold",
  "font-size": 44,
  "font-color": "#FFFFFF",
  "text-align": "center",
  "x": "center",
  "y": 150,
  "width": 950,
  "duration": 9
}
```

**Star Rating Display (Deprecated - Use Rating Component Instead):**
```json
// OLD METHOD - Using text with unicode stars
{
  "type": "text",
  "text": "⭐⭐⭐⭐☆ 4.5/5",
  "settings": {
    "font-family": "Open Sans",
    "font-size": "36px",
    "font-color": "#FFD700",
    "text-align": "center",
    "vertical-position": "center",
    "horizontal-position": "center"
  }
}

// RECOMMENDED - Use the rating component (advanced/070)
{
  "type": "component",
  "component": "advanced/070",
  "settings": {
    "rating": {
      "value": 4.5,
      "symbol": "star",
      "size": "8vw",
      "color": "#FFD700"
    }
  }
}
```

### Image Element

The image element displays images with various positioning and effect options.

#### Properties

| Property | Type | Required | Description | Values/Example |
|----------|------|----------|-------------|----------------|
| `type` | string | Yes | Must be `"image"` | `"image"` |
| `src` | string | Yes | Image URL | `"https://example.com/image.jpg"` |
| `resize` | string | No | Resize mode | `"cover"`, `"contain"`, `"fill"`, `"fit"` |
| `position` | string | No | Image position | `"center-center"`, `"top-left"`, etc. |
| `pan` | string | No | Pan direction | `"left"`, `"right"`, `"up"`, `"down"` |
| `zoom` | number | No | Zoom level | `1.5`, `2.0` |

#### Legacy Properties

| Property | Type | Description | Example |
|----------|------|-------------|---------|
| `x` | number | X position | `0`, `540` |
| `y` | number | Y position | `0`, `400` |
| `width` | number | Image width | `1080`, `500` |
| `height` | number | Image height | `1920`, `500` |
| `object-fit` | string | Object fit mode | `"cover"`, `"contain"` |
| `opacity` | number | Opacity level | `0.7`, `1.0` |

#### Examples

**Modern Format:**
```json
{
  "type": "image",
  "src": "https://drive.google.com/uc?id=XXXXX&export=download",
  "resize": "cover",
  "position": "center-center",
  "pan": "left",
  "zoom": 1.2
}
```

**Legacy Format:**
```json
{
  "type": "image",
  "src": "https://images.unsplash.com/photo-XXXXX",
  "x": 0,
  "y": 0,
  "width": 1080,
  "height": 1920,
  "object-fit": "cover",
  "opacity": 0.7
}
```

### Voice Element (TTS)

The voice element generates text-to-speech narration using various voice models.

#### Properties

| Property | Type | Required | Description | Values/Example |
|----------|------|----------|-------------|----------------|
| `type` | string | Yes | Must be `"voice"` | `"voice"` |
| `text` | string | Yes | Text to be spoken | `"Welcome to our review"` |
| `voice` | string | Yes | Voice identifier | See voice list below |
| `model` | string | No | TTS model | `"azure"`, `"elevenlabs"`, `"elevenlabs-flash"` |

#### Available Voices

**Azure Voices (Free):**
- `"en-US-EmmaMultilingualNeural"` - Female, natural
- `"en-US-BrianMultilingualNeural"` - Male, natural
- `"en-US-JennyNeural"` - Female, standard
- `"en-US-GuyNeural"` - Male, standard

**ElevenLabs Voices (60 credits/minute):**
- `"Daniel"` - Male, British
- `"Rachel"` - Female, American
- `"Drew"` - Male, American
- `"Emily"` - Female, American

#### Example

```json
{
  "type": "voice",
  "text": "Number 5 on our list is the Smart Kitchen Scale, perfect for precise measurements.",
  "voice": "en-US-EmmaMultilingualNeural",
  "model": "azure"
}
```

### Audio Element

The audio element plays background music or sound effects.

#### Properties

| Property | Type | Required | Description | Values/Example |
|----------|------|----------|-------------|----------------|
| `type` | string | Yes | Must be `"audio"` | `"audio"` |
| `src` | string | Yes | Audio file URL | `"https://example.com/music.mp3"` |
| `volume` | number | No | Volume level | `0.2` (20%), `1.0` (100%) |
| `loop` | number | No | Number of loops | `1`, `-1` (infinite) |
| `seek` | number | No | Start time in seconds | `0`, `5` |
| `muted` | boolean | No | Mute audio | `true`, `false` |
| `fade-in` | number | No | Fade in duration | `2` |
| `fade-out` | number | No | Fade out duration | `2` |

#### Example

```json
{
  "type": "audio",
  "src": "https://example.com/background-music.mp3",
  "volume": 0.2,
  "loop": 1,
  "fade-in": 2,
  "fade-out": 2
}
```

### Subtitles Element

The subtitles element provides automatic subtitle generation with various styling options.

**⚠️ Important:** Subtitles must be placed at the movie level, not within scenes!

#### Properties

| Property | Type | Required | Description | Values/Example |
|----------|------|----------|-------------|----------------|
| `type` | string | Yes | Must be `"subtitles"` | `"subtitles"` |
| `language` | string | Yes | Language code | `"en"`, `"es"`, `"fr"` |
| `model` | string | No | Subtitle model | `"default"` |
| `settings` | object | Yes | Styling configuration | See below |

#### Settings Properties

| Property | Type | Description | Values/Example |
|----------|------|-------------|----------------|
| `style` | string | Subtitle style | `"classic"`, `"classic-progressive"`, `"boxed-line"`, `"boxed-word"` |
| `font-family` | string | Font family | `"Roboto"`, `"Arial"` |
| `font-size` | number | Font size | `32`, `100` |
| `position` | string | Position | `"bottom-center"`, `"top-center"` |
| `word-color` | string | Word highlight color | `"#FFFF00"` |
| `line-color` | string | Line text color | `"#FFFFFF"` |
| `outline-width` | number | Outline width | `2` |
| `outline-color` | string | Outline color | `"#000000"` |
| `max-words-per-line` | number | Words per line | `5` |

#### Example

```json
{
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

## Component Elements

Pre-built components for common video elements.

### Properties

| Property | Type | Required | Description | Example |
|----------|------|----------|-------------|---------|
| `type` | string | Yes | Must be `"component"` | `"component"` |
| `component` | string | Yes | Component identifier | `"basic/050"` |
| `settings` | object | No | Component-specific settings | Varies by component |

### Available Components

| Component | Description | Use Case |
|-----------|-------------|----------|
| `basic/000` | Simple card | Basic text container |
| `basic/001` | Card with left bar | Highlighted card |
| `basic/050` | CNN-style lower-third | News-style text overlay |
| `basic/051` | Avatar lower-third | Profile with text |
| `basic/052` | One line lower-third | Simple subtitle bar |
| `basic/100` | Elastic box | Animated container |
| `basic/120` | Profile image | Circular profile image |
| **`advanced/070`** | **Rating Component** | **Star/Heart ratings** |

### Example - Basic Component

```json
{
  "type": "component",
  "component": "basic/050",
  "settings": {
    "text": {
      "content": "Breaking News",
      "color": "#FFFFFF"
    },
    "background": {
      "color": "#FF0000"
    }
  }
}
```

### Rating Component (advanced/070)

The rating component displays visual star or heart ratings, perfect for product reviews.

#### Properties

| Property | Type | Required | Description | Values/Default |
|----------|------|----------|-------------|---------------|
| `value` | integer | No | Rating value | `0-5` (default: `5`) |
| `symbol` | string | No | Rating symbol | `"star"`, `"heart"` (default: `"star"`) |
| `size` | string | No | Symbol size | `"3vw"`, `"12vw"`, etc. (default: `"3vw"`) |
| `color` | string | No | Color of filled symbols | `"gold"`, `"#FFD700"`, etc. (default: `"gold"`) |
| `off-color` | string | No | Color of empty symbols | `"transparent"`, `"rgba(255,255,255,0.1)"` (default: `"transparent"`) |
| `vertical-align` | string | No | Vertical alignment | `"top"`, `"center"`, `"bottom"` (default: `"center"`) |
| `horizontal-align` | string | No | Horizontal alignment | `"left"`, `"center"`, `"right"` (default: `"center"`) |

#### Examples

**Basic Star Rating (4.5 stars):**
```json
{
  "type": "component",
  "component": "advanced/070",
  "settings": {
    "rating": {
      "value": 4.5,
      "symbol": "star",
      "size": "8vw",
      "color": "#FFD700",
      "off-color": "rgba(255,255,255,0.2)"
    }
  }
}
```

**Large Product Rating:**
```json
{
  "type": "component",
  "component": "advanced/070",
  "x": "center",
  "y": 950,
  "start": 0.5,
  "duration": 8.5,
  "settings": {
    "rating": {
      "value": 4.2,
      "symbol": "star",
      "size": "12vw",
      "color": "gold",
      "off-color": "rgba(255,255,255,0.1)"
    }
  }
}
```

**Heart Rating for Favorites:**
```json
{
  "type": "component",
  "component": "advanced/070",
  "settings": {
    "rating": {
      "value": 5,
      "symbol": "heart",
      "size": "6vw",
      "color": "#FF1493",
      "off-color": "rgba(255,255,255,0.3)"
    }
  }
}
```

#### Integration with Product Scenes

Replace the text-based star rating with the proper component:

```json
// Instead of this (text with unicode stars):
{
  "type": "text",
  "text": "⭐⭐⭐⭐☆ 4.2/5",
  "font-family": "Open Sans",
  "font-size": 36,
  "font-color": "#FFD700"
}

// Use this (proper rating component):
{
  "type": "component",
  "component": "advanced/070",
  "x": "center",
  "y": 950,
  "start": 0.5,
  "duration": 8.5,
  "settings": {
    "rating": {
      "value": 4.2,
      "symbol": "star",
      "size": "8vw",
      "color": "#FFD700",
      "off-color": "rgba(255,255,255,0.2)"
    }
  }
}
```

## Video Configuration

### Resolution Options

JSON2Video supports various resolution formats optimized for different platforms:

| Resolution | Dimensions | Aspect Ratio | Use Case |
|------------|------------|--------------|----------|
| `"instagram-story"` | 1080x1920 | 9:16 (Vertical) | **YouTube Shorts**, TikTok, Instagram Stories/Reels |
| `"full-hd"` | 1920x1080 | 16:9 (Landscape) | YouTube videos, Facebook, LinkedIn |
| `"square"` | 1080x1080 | 1:1 (Square) | Instagram feed posts |
| `"4k"` | 3840x2160 | 16:9 (4K) | High-quality content (4x quota cost) |

### Quality Settings

| Setting | Description | File Size | Use Case |
|---------|-------------|-----------|----------|
| `"high"` | High quality output | Larger | Production content |
| `"medium"` | Balanced quality/size | Medium | Standard content |
| `"low"` | Lower quality | Smaller | Draft/testing |

### Movie Configuration Example

```json
{
  "resolution": "instagram-story",  // 9:16 for YouTube Shorts
  "quality": "high",
  "scenes": [
    // Scene objects
  ],
  "elements": [
    // Movie-level elements (subtitles, etc.)
  ]
}
```

## Scene Structure

Each scene is a container for elements with a specific duration.

### Properties

| Property | Type | Required | Description | Example |
|----------|------|----------|-------------|---------|
| `duration` | number | Yes | Scene duration in seconds | `5`, `7`, `9` |
| `elements` | array | Yes | Array of elements | `[]` |
| `transition` | object | No | Scene transition | See transitions section |
| `comment` | string | No | Scene description | `"INTRO - 5 seconds"` |
| `background-color` | string | No | Background color | `"rgba(22, 33, 62, 0.9)"` |

### Example

```json
{
  "comment": "Product #5 Scene",
  "duration": 9,
  "background-color": "rgba(22, 33, 62, 0.9)",
  "transition": {
    "type": "slide",
    "direction": "left",
    "duration": 0.6
  },
  "elements": [
    // Elements go here
  ]
}
```

## Transitions

Scene transitions control how one scene changes to the next.

### Available Transition Types

| Type | Description | Properties |
|------|-------------|------------|
| `fade` | Fade in/out | `duration` |
| `slide` | Slide transition | `direction`, `duration` |
| `slide_left` | Slide left | `duration` |
| `wipe` | Wipe effect | `direction`, `duration` |
| `cross-dissolve` | Cross fade | `duration` |
| `zoom` | Zoom transition | `duration` |

### Properties

| Property | Type | Description | Values |
|----------|------|-------------|--------|
| `type` | string | Transition type | See types above |
| `direction` | string | Direction (for slide/wipe) | `"left"`, `"right"`, `"up"`, `"down"` |
| `duration` | number | Transition duration | `0.5`, `0.8`, `1.0` |

### Examples

```json
// Fade transition
{
  "type": "fade",
  "duration": 0.5
}

// Slide transition
{
  "type": "slide",
  "direction": "left",
  "duration": 0.6
}

// Wipe transition
{
  "type": "wipe",
  "direction": "up",
  "duration": 0.8
}
```

## Animations

Element animations control how elements appear and move.

### Animation Types

| Type | Description | Properties |
|------|-------------|------------|
| `scale` | Scale animation | `from`, `to`, `start`, `duration`, `easing` |
| `slide` | Slide animation | `from`, `to`, `start`, `duration`, `easing` |
| `pulse` | Pulse effect | `scale`, `duration`, `loop` |
| `bounce` | Bounce effect | `duration` |
| `fade` | Fade effect | `from`, `to`, `start`, `duration` |

### Properties

| Property | Type | Description | Example |
|----------|------|-------------|---------|
| `type` | string | Animation type | `"scale"` |
| `from` | number/object | Starting value | `0`, `{x: -1080, y: 150}` |
| `to` | number/object | Ending value | `1`, `{x: "center", y: 150}` |
| `start` | number | Start time | `0`, `0.5` |
| `duration` | number | Animation duration | `0.8`, `1.0` |
| `easing` | string | Easing function | `"easeOutBack"`, `"easeOutCubic"` |
| `loop` | boolean | Loop animation | `true`, `false` |
| `scale` | number | Scale factor (pulse) | `1.2` |

### Examples

```json
// Scale animation
{
  "animations": [
    {
      "type": "scale",
      "from": 0,
      "to": 1,
      "start": 0,
      "duration": 0.8,
      "easing": "easeOutBack"
    }
  ]
}

// Slide animation
{
  "animations": [
    {
      "type": "slide",
      "from": {"x": -1080, "y": 150},
      "to": {"x": "center", "y": 150},
      "start": 0,
      "duration": 0.6,
      "easing": "easeOutCubic"
    }
  ]
}

// Pulse animation
{
  "animations": [
    {
      "type": "pulse",
      "scale": 1.2,
      "duration": 1,
      "loop": true
    }
  ]
}
```

## Visual Effects

### Ken Burns Effect

Subtle zoom and pan effect on images.

```json
{
  "type": "image",
  "src": "image_url",
  "pan": "left",
  "zoom": 1.2
}
```

### Gradient Overlays

Using background colors with transparency.

```json
{
  "background-color": "rgba(22, 33, 62, 0.9)"  // Dark blue with 90% opacity
}
```

### Image Filters

Control image appearance.

```json
{
  "type": "image",
  "src": "image_url",
  "opacity": 0.7  // 70% opacity
}
```

## Best Practices

### 1. Schema Version

Always use v2 schema format:
- ❌ NO `"movie"` wrapper
- ❌ NO `"version"` field
- ❌ NO `"type": "Scene"` in scenes
- ✅ Only `scenes` array and optional movie-level `elements`

### 2. Image URLs

- Use reliable image sources
- Test URLs before production
- For Google Drive: `https://drive.google.com/uc?id=XXXXX&export=download`
- Avoid broken or temporary URLs

### 3. Text Styling

- Always use `settings` object for modern format
- Include units in font-size (`"48px"` not `48`)
- Use web-safe fonts
- Ensure good contrast for readability

### 4. Voice Generation

- Keep voice text concise for timing
- Use Azure voices for free generation
- Test timing with actual TTS output
- Match voice text to subtitle display

### 5. Product Ratings

- Use the proper rating component (`advanced/070`) instead of text with unicode stars
- The component provides better visual consistency
- Supports fractional ratings (e.g., 4.5 stars)
- Customizable colors and sizes
- Example:
  ```json
  {
    "type": "component",
    "component": "advanced/070",
    "settings": {
      "rating": {
        "value": 4.2,
        "symbol": "star",
        "size": "8vw",
        "color": "#FFD700"
      }
    }
  }
  ```

### 6. Scene Timing

- Intro/Outro: 5-7 seconds
- Product scenes: 9-10 seconds
- Total video: Under 60 seconds for social media
- Account for transition duration

### 7. Subtitles

- Place at movie level, not scene level
- Use `classic-progressive` for word highlighting
- Set appropriate `max-words-per-line`
- Test subtitle timing with voice

### 8. Video Resolution

- Use `"instagram-story"` for YouTube Shorts, TikTok, Instagram (9:16 vertical)
- Use `"full-hd"` for standard YouTube videos (16:9 landscape)
- Use `"square"` for Instagram feed posts (1:1 square)
- Always specify `"quality": "high"` for production content
- Test resolution on target platforms before publishing

### 9. Performance

- Optimize image sizes
- Use appropriate video resolution
- Limit animation complexity
- Test on target platforms

## Complete Working Example

```json
{
  "width": 1080,   // Explicit dimensions for 9:16 YouTube Shorts
  "height": 1920,  // Ensures correct aspect ratio
  "quality": "high",
  "scenes": [
    {
      "comment": "INTRO - 5 seconds",
      "duration": 5,
      "transition": {
        "type": "fade",
        "duration": 0.5
      },
      "elements": [
        {
          "type": "image",
          "src": "https://images.unsplash.com/photo-XXXXX",
          "resize": "cover",
          "position": "center-center"
        },
        {
          "type": "text",
          "text": "Top 5 Kitchen Gadgets",
          "settings": {
            "font-family": "Montserrat",
            "font-size": "64px",
            "font-color": "#FFFFFF",
            "font-weight": "bold",
            "text-align": "center",
            "vertical-position": "center",
            "horizontal-position": "center"
          }
        },
        {
          "type": "voice",
          "text": "Welcome to our top 5 kitchen gadgets review!",
          "voice": "en-US-EmmaMultilingualNeural",
          "model": "azure"
        }
      ]
    },
    {
      "comment": "PRODUCT #5 - 9 seconds",
      "duration": 9,
      "background-color": "rgba(22, 33, 62, 0.9)",
      "transition": {
        "type": "slide",
        "direction": "left",
        "duration": 0.6
      },
      "elements": [
        {
          "type": "text",
          "text": "#5. Smart Kitchen Scale - $45",
          "font-family": "Montserrat",
          "font-weight": "bold",
          "font-size": 44,
          "font-color": "#FFFFFF",
          "text-align": "center",
          "x": "center",
          "y": 150,
          "width": 950,
          "animations": [
            {
              "type": "slide",
              "from": {"x": -1080, "y": 150},
              "to": {"x": "center", "y": 150},
              "start": 0,
              "duration": 0.6,
              "easing": "easeOutCubic"
            }
          ]
        },
        {
          "type": "image",
          "src": "https://example.com/product5.jpg",
          "x": "center",
          "y": 400,
          "width": 500,
          "height": 500,
          "object-fit": "contain",
          "animations": [
            {
              "type": "scale",
              "from": 0.7,
              "to": 1,
              "start": 0.3,
              "duration": 0.8,
              "easing": "easeOutBack"
            }
          ]
        },
        {
          "type": "component",
          "component": "advanced/070",
          "x": "center",
          "y": 950,
          "start": 0.5,
          "duration": 8.5,
          "settings": {
            "rating": {
              "value": 4.2,
              "symbol": "star",
              "size": "8vw",
              "color": "#FFD700",
              "off-color": "rgba(255,255,255,0.2)"
            }
          }
        },
        {
          "type": "text",
          "text": "4.2/5 (1,234 reviews)",
          "font-family": "Open Sans",
          "font-size": 28,
          "font-color": "#FFFFFF",
          "text-align": "center",
          "x": "center",
          "y": 1020,
          "width": 400,
          "start": 0.7,
          "duration": 8.3
        },
        {
          "type": "voice",
          "text": "Number 5 is the Smart Kitchen Scale, perfect for precise measurements in your cooking.",
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

---

*This documentation is based on JSON2Video API v2 implementation in the Claude Workflow project. Last updated: July 19, 2025*