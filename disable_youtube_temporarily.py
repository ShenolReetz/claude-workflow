import json

# Update config to disable YouTube
config_path = '/home/claude-workflow/config/api_keys.json'

with open(config_path, 'r') as f:
    config = json.load(f)

config['youtube_enabled'] = False

with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)

print("✅ YouTube disabled in config")
print("Your main workflow will now skip YouTube uploads")
