with open('src/workflow_runner.py', 'r') as f:
    lines = f.readlines()

# Find where other agents are initialized (in __init__ method)
fixed_lines = []
added_gdrive = False

for i, line in enumerate(lines):
    # Add the line first
    fixed_lines.append(line)
    
    # If we're in the __init__ method and see other agent initializations
    if '__init__' in line and 'self' in line:
        # Look for where to add Google Drive agent
        j = i + 1
        while j < len(lines) and lines[j].strip() and not lines[j].strip().startswith('def '):
            if 'self.config = config' in lines[j] and not added_gdrive:
                # Add Google Drive agent initialization after config
                fixed_lines.append(lines[j])
                fixed_lines.append('        # Initialize Google Drive agent\n')
                fixed_lines.append('        self.google_drive_agent = GoogleDriveAgent()\n')
                added_gdrive = True
                j += 1
                continue
            fixed_lines.append(lines[j])
            j += 1
        i = j - 1

# If we didn't find a good place to add it, add it at the class level
if not added_gdrive:
    # Find the class definition
    for i, line in enumerate(fixed_lines):
        if 'class WorkflowRunner' in line:
            # Find the __init__ method
            for j in range(i, len(fixed_lines)):
                if 'def __init__' in fixed_lines[j]:
                    # Find the end of __init__ parameters
                    k = j
                    while k < len(fixed_lines) and not fixed_lines[k].strip().endswith(':'):
                        k += 1
                    # Insert after the config line
                    for m in range(k, len(fixed_lines)):
                        if 'self.config = config' in fixed_lines[m]:
                            fixed_lines.insert(m + 1, '        self.google_drive_agent = GoogleDriveAgent()\n')
                            added_gdrive = True
                            break
                    break
            break

# Write back
with open('src/workflow_runner.py', 'w') as f:
    f.writelines(fixed_lines)

print(f"✅ Added Google Drive agent initialization: {added_gdrive}")
