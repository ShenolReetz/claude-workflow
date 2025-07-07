import json

# Complete template structure
template = {
    "comment": "ReviewCh3kr Top 5 Countdown Video Template",
    "resolution": "vertical",
    "quality": "high",
    "fps": 30,
    "width": 1080,
    "height": 1920,
    "cache": True,
    "scenes": [],
    "audio": {
        "comment": "Background music for entire video",
        "src": "{{background_music_url}}",
        "start": 0,
        "duration": 60,
        "volume": 0.2,
        "fade-in": 2,
        "fade-out": 2
    },
    "exports": [{
        "destinations": [{
            "type": "google-drive",
            "folder": "{{google_drive_folder_id}}",
            "filename": "{{video_filename}}"
        }]
    }]
}

# INTRO SCENE
intro_scene = {
    "comment": "INTRO SCENE",
    "duration": 5,
    "transition": {"type": "fade", "duration": 1.0, "from": "black"},
    "elements": [
        {
            "type": "image",
            "comment": "Intro Background Image",
            "src": "{{intro_background_image}}",
            "start": 0,
            "duration": 5,
            "width": 1080,
            "height": 1920,
            "x": 0,
            "y": 0,
            "object-fit": "cover"
        },
        {
            "type": "rectangle",
            "comment": "Dark overlay for better text visibility",
            "start": 0,
            "duration": 5,
            "width": 1080,
            "height": 1920,
            "x": 0,
            "y": 0,
            "fill-color": "#000000",
            "opacity": 0.4
        },
        {
            "type": "component",
            "comment": "Intro Title at Top with Zoom Animation",
            "component": "advanced/000",
            "settings": {
                "animation": {"type": "zoom-in", "duration": 0.5},
                "text": "{{intro_title}}",
                "start": 1,
                "duration": 3,
                "x": 540,
                "y": 200,
                "width": 900,
                "height": 200,
                "x-anchor": "center",
                "y-anchor": "center",
                "fade-out": 0.5,
                "style": {
                    "text-align": "center",
                    "font-family": "Montserrat",
                    "font-weight": "bold",
                    "font-size": "72px",
                    "color": "#FFFFFF",
                    "text-shadow": "2px 2px 4px rgba(0,0,0,0.8)"
                }
            }
        },
        {
            "type": "text",
            "comment": "Intro Description at Bottom",
            "text": "{{intro_description}}",
            "start": 1,
            "duration": 3,
            "x": 540,
            "y": 1600,
            "width": 900,
            "height": 200,
            "x-anchor": "center",
            "y-anchor": "center",
            "fade-in": 0.5,
            "fade-out": 0.5,
            "style": {
                "text-align": "center",
                "font-family": "Roboto",
                "font-weight": "normal",
                "font-size": "36px",
                "color": "#FFFFFF",
                "text-shadow": "1px 1px 3px rgba(0,0,0,0.8)",
                "padding": "20px"
            }
        },
        {
            "type": "voice",
            "comment": "Voice reading intro description",
            "text": "{{intro_description}}",
            "start": 1,
            "duration": 3,
            "provider": "elevenlabs",
            "voice": "{{voice_id}}"
        }
    ]
}
template["scenes"].append(intro_scene)

# Add 5 product scenes
transitions = [
    {"type": "wipe-up", "duration": 0.8, "ease": "ease-out", "softness": 0.1},
    {"type": "slide-left", "duration": 0.6, "ease": "ease-in-out", "overlap": 0.1},
    {"type": "cross-dissolve", "duration": 0.8, "overlap": 0.4},
    {"type": "slide-left", "duration": 0.6, "ease": "ease-in-out", "overlap": 0.1},
    {"type": "zoom-in", "duration": 0.8, "scale": 1.3, "ease": "ease-out"}
]

