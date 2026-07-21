# Verify GDScript has timer decrementing logic
with open("src/ai/action.gd", "r") as f:
    text = f.read()

print("GM timer occurences in action.gd:")
for line in text.split("\n"):
    if "gravity_multiplier_timer" in line:
        print(line.strip())
