with open("src/ai/action.py", "r") as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    if line.strip() == 'if getattr(self.ball, "is_decoy", False):' and lines[i+1].strip() == 'self.ball.decoy_timer -= delta' and 'Emit aura' in lines[i+3]:
        new_lines.append('        if getattr(self.ball, "is_decoy", False) and getattr(self.ball, "decoy_type", "") != "hologram":\n')
    else:
        new_lines.append(line)

with open("src/ai/action.py", "w") as f:
    f.writelines(new_lines)
