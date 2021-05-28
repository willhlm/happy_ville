import json

with open('pathways_config.json') as f:
    config = json.load(f)

print(config['village1']['pathways']['10'])
