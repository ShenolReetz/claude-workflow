#!/usr/bin/env python3
"""
Fix the affiliate result handling
"""

# Read the file
with open('/home/claude-workflow/src/workflow_runner.py', 'r') as f:
    content = f.read()

# Fix the affiliate result handling
old_code = """if affiliate_result['success']:
            print(f"✅ Generated {affiliate_result['links_generated']} affiliate links")
        else:
            print(f"⚠️ Affiliate link generation had issues: {affiliate_result.get('error', 'Unknown error')}")"""

new_code = """if affiliate_result.get('success'):
            links_count = affiliate_result.get('links_generated', 0)
            print(f"✅ Generated {links_count} affiliate links")
        else:
            print(f"⚠️ Affiliate link generation had issues: {affiliate_result.get('error', 'Unknown error')}")"""

content = content.replace(old_code, new_code)

# Write back
with open('/home/claude-workflow/src/workflow_runner.py', 'w') as f:
    f.write(content)

print("✅ Fixed affiliate result handling")
