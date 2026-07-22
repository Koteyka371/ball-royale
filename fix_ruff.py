with open("src/ai/game_modes.py", "r") as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    if "new_explosions = [] # explosions added during this tick" in line:
        continue
    if line.strip() == "import random":
        # Check if it's the one at 32953
        if "Spawn anchor in the center" in lines[i-1]:
            continue
    new_lines.append(line)

with open("src/ai/game_modes.py", "w") as f:
    f.writelines(new_lines)
