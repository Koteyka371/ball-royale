with open("src/arena/arena_types.gd", "r") as f:
    content = f.read()

# Check if tornado is exported in some array or dict
print("tornado" in content)

with open("src/arena/arena_types.py", "r") as f:
    content = f.read()

print("tornado" in content)
