with open("src/ai/action.py", "r") as f:
    content = f.read()

# Fix the indentation on the second one
content = content.replace('''                    if getattr(hazard, "kind", "") == "void_panel":
                    if getattr(self.ball, "bumper_booster_timer", 0.0) > 0.0:
                        continue
                        hx = hazard.x - self.ball.x''', '''                    if getattr(hazard, "kind", "") == "void_panel":
                        if getattr(self.ball, "bumper_booster_timer", 0.0) > 0.0:
                            continue
                        hx = hazard.x - self.ball.x''')

with open("src/ai/action.py", "w") as f:
    f.write(content)
