import os, glob

# 1. Update dispatch_agents.py
with open('scripts/dispatch_agents.py', 'r') as f:
    text = f.read()

new_agents = {
    'agent-13': 'tests',
    'agent-14': 'content',
    'agent-15': 'meta',
    'agent-16': 'innovation',
    'agent-17': 'ai-core',
    'agent-18': 'behaviors',
    'agent-19': 'tests',
    'agent-20': 'content'
}

for ag, area in new_agents.items():
    if f'"{ag}"' not in text:
        text = text.replace('"agent-12": "ai-core",', f'"agent-12": "ai-core",\n    "{ag}": "{area}",')

with open('scripts/dispatch_agents.py', 'w') as f:
    f.write(text)

# 2. Update launch_agent.py
with open('scripts/launch_agent.py', 'r') as f:
    text = f.read()
text = text.replace('agent_num > 12', 'agent_num > 20')
text = text.replace('1-6 only', '1-20 only')
with open('scripts/launch_agent.py', 'w') as f:
    f.write(text)

# 3. Create workflow files
with open('.github/workflows/jules-agent-1.yml', 'r') as f:
    tmpl = f.read()

for i in range(13, 21):
    new_yml = tmpl.replace('Jules Agent 1', f'Jules Agent {i}').replace('agent-1', f'agent-{i}')
    with open(f'.github/workflows/jules-agent-{i}.yml', 'w') as f:
        f.write(new_yml)

print('Updated scripts and created 8 new workflows.')
