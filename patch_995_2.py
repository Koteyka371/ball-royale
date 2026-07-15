with open("src/ai/test_idea_995.py", "r") as f:
    text = f.read()
text = text.replace("from src.ai.", "from ai.")
with open("src/ai/test_idea_995.py", "w") as f:
    f.write(text)
