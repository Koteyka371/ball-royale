import re

with open("tests/test_ice_patches.py", "r") as f:
    content = f.read()

content = content.replace("\\    # Save original position", "    # Save original position")

with open("tests/test_ice_patches.py", "w") as f:
    f.write(content)
