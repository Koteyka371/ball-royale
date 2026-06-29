import re

with open("src/ai/action.py", "r") as f:
    content = f.read()

# Add import random to the top if it's missing (it says name random used before definition)
if 'import random' not in content:
    content = 'import random\n' + content

with open("src/ai/action.py", "w") as f:
    f.write(content)
