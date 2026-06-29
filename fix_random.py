with open("src/ai/action.py", "r") as f:
    content = f.read()

# Fix random import in python
if "import random" not in content[:50]:
    content = "import random\n" + content

with open("src/ai/action.py", "w") as f:
    f.write(content)
