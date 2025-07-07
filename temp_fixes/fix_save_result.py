with open('src/workflow_runner.py', 'r') as f:
    content = f.read()

# Fix the save_result check - it returns a boolean, not a dict
content = content.replace(
    "if save_result['success']:",
    "if save_result:"
)

# Also fix the Status field values to match what Airtable expects
# Let's use 'Processing' instead of 'Failed' for errors
content = content.replace("{'Status': 'Failed'}", "{'Status': 'Processing'}")

with open('src/workflow_runner.py', 'w') as f:
    f.write(content)

print("✅ Fixed save_result boolean check and Status field")
