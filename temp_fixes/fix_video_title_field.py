with open('src/workflow_runner.py', 'r') as f:
    content = f.read()

# Fix the field name from 'video_title' to 'optimized_title'
content = content.replace(
    "'video_title': optimized_title",
    "'optimized_title': optimized_title"
)

with open('src/workflow_runner.py', 'w') as f:
    f.write(content)

print("✅ Fixed video title field name to match Airtable server expectations")
