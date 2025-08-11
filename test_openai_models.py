#!/usr/bin/env python3
"""Test which OpenAI models are actually available"""

import os
from openai import OpenAI

# Initialize client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Test models that might exist
test_models = [
    # GPT-5 variants (checking if they exist)
    'gpt-5',
    'gpt-5-mini',
    'gpt-5-nano',
    
    # GPT-4 variants (known to exist)
    'gpt-4o',
    'gpt-4o-mini',
    'gpt-4-turbo',
    'gpt-4-turbo-preview',
    'gpt-4',
    
    # GPT-3.5 variants
    'gpt-3.5-turbo',
    'gpt-3.5-turbo-16k',
]

print("Testing OpenAI Models:")
print("=" * 50)

for model in test_models:
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{'role': 'user', 'content': 'Say "hi"'}],
            max_tokens=5
        )
        print(f"✅ {model:<25} - WORKS!")
    except Exception as e:
        error_msg = str(e)
        if 'does not exist' in error_msg or '404' in error_msg:
            print(f"❌ {model:<25} - DOES NOT EXIST")
        elif 'invalid' in error_msg:
            print(f"❌ {model:<25} - INVALID MODEL NAME")
        else:
            print(f"⚠️  {model:<25} - Error: {error_msg[:50]}")

print("\n" + "=" * 50)
print("Models marked with ✅ are available and working")
print("Models marked with ❌ do not exist or are invalid")