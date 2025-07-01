with open('src/workflow_runner.py', 'r') as f:
    content = f.read()

# Add optimize_title step after keywords
if 'optimize_title' not in content:
    # Find where to insert it (after keywords generation)
    insert_after = "print(f\"✅ Generated {len(keywords_result)} SEO keywords\")"
    
    new_code = '''
            
            # Step 2.5: Optimize title for social media
            print("🎯 Optimizing title for social media...")
            optimized_title = await self.content_server.optimize_title(pending_title['title'], keywords_result)
            print(f"✅ Optimized title: {optimized_title}")'''
    
    content = content.replace(insert_after, insert_after + new_code)
    
    # Update the content_data to include the optimized title
    content = content.replace(
        "content_data = {\n                'keywords': keywords_result,\n                'script': script_result\n            }",
        "content_data = {\n                'keywords': keywords_result,\n                'script': script_result,\n                'video_title': optimized_title\n            }"
    )

with open('src/workflow_runner.py', 'w') as f:
    f.write(content)

print("✅ Added title optimization to workflow")
