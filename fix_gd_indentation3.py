with open("src/ai/action.gd", "r") as f:
    lines = f.readlines()

def get_indent(line):
    return len(line) - len(line.lstrip())

# The issue is the blocks inside the `if` and `elif` statements were not indented correctly
# Let's fix lines where is_qs = ... is not indented relative to the previous line
for i in range(len(lines)):
    line = lines[i]
    if "is_qs = " in line and ("self.ball.get_meta(\"is_in_quicksand\")" in line or "self.ball.is_in_quicksand" in line):
        prev_line = lines[i-1]
        if "if self.ball.has_method" in prev_line or "elif \"is_in_quicksand\" in self.ball:" in prev_line:
            prev_indent = get_indent(prev_line)
            current_indent = get_indent(line)
            if current_indent <= prev_indent:
                lines[i] = (" " * (prev_indent + 4)) + line.lstrip()

    if "dmg *= 2.0" in line or "hd *= 2.0" in line:
        prev_line = lines[i-1]
        if "if is_qs:" in prev_line:
            prev_indent = get_indent(prev_line)
            current_indent = get_indent(line)
            if current_indent <= prev_indent:
                lines[i] = (" " * (prev_indent + 4)) + line.lstrip()

    if "self.ball.take_damage(dmg)" in line or "self.ball.hp -= dmg" in line:
        # Check if it was indented as part of if is_qs, and unindent it
        # Actually it should be at the same level as the "if is_qs:"
        for j in range(1, 5):
            if i-j >= 0 and "if is_qs:" in lines[i-j]:
                prev_indent = get_indent(lines[i-j])
                lines[i] = (" " * prev_indent) + line.lstrip()
                break

with open("src/ai/action.gd", "w") as f:
    f.writelines(lines)
