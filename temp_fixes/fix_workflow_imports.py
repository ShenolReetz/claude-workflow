with open('src/workflow_runner.py', 'r') as f:
    content = f.read()

# Fix the import statements
replacements = [
    # Fix Google Drive import if needed
    ('from mcp.google_drive_agent_mcp import GoogleDriveAgentMCP', 
     'from mcp.google_drive_agent_mcp import GoogleDriveAgent'),
    ('GoogleDriveAgentMCP(', 'GoogleDriveAgent('),
    
    # Fix Amazon import if needed
    ('from mcp.amazon_affiliate_agent_mcp import AmazonAffiliateAgent',
     'from mcp.amazon_affiliate_agent_mcp import AmazonAffiliateAgentMCP'),
    ('AmazonAffiliateAgent(', 'AmazonAffiliateAgentMCP('),
]

for old, new in replacements:
    if old in content:
        content = content.replace(old, new)
        print(f"✅ Fixed: {old[:50]}...")

with open('src/workflow_runner.py', 'w') as f:
    f.write(content)

print("✅ Workflow runner imports fixed")
