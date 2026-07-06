import re

with open("src/ai/action.gd", "r") as f:
    content = f.read()

print("energy_barrier" in content)
print("energy_shield" in content)
