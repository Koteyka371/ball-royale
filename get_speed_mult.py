with open("src/ai/action.py") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "speed = getattr(self.ball, \"speed\"" in line:
        print(f"{i}: {line.strip()}")
