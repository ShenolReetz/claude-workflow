with open('src/workflow_runner.py', 'r') as f:
    lines = f.readlines()

# Find and fix the problematic section
fixed_lines = []
in_problem_area = False
skip_lines = False

for i, line in enumerate(lines):
    # Check if we're in the problematic area (around line 140-150)
    if i >= 139 and i <= 155:
        stripped = line.strip()
        
        # If this is the except block
        if 'except Exception as e:' in line:
            fixed_lines.append(line)
            in_problem_area = True
            continue
        
        # If we're in the problem area after except
        if in_problem_area:
            # Keep the error logging and comment
            if 'logger.error' in line or '# Continue workflow' in line:
                fixed_lines.append(line)
                continue
            
            # If we hit an empty line after the except block content
            if not stripped and i > 142:
                fixed_lines.append(line)
                in_problem_area = False
                skip_lines = True
                continue
            
            # Skip the incorrectly indented lines
            if skip_lines and stripped:
                # Check if this line should be kept but at correct indentation
                if 'DEBUG: video_url' in line:
                    # This should be removed or moved elsewhere
                    continue
                elif 'if video_url and video_url.strip():' in line:
                    # This block seems to be duplicated, skip it
                    continue
                elif 'Uploading video to Google Drive' in line:
                    continue
                elif 'upload_video_to_google_drive' in line:
                    continue
                # If we hit a line that looks like it should be at the main level
                elif not line.startswith('                '):
                    skip_lines = False
                    fixed_lines.append(line)
                    continue
                else:
                    continue
    
    # For all other lines, keep as is
    fixed_lines.append(line)

# Write the fixed file
with open('src/workflow_runner.py', 'w') as f:
    f.writelines(fixed_lines)

print("✅ Fixed workflow structure")

# Show the fixed area
print("\nFixed lines 140-155:")
for i in range(140, min(155, len(fixed_lines))):
    if i < len(fixed_lines):
        print(f"{i}: {fixed_lines[i]}", end='')
