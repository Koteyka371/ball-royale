with open("src/ai/action.gd", "r") as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    if line.strip() == 'if "decoy_timer" in my_ball:' and 'var dt = 0.0' in lines[i-1] and 'my_ball.decoy_timer -= delta' in lines[i+1]:
        new_lines.append('        if decoy_type != "hologram" and "decoy_timer" in my_ball:\n')
    elif line.strip() == 'elif my_ball.has_method("get_meta") and my_ball.has_meta("decoy_timer"):' and 'my_ball.decoy_timer -= delta' in lines[i-2]:
        new_lines.append('        elif decoy_type != "hologram" and my_ball.has_method("get_meta") and my_ball.has_meta("decoy_timer"):\n')
    else:
        new_lines.append(line)

with open("src/ai/action.gd", "w") as f:
    f.writelines(new_lines)
