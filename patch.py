with open("src/tests/test_spiderman.py", "r") as f:
    content = f.read()
if "from ai.spiderman import SpidermanMode" not in content:
    content = "from ai.spiderman import SpidermanMode\n" + content
with open("src/tests/test_spiderman.py", "w") as f:
    f.write(content)
