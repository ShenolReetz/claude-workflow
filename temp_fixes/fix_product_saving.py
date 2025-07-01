#!/usr/bin/env python3
"""
Fix product saving from countdown script
"""

# Read the workflow runner
with open('src/workflow_runner.py', 'r') as f:
    content = f.read()

# Let's find where the script result is processed
lines = content.split('\n')
for i, line in enumerate(lines):
    if 'script_result' in line and 'products' in line:
        print(f"Line {i+1}: {line}")
        # Show context
        for j in range(max(0, i-5), min(len(lines), i+10)):
            print(f"  {j+1}: {lines[j]}")