for i in range(1, 6):
    # Product numbers count down: Scene 1 shows #5, Scene 5 shows #1
    display_number = 6 - i
    is_winner = (i == 5)
    
    product_scene = {
        "comment": f"PRODUCT SCENE {i}" + (" - THE WINNER" if is_winner else ""),
        "duration": 10,
        "transition": transitions[i-1],
        "elements": [
            # Background image
            {
                "type": "image",
                "comment": f"Product {i} Background Image",
                "src": f"{{{{product{i}_image}}}}",
                "start": 0,
                "duration": 10,
                "width": 1080,
                "height": 1920,
                "x": 0,
                "y": 0,
                "object-fit": "cover",
                "ken-burns": {
                    "start": {"zoom": 1.0 if i % 2 else 1.1},
                    "end": {"zoom": 1.1 if i % 2 else 1.0}
                }
            },
            # Gradient overlay
            {
                "type": "rectangle",
                "comment": "Gradient overlay",
                "start": 0,
                "duration": 10,
                "width": 1080,
                "height": 1920,
                "x": 0,
                "y": 0,
                "fill-gradient": {
                    "type": "radial" if is_winner else "linear",
                    "angle": 180 if not is_winner else None,
                    "colors": [
                        {"color": "rgba(255,215,0,0.2)" if is_winner else "rgba(0,0,0,0)", "offset": 0},
                        {"color": "rgba(0,0,0,0.3)", "offset": 0.5},
                        {"color": "rgba(0,0,0,0.7)", "offset": 1}
                    ]
                }
            },
            # Number badge
            {
                "type": "text",
                "comment": "Number Badge" + (" - WINNER" if is_winner else ""),
                "text": f"#{display_number}",
                "start": 0.5,
                "duration": 9,
                "x": 100,
                "y": 100,
                "width": 150,
                "height": 150,
                "x-anchor": "center",
                "y-anchor": "center",
                "fade-in": 0.3,
                "style": {
                    "text-align": "center",
                    "font-family": "Bebas Neue",
                    "font-size": "140px" if is_winner else "120px",
                    "color": "#FFD700",
                    "text-shadow": "3px 3px 6px rgba(0,0,0,0.9)"
                }
            }
        ]
    }
    
    # Add crown for winner
    if is_winner:
        product_scene["elements"].append({
            "type": "image",
            "comment": "Winner crown icon",
            "src": "https://cdn-icons-png.flaticon.com/512/3141/3141811.png",
            "start": 0.5,
            "duration": 9,
            "x": 100,
            "y": 30,
            "width": 80,
            "height": 80,
            "x-anchor": "center",
            "y-anchor": "center",
            "fade-in": 0.5
        })
    
    # Add title, review counter, rating, description, and voice
    # Title
    product_scene["elements"].append({
        "type": "component",
        "comment": f"Product {i} Title at Top with Zoom Animation" + (" - WINNER" if is_winner else ""),
        "component": "advanced/000",
        "settings": {
            "animation": {
                "type": "zoom-in",
                "duration": 0.5,
                "delay": 0,
                "scale_from": 0.5 if is_winner else None,
                "scale_to": 1.1 if is_winner else None
            },
            "text": f"{{{{product{i}_title}}}}",
            "start": 1,
            "duration": 8,
            "x": 540,
            "y": 250,
            "width": 900,
            "height": 150,
            "x-anchor": "center",
            "y-anchor": "center",
            "fade-out": 0.5,
            "style": {
                "text-align": "center",
                "font-family": "Montserrat",
                "font-weight": "bold",
                "font-size": "64px" if is_winner else "56px",
                "color": "#FFD700" if is_winner else "#FFFFFF",
                "text-shadow": "3px 3px 6px rgba(0,0,0,0.9)" if is_winner else "2px 2px 4px rgba(0,0,0,0.8)"
            }
        }
    })
    
    # Review counter
    product_scene["elements"].append({
        "type": "component",
        "comment": f"Product {i} Review Counter" + (" - WINNER" if is_winner else ""),
        "component": "advanced/060",
        "settings": {
            "counter": {
                "value": f"{{{{product{i}_review_count}}}}",
                "suffix": " Reviews",
                "animation_duration": 2,
                "format": "comma",
                "highlight": is_winner
            },
            "start": 1,
            "duration": 8,
            "x": 540,
            "y": 1450,
            "x-anchor": "center",
            "y-anchor": "center",
            "style": {
                "font-family": "Roboto",
                "font-weight": "bold" if is_winner else "normal",
                "font-size": "32px" if is_winner else "28px",
                "color": "#FFD700" if is_winner else "#FFFFFF",
                "text-shadow": "2px 2px 4px rgba(0,0,0,0.9)" if is_winner else "1px 1px 3px rgba(0,0,0,0.8)"
            }
        }
    })
    
    # Rating stars
    product_scene["elements"].append({
        "type": "component",
        "comment": f"Product {i} Rating Stars" + (" - WINNER" if is_winner else ""),
        "component": "advanced/070",
        "settings": {
            "rating": {
                "value": f"{{{{product{i}_rating}}}}",
                "max_value": 5,
                "star_size": 42 if is_winner else 36,
                "star_color": "#FFD700",
                "empty_star_color": "#666666",
                "show_value": True,
                "animate": is_winner
            },
            "start": 1,
            "duration": 8,
            "x": 540,
            "y": 1520,
            "x-anchor": "center",
            "y-anchor": "center"
        }
    })
    
    # Description
    product_scene["elements"].append({
        "type": "text",
        "comment": f"Product {i} Description at Bottom",
        "text": f"{{{{product{i}_description}}}}",
        "start": 1,
        "duration": 8,
        "x": 540,
        "y": 1650,
        "width": 900,
        "height": 200,
        "x-anchor": "center",
        "y-anchor": "center",
        "fade-in": 0.5,
        "fade-out": 0.5,
        "style": {
            "text-align": "center",
            "font-family": "Roboto",
            "font-weight": "bold" if is_winner else "normal",
            "font-size": "34px" if is_winner else "32px",
            "color": "#FFFFFF",
            "text-shadow": "2px 2px 4px rgba(0,0,0,0.8)",
            "padding": "20px",
            "background-color": "rgba(255,215,0,0.2)" if is_winner else "rgba(0,0,0,0.5)",
            "border": "3px solid #FFD700" if is_winner else None,
            "border-radius": "15px" if is_winner else "10px"
        }
    })
    
    # Voice
    product_scene["elements"].append({
        "type": "voice",
        "comment": f"Voice reading product {i} description",
        "text": f"{{{{product{i}_voice_text}}}}",
        "start": 1,
        "duration": 8,
        "provider": "elevenlabs",
        "voice": "{{voice_id}}"
    })
    
    template["scenes"].append(product_scene)

