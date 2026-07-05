import re
with open("src/ai/test_ice_patch.py", "r") as f:
    code = f.read()

new_code = code.replace(
"""    ball.x = 995 # Near edge
    ball.vx = 100.0""",
"""    ball.x = 995 # Near edge
    ball.vx = 100.0
    ball._reflection_vx = 200.0
    ball._reflection_vy = 0.0""")

with open("src/ai/test_ice_patch.py", "w") as f:
    f.write(new_code)
