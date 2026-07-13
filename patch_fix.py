with open("src/ai/action.py", "r") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "ghost_mode_timer -= delta" in line:
        print(f"Match at line {i}")
        for j in range(max(0, i-20), min(len(lines), i+10)):
            print(lines[j], end="")
        print("-" * 40)
