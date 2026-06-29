with open("src/ai/action.py", "r") as f:
    content = f.read()

content = content.replace("                import random\n                    trap_id =", "                import random\n                trap_id =")
content = content.replace("                    import random\n                        decoy.id =", "                    import random\n                    decoy.id =")

with open("src/ai/action.py", "w") as f:
    f.write(content)
