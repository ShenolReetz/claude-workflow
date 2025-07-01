#!/usr/bin/env python3
"""
Fix method calls in workflow runner to match the content generation server
"""

# Read the workflow runner
with open('src/workflow_runner.py', 'r') as f:
    content = f.read()

# Fix 1: Remove extra parameter from generate_seo_keywords
content = content.replace(
    "self.content_server.generate_seo_keywords(pending_title['title'], 'Tech Accessories')",
    "self.content_server.generate_seo_keywords(pending_title['title'])"
)

# Fix 2: Change optimize_title to generate_social_media_title
content = content.replace(
    "self.content_server.optimize_title(",
    "self.content_server.generate_social_media_title("
)

# Fix 3: Remove keywords_result parameter from generate_social_media_title
content = content.replace(
    "self.content_server.generate_social_media_title(pending_title['title'], keywords_result)",
    "self.content_server.generate_social_media_title(pending_title['title'])"
)

# Fix 4: Remove keywords_result parameter from generate_countdown_script
import re
# This one is multi-line, so we need regex
pattern = r"self\.content_server\.generate_countdown_script\(\s*pending_title\['title'\],\s*keywords_result\s*\)"
replacement = "self.content_server.generate_countdown_script(pending_title['title'])"
content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)

# Write the fixed content
with open('src/workflow_runner.py', 'w') as f:
    f.write(content)

print("✅ Fixed generate_seo_keywords call - removed 'Tech Accessories' parameter")
print("✅ Changed optimize_title to generate_social_media_title")
print("✅ Fixed all method calls to match expected parameters")

# Verify the fixes
print("\nVerifying method calls:")
with open('src/workflow_runner.py', 'r') as f:
    content = f.read()
    
# Check each method
methods = [
    'generate_seo_keywords',
    'generate_social_media_title', 
    'generate_countdown_script'
]

for method in methods:
    if method in content:
        # Find the line with this method
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if f'self.content_server.{method}' in line:
                print(f"\n{method}: Line {i+1}")
                # Show a few lines of context
                for j in range(max(0, i-1), min(len(lines), i+3)):
                    print(f"  {lines[j].strip()}")
