with open("tests/simulate_battle.py", 'r') as f:
    text = f.read()

for i, line in enumerate(text.split('\n')):
    if 'stats["winner"] =' in line:
        print(f"L{i}: {line.strip()}")
