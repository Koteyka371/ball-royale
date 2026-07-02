import re
with open("src/ai/action.py", "r") as f:
    content = f.read()

content = content.replace(
"""            if getattr(self.ball, "invert_timer", 0.0) > 0:
                step = -step
            if getattr(self.ball, "invert_timer", 0.0) > 0:
                step = -step""",
"""            if getattr(self.ball, "invert_timer", 0.0) > 0:
                step = -step"""
)
content = content.replace(
"""        if getattr(self.ball, "invert_timer", 0.0) > 0:
            step = -step
        if getattr(self.ball, "invert_timer", 0.0) > 0:
            step = -step""",
"""        if getattr(self.ball, "invert_timer", 0.0) > 0:
            step = -step"""
)

with open("src/ai/action.py", "w") as f:
    f.write(content)
