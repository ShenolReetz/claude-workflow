#!/usr/bin/env python3
"""
Check and fix method calls in workflow runner
"""

# Read the workflow runner
with open('src/workflow_runner.py', 'r') as f:
    content = f.read()

# Let's find all calls to content server methods
import re

# Find all content_server method calls
method_calls = re.findall(r'self\.content_server\.\w+\([^)]*\)', content, re.MULTILINE | re.DOTALL)

print("Found content_server method calls:")
for call in method_calls:
    print(f"  - {call}")

# Now let's check the actual workflow runner content around the error
lines = content.split('\n')
for i, line in enumerate(lines):
    if 'generate_seo_keywords' in line:
        print(f"\nLine {i+1}: {line}")
        # Show context
        for j in range(max(0, i-2), min(len(lines), i+3)):
            print(f"  {j+1}: {lines[j]}")
