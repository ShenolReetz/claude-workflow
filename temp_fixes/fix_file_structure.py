#!/usr/bin/env python3
"""
Fix the file structure
"""

# Read the file
with open('/home/claude-workflow/src/workflow_runner.py', 'r') as f:
    lines = f.readlines()

# Find the problematic area and fix it
fixed_lines = []
i = 0

while i < len(lines):
    line = lines[i]
    
    # If we find the error saving line followed by if __name__
    if 'Error saving to Airtable' in line and i + 1 < len(lines):
        fixed_lines.append(line)
        
        # Check next line
        next_line = lines[i + 1]
        if 'if __name__' in next_line or 'if **name**' in next_line:
            # This is wrong - we need to close the method first
            # Add proper method closing
            fixed_lines.append('\n')
            fixed_lines.append('\n# Run the workflow\n')
            fixed_lines.append('if __name__ == "__main__":\n')
            i += 2  # Skip the malformed if line
            continue
    
    # Fix any malformed if __name__ lines
    if 'if **name**' in line or ('if __name__' in line and ':' not in line):
        fixed_lines.append('if __name__ == "__main__":\n')
    else:
        fixed_lines.append(line)
    
    i += 1

# Write back
with open('/home/claude-workflow/src/workflow_runner.py', 'w') as f:
    f.writelines(fixed_lines)

print("✅ Fixed file structure")
