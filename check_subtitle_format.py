#!/usr/bin/env python3
"""
Check JSON2Video subtitle format requirements
"""

subtitle_example = {
    "id": "product1_subtitles",
    "type": "subtitles", 
    "settings": {
        "font-size": 80,
        "style": "classic-progressive",
        "font-family": "Roboto",
        "all-caps": True,
        "outline-width": -1,
        "vertical-align": "bottom",
        "offset-y": 900
    },
    "language": "en-US",
    # Missing: subtitle text or reference to audio track
}

print("JSON2Video Subtitle Requirements:")
print("1. Subtitles need text source - either:")
print("   - Direct 'text' field with subtitle content")
print("   - Reference to audio element for auto-generation")
print("   - SRT file reference")
print("\n2. Current implementation is missing subtitle text")
print("\n3. Options to fix:")
print("   a) Add 'text' field with product description")
print("   b) Add 'source' field referencing audio element")
print("   c) Use JSON2Video's auto-transcription feature")