with open('src/ai/action.py', 'r') as f:
    content = f.read()

# Let's replace _random with random
content = content.replace('_random.uniform', 'random.uniform')
content = content.replace('_math.pi', 'math.pi')
content = content.replace('_math.cos', 'math.cos')
content = content.replace('_math.sin', 'math.sin')

with open('src/ai/action.py', 'w') as f:
    f.write(content)
