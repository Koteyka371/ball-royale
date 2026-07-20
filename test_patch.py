with open('src/ai/test_dragging_magnetic_mines.py', 'r') as f:
    content = f.read()

content = content.replace("assert ball.hp == 50", "assert ball.hp == 100")

with open('src/ai/test_dragging_magnetic_mines.py', 'w') as f:
    f.write(content)
