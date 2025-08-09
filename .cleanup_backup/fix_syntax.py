#!/usr/bin/env python3
import re

# Read the file
with open('src/mcp/Production_platform_content_generator.py', 'r') as f:
    content = f.read()

# Pattern to find try blocks that need except blocks
# This finds: try: followed by response = client.chat.completions.create(model="gpt-5-mini-2025-08-07"
# and then adds the except block
pattern = r'(try:\s*\n\s*response = self\.client\.chat\.completions\.create\(\s*model="gpt-5-mini-2025-08-07",.*?\))\s*\n(\s*)(.*?)(?=\n\s*except|\n\s*finally|\n\s*def|\n\s*class|\n\s*return|\Z)'

def replace_match(match):
    try_block = match.group(1)
    indent = match.group(2)
    rest = match.group(3)
    
    # Add the except block with proper indentation
    replacement = f"""{try_block}
{indent}except Exception as e:
{indent}    print(f"Error with GPT-5, falling back to GPT-4: {{e}}")
{indent}    response = self.client.chat.completions.create(
{indent}        model="gpt-4-turbo",
{indent}        messages=[
{indent}            {{"role": "system", "content": "You are an expert content generator."}},
{indent}            {{"role": "user", "content": prompt if 'prompt' in locals() else caption_prompt if 'caption_prompt' in locals() else description_prompt if 'description_prompt' in locals() else intro_title_prompt if 'intro_title_prompt' in locals() else keyword_prompt}}
{indent}        ],
{indent}        temperature=0.7,
{indent}        max_tokens=300
{indent}    )
{indent}{rest}"""
    
    return replacement

# This is too complex - let me do it manually for each case
print("This script is too complex. Let me fix them one by one manually.")