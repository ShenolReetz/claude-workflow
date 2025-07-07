#!/usr/bin/env python3
import json

# Read config
with open('config/api_keys.json', 'r') as f:
    config = json.load(f)

# Check if password exists
if not config.get('wordpress_password'):
    print("⚠️ WordPress password is missing!")
    print("Please add your WordPress application password to config/api_keys.json")
    print('Add this line: "wordpress_password": "YOUR_APPLICATION_PASSWORD",')
    print("\nTo create an application password:")
    print("1. Go to: https://reviewch3kr.com/wp-admin/profile.php")
    print("2. Scroll to 'Application Passwords'")
    print("3. Create a new password for 'Automation'")
else:
    print("✅ WordPress password is configured")
