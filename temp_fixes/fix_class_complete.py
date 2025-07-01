with open('src/workflow_runner.py', 'r') as f:
    content = f.read()

# Find the ContentPipelineOrchestrator class and rebuild it properly
import re

# Extract everything before the class
before_class = content.split('class ContentPipelineOrchestrator:')[0]

# Create a properly structured class
fixed_class = '''class ContentPipelineOrchestrator:
    def __init__(self):
        # Load configuration
        with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
            self.config = json.load(f)
        
        # Initialize MCP servers
        self.airtable_server = AirtableMCPServer(
            api_key=self.config['airtable_api_key'],
            base_id=self.config['airtable_base_id'],
            table_name=self.config['airtable_table_name']
        )
        
        self.content_server = ContentGenerationMCPServer(
            anthropic_api_key=self.config['anthropic_api_key']
        )
        
        # Initialize Google Drive agent
        self.google_drive_agent = GoogleDriveAgent()
    
    async def run_complete_workflow(self):
        """Run the complete content generation workflow"""
        print(f"🚀 Starting content workflow at {datetime.now()}")
        
        # Step 1: Get pending title from Airtable
        print("📋 Getting pending title from Airtable...")
        pending_title = await self.airtable_server.get_pending_titles()
'''

# Find the rest of the run_complete_workflow method
workflow_match = re.search(r'async def run_complete_workflow.*?(?=\n\s*(?:async )?def|if __name__|$)', content, re.DOTALL)
if workflow_match:
    # Extract the method content
    method_content = workflow_match.group()
    # Remove the method definition line since we already have it
    method_lines = method_content.split('\n')[1:]
    
    # Add the rest of the method with proper indentation
    for line in method_lines:
        if line.strip():
            # Ensure proper indentation (8 spaces for method content)
            stripped = line.lstrip()
            fixed_class += '\n        ' + stripped
        else:
            fixed_class += '\n'

# Add the main execution block
fixed_class += '''

# Main execution
if __name__ == "__main__":
    orchestrator = ContentPipelineOrchestrator()
    asyncio.run(orchestrator.run_complete_workflow())
'''

# Combine everything
new_content = before_class + fixed_class

# Write back
with open('src/workflow_runner.py', 'w') as f:
    f.write(new_content)

print("✅ Fixed class structure completely")
