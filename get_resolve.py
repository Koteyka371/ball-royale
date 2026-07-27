import re

with open("src/ai/action.py", "r") as f:
    data = f.read()

start = data.find("def _resolve_collisions")
print(data[start:start+1500])
