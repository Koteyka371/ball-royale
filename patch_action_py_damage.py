with open("src/ai/action.py", "r") as f:
    content = f.read()

search = """        if is_nemesis_active:
            attacker.damage = original_damage * 1.2"""

# Make sure it uses setter or sets attribute correctly, though looking at the code reviewer feedback:
# "The 20% bonus damage mechanic is completely missing from both the Python (action.py) and GDScript (action.gd) implementations."
# Wait, it's ALREADY THERE in both.
