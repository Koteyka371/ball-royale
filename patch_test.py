import re

with open("src/ai/test_breach_charge.py", "r") as f:
    content = f.read()

content = content.replace("assert len(world.arena.hazards) == 1", "assert len(world.arena.hazards) == 2")
content = content.replace('assert world.arena.hazards[0].kind == "breakable_wall"', 'assert bumper.emp_disabled_timer == 15.0')
content = content.replace('assert world.arena.hazards[0].kind == "bumper"', 'assert wall.emp_disabled_timer == 15.0')

content = content.replace('def __init__(self, x=0, y=0, radius=10, kind="bumper"):', 'def __init__(self, x=0, y=0, radius=10, kind="bumper"):\n        self.emp_disabled_timer = 0.0')


with open("src/ai/test_breach_charge.py", "w") as f:
    f.write(content)
