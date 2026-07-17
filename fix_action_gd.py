with open("src/ai/action.gd", "r") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'if skill_timer <= 0.0 and self.ball.has_method("use_skill"):' in line:
        pass
