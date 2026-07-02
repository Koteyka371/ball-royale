with open("src/ai/action.py", "r") as f:
    content = f.read()

content = content.replace(
    'if hasattr(self.ball, "invert_timer") and self.ball.invert_timer > 0:\n            self.ball.invert_timer -= delta\n            if self.ball.invert_timer < 0:\n                self.ball.invert_timer = 0.0\n        if hasattr(self.ball, "nemesis_booster_timer") and self.ball.nemesis_booster_timer > 0:',
    'if hasattr(self.ball, "invert_timer") and self.ball.invert_timer > 0:\n            self.ball.invert_timer -= delta\n            if self.ball.invert_timer < 0:\n                self.ball.invert_timer = 0.0\n\n        if hasattr(self.ball, "nemesis_booster_timer") and self.ball.nemesis_booster_timer > 0:'
)

with open("src/ai/action.py", "w") as f:
    f.write(content)
