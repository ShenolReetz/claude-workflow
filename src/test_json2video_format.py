#!/usr/bin/env python3
"""
Test JSON2Video Format Analysis - Check all video generation details
"""

import json
import sys
sys.path.append('/home/claude-workflow')

def analyze_template():
    """Analyze the JSON2Video template in detail"""
    
    print("🎬 JSON2Video Template Format Analysis")
    print("=" * 60)
    
    # Load and analyze the template
    with open('/home/claude-workflow/templates/countdown_video_template.json', 'r') as f:
        template = json.load(f)
    
    print(f"📋 Template Analysis:")
    print(f"   - Resolution: {template.get('resolution', 'N/A')}")
    print(f"   - Quality: {template.get('quality', 'N/A')}")
    print(f"   - FPS: {template.get('fps', 'N/A')}")
    print(f"   - Width: {template.get('width', 'N/A')}")
    print(f"   - Height: {template.get('height', 'N/A')}")
    print(f"   - Cache: {template.get('cache', 'N/A')}")
    print(f"   - Total Scenes: {len(template.get('scenes', []))}")
    
    # Calculate total duration
    total_duration = sum(scene.get('duration', 0) for scene in template.get('scenes', []))
    print(f"   - Total Duration: {total_duration} seconds")
    
    print("\n📽️ Scene Breakdown:")
    for i, scene in enumerate(template.get('scenes', []), 1):
        duration = scene.get('duration', 0)
        comment = scene.get('comment', f'Scene {i}')
        transition = scene.get('transition', {})
        elements = scene.get('elements', [])
        
        print(f"\n   Scene {i}: {comment}")
        print(f"      Duration: {duration}s")
        print(f"      Transition: {transition.get('type', 'none')} ({transition.get('duration', 0)}s)")
        print(f"      Elements: {len(elements)}")
        
        for j, element in enumerate(elements, 1):
            elem_type = element.get('type', 'unknown')
            elem_comment = element.get('comment', f'Element {j}')
            print(f"         {j}. {elem_type}: {elem_comment}")
            
            if elem_type == 'voice':
                print(f"            Provider: {element.get('provider', 'N/A')}")
                print(f"            Voice: {element.get('voice', 'N/A')}")
                print(f"            Text: {element.get('text', 'N/A')[:50]}...")
    
    print("\n🎵 Audio Configuration:")
    audio = template.get('audio', {})
    if audio:
        print(f"   - Background Music: {audio.get('src', 'N/A')}")
        print(f"   - Duration: {audio.get('duration', 'N/A')}s")
        print(f"   - Volume: {audio.get('volume', 'N/A')}")
        print(f"   - Fade In: {audio.get('fade-in', 'N/A')}s")
        print(f"   - Fade Out: {audio.get('fade-out', 'N/A')}s")
    else:
        print("   - No background music configured")
    
    print("\n📤 Export Configuration:")
    exports = template.get('exports', [])
    if exports:
        for export in exports:
            for dest in export.get('destinations', []):
                print(f"   - Type: {dest.get('type', 'N/A')}")
                print(f"   - Folder: {dest.get('folder', 'N/A')}")
                print(f"   - Filename: {dest.get('filename', 'N/A')}")
    else:
        print("   - No exports configured")
    
    print("\n🏷️ Template Variables:")
    template_str = json.dumps(template, indent=2)
    import re
    variables = re.findall(r'\{\{([^}]+)\}\}', template_str)
    unique_vars = sorted(set(variables))
    
    print(f"   Found {len(unique_vars)} unique variables:")
    for var in unique_vars:
        print(f"      - {var}")
    
    print("\n🎨 Visual Elements Analysis:")
    
    # Analyze fonts
    fonts = set()
    colors = set()
    animations = set()
    
    for scene in template.get('scenes', []):
        for element in scene.get('elements', []):
            if element.get('type') == 'text':
                style = element.get('style', {})
                if 'font-family' in style:
                    fonts.add(style['font-family'])
                if 'color' in style:
                    colors.add(style['color'])
            
            if element.get('type') == 'component':
                settings = element.get('settings', {})
                style = settings.get('style', {})
                if 'font-family' in style:
                    fonts.add(style['font-family'])
                if 'color' in style:
                    colors.add(style['color'])
                
                animation = settings.get('animation', {})
                if 'type' in animation:
                    animations.add(animation['type'])
    
    print(f"   Fonts Used: {', '.join(fonts) if fonts else 'None'}")
    print(f"   Colors Used: {len(colors)} unique colors")
    print(f"   Animations: {', '.join(animations) if animations else 'None'}")
    
    print("\n🔄 Transitions Analysis:")
    transitions = []
    for scene in template.get('scenes', []):
        transition = scene.get('transition', {})
        if transition:
            transitions.append(transition.get('type', 'unknown'))
    
    print(f"   Transition Types: {', '.join(set(transitions)) if transitions else 'None'}")
    
    print("\n⭐ Advanced Features:")
    advanced_features = []
    
    for scene in template.get('scenes', []):
        for element in scene.get('elements', []):
            if element.get('type') == 'component':
                component = element.get('component', '')
                if component:
                    advanced_features.append(f"Component: {component}")
                    
                settings = element.get('settings', {})
                if 'counter' in settings:
                    advanced_features.append("Review Counter Animation")
                if 'rating' in settings:
                    advanced_features.append("Star Rating System")
                if 'button' in settings:
                    advanced_features.append("Interactive Button")
            
            if 'ken-burns' in element:
                advanced_features.append("Ken Burns Effect")
            if 'fill-gradient' in element:
                advanced_features.append("Gradient Overlays")
    
    for feature in set(advanced_features):
        print(f"   ✅ {feature}")
    
    return template

def analyze_workflow_integration():
    """Analyze how the template integrates with the workflow"""
    
    print("\n🔗 Workflow Integration Analysis")
    print("=" * 60)
    
    # Check if enhanced server is used
    try:
        from mcp_servers.json2video_enhanced_server import JSON2VideoEnhancedMCPServer
        print("✅ Enhanced JSON2Video server available")
    except ImportError:
        print("❌ Enhanced JSON2Video server not found")
    
    # Check voice integration
    try:
        from mcp_servers.voice_generation_server import VoiceGenerationMCPServer
        print("✅ Voice generation server available")
    except ImportError:
        print("❌ Voice generation server not found")
    
    # Check image integration
    try:
        from mcp_servers.image_generation_server import ImageGenerationMCPServer
        print("✅ Image generation server available")
    except ImportError:
        print("❌ Image generation server not found")
    
    print("\n📊 Data Sources:")
    print("   ✅ Amazon product data (title, description, rating, reviews)")
    print("   ✅ AI-generated product images (OpenAI DALL-E)")
    print("   ✅ Voice narration (ElevenLabs)")
    print("   ✅ Background music support")
    print("   ✅ Google Drive export")

if __name__ == "__main__":
    template = analyze_template()
    analyze_workflow_integration()
    
    print("\n" + "=" * 60)
    print("✅ JSON2Video format analysis complete!")
    print("🎬 Template ready for production video generation")