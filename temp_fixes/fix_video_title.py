# Check what fields the save_generated_content is actually saving
with open('mcp_servers/airtable_server.py', 'r') as f:
    content = f.read()
    
# Look for VideoTitle field
if 'VideoTitle' in content:
    print("✅ VideoTitle field is being saved")
else:
    print("❌ VideoTitle field is NOT being saved - needs to be added")

# Check if we're passing the optimized title
with open('src/workflow_runner.py', 'r') as f:
    workflow_content = f.read()
    
if 'optimize_title' in workflow_content:
    print("✅ Title optimization is in workflow")
else:
    print("❌ Title optimization is missing")
