#!/usr/bin/env python3
"""
Fix the AirtableMCPServer class structure
"""

# Read the original file
with open('/home/claude-workflow/mcp_servers/airtable_server.py', 'r') as f:
    content = f.read()

# Find where the class ends (the test code starts)
lines = content.split('\n')
class_lines = []
test_lines = []
in_class = True
class_methods = []

for i, line in enumerate(lines):
    if line.strip() == 'if __name__ == "__main__":':
        in_class = False
        test_lines.append(line)
    elif in_class:
        class_lines.append(line)
        # Track method definitions
        if line.strip().startswith('async def ') or line.strip().startswith('def '):
            class_methods.append(line.strip())
    else:
        test_lines.append(line)

print(f"Found {len(class_lines)} class lines")
print(f"Found {len(test_lines)} test lines")
print(f"Class methods: {len(class_methods)}")

# Find any methods that appear after the test code
post_test_methods = []
for i, line in enumerate(test_lines):
    if line.strip().startswith('async def ') and 'self' in line:
        post_test_methods.append((i + len(class_lines), line.strip()))

print(f"Methods found after test code: {len(post_test_methods)}")
for line_num, method in post_test_methods:
    print(f"  Line {line_num}: {method}")

# Check if update_multi_platform_keywords is in the post-test methods
has_multi_platform = any('update_multi_platform_keywords' in method for _, method in post_test_methods)
print(f"update_multi_platform_keywords in post-test methods: {has_multi_platform}")