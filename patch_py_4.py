with open("src/ai/action.py", "r") as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    if line.strip() == 'decoy.vx = vx' and 'if speed > 0.001:' in lines[i-1]:
        new_lines.append('                        # scale to max speed\n')
        new_lines.append('                        max_s = getattr(self.ball, "speed", 200.0) * 1.5\n')
        new_lines.append('                        decoy.vx = (vx / speed) * max_s\n')
        new_lines.append('                        decoy.vy = (vy / speed) * max_s\n')
    elif line.strip() == 'decoy.vy = vy' and 'if speed > 0.001:' in lines[i-2]:
        pass # we handled it above
    elif line.strip() == 'b_speed = getattr(self.ball, "speed", 100.0)':
        new_lines.append('                        b_speed = getattr(self.ball, "speed", 100.0) * 1.5\n')
    else:
        new_lines.append(line)

with open("src/ai/action.py", "w") as f:
    f.writelines(new_lines)
