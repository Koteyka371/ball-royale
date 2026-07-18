with open("src/tests/test_bone_wall.py", "r") as f:
    content = f.read()

content = content.replace("action.execute(\"idle\", 0.1)", "action.execute(\"use_skill\", 0.1)")

with open("src/tests/test_bone_wall.py", "w") as f:
    f.write(content)
