import re
with open("src/ai/action.py", "r") as f:
    code = f.read()

new_code = code.replace(
"""                new_speed = min(speed * 1.5, 2000.0)  # Increase speed, cap at 2000""",
"""                new_speed = min(speed * 1.5, 2000.0)  # Increase speed, cap at 2000
                if getattr(self.ball, "in_ice_patch", False):
                    new_speed = min(speed * 2.0, 3000.0)""")

with open("src/ai/action.py", "w") as f:
    f.write(new_code)
