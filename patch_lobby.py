import sys

def patch_file(filepath):
    with open(filepath, "r") as f:
        content = f.read()

    target = '["swift", "slow", "sturdy", "fragile", "lethal", "weak", "soul_dropper", "quantum_entangled"]'
    new_str = '["swift", "slow", "sturdy", "fragile", "lethal", "weak", "soul_dropper", "quantum_entangled", "quantum_echo"]'

    content = content.replace(target, new_str)

    with open(filepath, "w") as f:
        f.write(content)

patch_file("src/system/lobby.py")
patch_file("src/system/lobby.gd")
