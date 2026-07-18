with open("src/ai/action.py", "r") as f:
    text = f.read()

replacement = """        if bounced_wall:
            if getattr(self.ball, "wall_stick_timer", 0.0) <= 0.0:
                self.ball.wall_stick_timer = 2.0
                self.ball.is_stunned = True"""

replacement_new = """        if bounced_wall and not getattr(self.ball, "is_stunned", False):
            if getattr(self.ball, "wall_stick_timer", 0.0) <= 0.0:
                self.ball.wall_stick_timer = 2.0
                self.ball.is_stunned = True"""

text = text.replace(replacement, replacement_new)

with open("src/ai/action.py", "w") as f:
    f.write(text)