# OUTRO SCENE
outro_scene = {
    "comment": "OUTRO SCENE",
    "duration": 5,
    "transition": {"type": "cross-dissolve", "duration": 1.0, "overlap": 0.5},
    "elements": [
        {
            "type": "image",
            "comment": "Outro Background Image",
            "src": "{{outro_background_image}}",
            "start": 0,
            "duration": 5,
            "width": 1080,
            "height": 1920,
            "x": 0,
            "y": 0,
            "object-fit": "cover"
        },
        {
            "type": "rectangle",
            "comment": "Dark overlay",
            "start": 0,
            "duration": 5,
            "width": 1080,
            "height": 1920,
            "x": 0,
            "y": 0,
            "fill-color": "#000000",
            "opacity": 0.6
        },
        {
            "type": "component",
            "comment": "Outro Title at Top with Zoom Animation",
            "component": "advanced/000",
            "settings": {
                "animation": {"type": "zoom-in", "duration": 0.5},
                "text": "{{outro_title}}",
                "start": 1,
                "duration": 3,
                "x": 540,
                "y": 400,
                "width": 900,
                "height": 200,
                "x-anchor": "center",
                "y-anchor": "center",
                "fade-out": 0.5,
                "style": {
                    "text-align": "center",
                    "font-family": "Montserrat",
                    "font-weight": "bold",
                    "font-size": "64px",
                    "color": "#FFFFFF",
                    "text-shadow": "2px 2px 4px rgba(0,0,0,0.8)"
                }
            }
        },
        {
            "type": "text",
            "comment": "Outro Description/CTA at Bottom",
            "text": "{{outro_description}}",
            "start": 1,
            "duration": 3,
            "x": 540,
            "y": 1400,
            "width": 900,
            "height": 300,
            "x-anchor": "center",
            "y-anchor": "center",
            "fade-in": 0.5,
            "fade-out": 0.5,
            "style": {
                "text-align": "center",
                "font-family": "Roboto",
                "font-weight": "normal",
                "font-size": "36px",
                "color": "#FFFFFF",
                "text-shadow": "1px 1px 3px rgba(0,0,0,0.8)",
                "padding": "30px"
            }
        },
        {
            "type": "component",
            "comment": "Interactive Subscribe/Follow Button with Cursor",
            "component": "advanced/051",
            "settings": {
                "button": {
                    "text": "FOLLOW FOR MORE!",
                    "style": {
                        "background-color": "#FF0000",
                        "color": "#FFFFFF",
                        "font-family": "Bebas Neue",
                        "font-size": "48px",
                        "padding": "20px 40px",
                        "border-radius": "50px",
                        "border": "3px solid #FFFFFF",
                        "box-shadow": "0 4px 15px rgba(0,0,0,0.5)"
                    },
                    "hover_style": {
                        "background-color": "#FFD700",
                        "transform": "scale(1.1)",
                        "box-shadow": "0 6px 20px rgba(255,215,0,0.6)"
                    },
                    "animation": {
                        "type": "pulse",
                        "duration": 1.5,
                        "repeat": "infinite"
                    }
                },
                "cursor": {
                    "show": True,
                    "animation": {
                        "type": "move-and-click",
                        "start_position": {"x": 400, "y": 1600},
                        "end_position": {"x": 540, "y": 1700},
                        "click_at": 3.5,
                        "duration": 2
                    },
                    "style": {
                        "size": 32,
                        "color": "#FFFFFF"
                    }
                },
                "start": 2,
                "duration": 3,
                "x": 540,
                "y": 1700,
                "x-anchor": "center",
                "y-anchor": "center"
            }
        },
        {
            "type": "component",
            "comment": "Interactive Like Button",
            "component": "advanced/051",
            "settings": {
                "button": {
                    "text": "👍 LIKE",
                    "style": {
                        "background-color": "#1877F2",
                        "color": "#FFFFFF",
                        "font-family": "Roboto",
                        "font-weight": "bold",
                        "font-size": "36px",
                        "padding": "15px 30px",
                        "border-radius": "30px",
                        "box-shadow": "0 3px 10px rgba(0,0,0,0.3)"
                    },
                    "hover_style": {
                        "background-color": "#FFD700",
                        "transform": "scale(1.05)"
                    },
                    "animation": {
                        "type": "bounce",
                        "delay": 0.5,
                        "duration": 0.8
                    }
                },
                "cursor": {
                    "show": False
                },
                "start": 2.5,
                "duration": 2.5,
                "x": 300,
                "y": 1550,
                "x-anchor": "center",
                "y-anchor": "center"
            }
        },
        {
            "type": "component",
            "comment": "Interactive Bell Notification",
            "component": "advanced/051",
            "settings": {
                "button": {
                    "text": "🔔 NOTIFY",
                    "style": {
                        "background-color": "#FF0000",
                        "color": "#FFFFFF",
                        "font-family": "Roboto",
                        "font-weight": "bold",
                        "font-size": "36px",
                        "padding": "15px 30px",
                        "border-radius": "30px",
                        "box-shadow": "0 3px 10px rgba(0,0,0,0.3)"
                    },
                    "hover_style": {
                        "background-color": "#FFD700",
                        "transform": "scale(1.05)"
                    },
                    "animation": {
                        "type": "shake",
                        "delay": 0.8,
                        "duration": 0.5,
                        "repeat": 2
                    }
                },
                "cursor": {
                    "show": False
                },
                "start": 2.5,
                "duration": 2.5,
                "x": 780,
                "y": 1550,
                "x-anchor": "center",
                "y-anchor": "center"
            }
        },
        {
            "type": "voice",
            "comment": "Voice reading outro description",
            "text": "{{outro_voice_text}}",
            "start": 1,
            "duration": 3,
            "provider": "elevenlabs",
            "voice": "{{voice_id}}"
        }
    ]
}
template["scenes"].append(outro_scene)

# Save the complete template
with open('templates/countdown_video_template.json', 'w', encoding='utf-8') as f:
    json.dump(template, f, indent=2)

print("✅ Complete template created successfully!")

# Validate
try:
    with open('templates/countdown_video_template.json', 'r') as f:
        data = json.load(f)
    print(f"✅ Valid JSON with {len(data['scenes'])} scenes")
    print("✅ Features included:")
    print("  - Intro scene with zoom animation")
    print("  - 5 product scenes with countdown (#5 to #1)")
    print("  - Review counters and rating stars")
    print("  - Enhanced transitions")
    print("  - Outro with interactive buttons")
    print("  - Voice narration support")
    print("  - Background music configuration")
except Exception as e:
    print(f"❌ Error: {e}")

# Check file size
import os
size = os.path.getsize('templates/countdown_video_template.json')
print(f"📏 File size: {size/1024:.1f} KB")
