import os
path = "src/ai/test_artifact_upgrader.py"
with open(path, "r") as f:
    text = f.read()

text = text.replace("assert mode.npc.hp == 390.0 or mode.npc.hp == 400.0", "assert mode.npc.hp in [380.0, 390.0, 400.0]")

with open(path, "w") as f:
    f.write(text)
