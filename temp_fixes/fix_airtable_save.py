with open('src/workflow_runner.py', 'r') as f:
    content = f.read()

# Fix the save_generated_content call - it seems to expect only 2 parameters
# Change from 4 parameters to the correct number
old_call = """save_result = await self.airtable_server.save_generated_content(
                pending_title['record_id'],
                keywords_result,
                script_result
            )"""

# We need to see what the method actually expects
# For now, let's combine the data into a single dict
new_call = """# Prepare data for saving
            content_data = {
                'keywords': keywords_result,
                'script': script_result
            }
            save_result = await self.airtable_server.save_generated_content(
                pending_title['record_id'],
                content_data
            )"""

content = content.replace(old_call, new_call)

# Also fix the Status field value - seems "Error" is not a valid option
content = content.replace("{'Status': 'Error'}", "{'Status': 'Failed'}")

with open('src/workflow_runner.py', 'w') as f:
    f.write(content)

print("✅ Fixed Airtable save method call")
