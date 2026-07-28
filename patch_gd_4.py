with open("src/ai/action.gd", "r") as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    if line.strip() == 'vx = cos(angle) * b_speed' and 'var b_speed =' in lines[i-1]:
        new_lines.append('                        b_speed *= 1.5\n')
        new_lines.append(line)
    elif line.strip() == 'var vx = self.ball.vx if "vx" in self.ball else (self.ball.get("vx", 0.0) if typeof(self.ball) == TYPE_DICTIONARY else (self.ball.get_meta("vx") if self.ball.has_method("get_meta") and self.ball.has_meta("vx") else 0.0))':
        new_lines.append(line)
    elif line.strip() == 'if speed < 0.001:':
        new_lines.append('                    if speed >= 0.001:\n')
        new_lines.append('                        var max_s = (self.ball.speed if "speed" in self.ball else (self.ball.get("speed", 100.0) if typeof(self.ball) == TYPE_DICTIONARY else (self.ball.get_meta("speed") if self.ball.has_method("get_meta") and self.ball.has_meta("speed") else 100.0))) * 1.5\n')
        new_lines.append('                        vx = (vx / speed) * max_s\n')
        new_lines.append('                        vy = (vy / speed) * max_s\n')
        new_lines.append(line)
    else:
        new_lines.append(line)

with open("src/ai/action.gd", "w") as f:
    f.writelines(new_lines)
