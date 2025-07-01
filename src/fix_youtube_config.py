def fix_config_references():
    workflow_file = '/home/claude-workflow/src/workflow_runner.py'
    
    with open(workflow_file, 'r') as f:
        content = f.read()
    
    # Fix all instances where config is used instead of self.config
    lines = content.split('\n')
    fixed_lines = []
    in_youtube_section = False
    
    for line in lines:
        if 'Upload to YouTube' in line:
            in_youtube_section = True
        elif 'print("✅ Updating record status' in line:
            in_youtube_section = False
            
        if in_youtube_section and 'config.get(' in line and 'self.config' not in line:
            line = line.replace('config.get(', 'self.config.get(')
            
        fixed_lines.append(line)
    
    with open(workflow_file, 'w') as f:
        f.write('\n'.join(fixed_lines))
    
    print("✅ Fixed config references!")

fix_config_references()
