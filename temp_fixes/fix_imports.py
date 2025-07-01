import os

# Check Google Drive agent
gdrive_file = 'src/mcp/google_drive_agent_mcp.py'
if os.path.exists(gdrive_file):
    with open(gdrive_file, 'r') as f:
        content = f.read()
        if 'class GoogleDriveAgent' not in content:
            print("❌ GoogleDriveAgent class not found in google_drive_agent_mcp.py")
            # Check what class is actually there
            import re
            classes = re.findall(r'^class\s+(\w+)', content, re.MULTILINE)
            if classes:
                print(f"Found classes: {classes}")
        else:
            print("✅ GoogleDriveAgent class found")

# Check Amazon agent
amazon_file = 'src/mcp/amazon_affiliate_agent_mcp.py'
if os.path.exists(amazon_file):
    with open(amazon_file, 'r') as f:
        content = f.read()
        if 'class AmazonAffiliateAgent' not in content:
            print("❌ AmazonAffiliateAgent class not found")
            # Check what class is actually there
            import re
            classes = re.findall(r'^class\s+(\w+)', content, re.MULTILINE)
            if classes:
                print(f"Found classes: {classes}")
        else:
            print("✅ AmazonAffiliateAgent class found")
