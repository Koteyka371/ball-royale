with open('src/ai/action.gd', 'r') as f:
    content = f.read()

content = content.replace('\x01', 'elif skill_name == "flare":')

with open('src/ai/action.gd', 'w') as f:
    f.write(content)
