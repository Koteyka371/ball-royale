with open("src/ai/action.py", "r") as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    new_lines.append(line)
    if "if new_hp < old_hp:" in line and "Award XP for damage dealt and kills" in lines[i-1]:
        # Need to find the exact place
        pass

with open("src/ai/action.py", "w") as f:
    f.writelines(new_lines)
