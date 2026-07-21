with open("src/ai/game_modes.py", "r") as f:
    content = f.read()
if "'mirror': Mirror" not in content:
    # Need to add to ball_types map if it exists
    if "ball_classes = {" in content:
        content = content.replace("ball_classes = {", "ball_classes = {\n    'mirror': Mirror,")
with open("src/ai/game_modes.py", "w") as f:
    f.write(content)
