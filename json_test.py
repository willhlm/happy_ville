import json

with open('pathways_config.json') as f:
    config = json.load(f)

print(config)
