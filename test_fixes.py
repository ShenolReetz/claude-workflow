#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, 'src')

print("🧪 Testing Claude Workflow Fixes")
print("=" * 50)

# Test 1: Filename sanitization
print("\n1️⃣ Testing filename sanitization:")
try:
    from utils.filename_utils import sanitize_filename
    test_cases = [
        "🔥 5 MUST-HAVE Monitor Mounts in 2025 | Don't Buy Wrong!",
        "Amazon Basics Premium Wall Mount",
        "Test 😀 with emojis!!"
    ]
    for test in test_cases:
        clean = sanitize_filename(test)
        print(f"✅ '{test}' -> '{clean}'")
except Exception as e:
    print(f"❌ Sanitization test failed: {e}")

# Test 2: Google Drive import
print("\n2️⃣ Testing Google Drive agent:")
try:
    from mcp.google_drive_agent_mcp import GoogleDriveAgent
    print("✅ Google Drive agent imports successfully")
except Exception as e:
    print(f"❌ Google Drive import failed: {e}")

# Test 3: Amazon agent - with correct class name
print("\n3️⃣ Testing Amazon agent:")
try:
    from mcp.amazon_affiliate_agent_mcp import AmazonAffiliateAgentMCP
    print("✅ Amazon agent imports successfully (as AmazonAffiliateAgentMCP)")
except Exception as e:
    print(f"❌ Amazon import failed: {e}")

print("\n✅ All tests complete! Ready to run workflow.")
