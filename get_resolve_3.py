with open("src/ai/action.py", "r") as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if "for hazard in self.world.arena.hazards:" in line:
        print(f"Line {i}: {line.strip()}")
