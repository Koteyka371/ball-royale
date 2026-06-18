import os

with open('scripts/dispatch_agents.py', 'r') as f:
    text = f.read()

new_agents = {
    'agent-21': 'ai-core', 'agent-22': 'behaviors', 'agent-23': 'tests', 'agent-24': 'content',
    'agent-25': 'meta', 'agent-26': 'innovation', 'agent-27': 'content', 'agent-28': 'tests',
    'agent-29': 'behaviors', 'agent-30': 'meta'
}

for ag, area in new_agents.items():
    if f'"{ag}"' not in text:
        text = text.replace('"agent-20": "content"', f'"agent-20": "content",\n    "{ag}": "{area}"')

with open('scripts/dispatch_agents.py', 'w') as f:
    f.write(text)

with open('scripts/launch_agent.py', 'r') as f:
    text = f.read()
text = text.replace('agent_num > 20', 'agent_num > 30')
text = text.replace('1-20 only', '1-30 only')
with open('scripts/launch_agent.py', 'w') as f:
    f.write(text)

with open('.github/workflows/jules-agent-1.yml', 'r') as f:
    tmpl = f.read()
for i in range(21, 31):
    with open(f'.github/workflows/jules-agent-{i}.yml', 'w') as f:
        f.write(tmpl.replace('Jules Agent 1', f'Jules Agent {i}').replace('agent-1', f'agent-{i}'))

print('Added 10 more agents.')
