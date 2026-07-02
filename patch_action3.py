with open("src/ai/action.py", "r") as f:
    content = f.read()

import re

# Need to avoid quicksand/shrinking zone twice, let's use search and replace with 1 instance.
with open("src/ai/action.py", "w") as f:
    f.write(content)
