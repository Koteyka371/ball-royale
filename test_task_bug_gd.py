import re

with open("src/ai/action.gd", "r") as f:
    text = f.read()

# I will replace the division by zero guard issue in the python action.py first.
