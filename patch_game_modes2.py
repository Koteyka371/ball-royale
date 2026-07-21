with open("src/ai/game_modes.py", "r") as f:
    content = f.read()
content = content.replace("from ai.ball_types_easy import Easy", "from ai.ball_types_easy import Easy\nfrom ai.ball_types_mirror import Mirror")
with open("src/ai/game_modes.py", "w") as f:
    f.write(content)
