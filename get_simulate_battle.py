import sys

with open("tests/simulate_battle.py", 'r') as f:
    text = f.read()

# find check_winner
for i, line in enumerate(text.split('\n')):
    if "check_winner" in line or "match_over" in line or "winner" in line:
        print(f"L{i}: {line.strip()}")
