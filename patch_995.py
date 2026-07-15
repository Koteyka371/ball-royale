with open("src/ai/test_idea_995.py", "r") as f:
    text = f.read()
text = text.replace("from src.ai.game_modes", "from ai.game_modes")
with open("src/ai/test_idea_995.py", "w") as f:
    f.write(text)
