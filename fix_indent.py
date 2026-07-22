with open("src/ai/game_modes.py", "r") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if line.startswith("                            self.y = y"):
        new_lines.append(line)
    elif line.startswith("                            self.radius = radius"):
        new_lines.append(line)
    elif line.startswith("                            self.kind = kind"):
        new_lines.append(line)
    elif line.startswith("                            self.damage = damage"):
        new_lines.append(line)
    else:
        new_lines.append(line)

with open("src/ai/game_modes.py", "w") as f:
    f.writelines(new_lines)
