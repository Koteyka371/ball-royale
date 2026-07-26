import re

with open('src/ai/action.py', 'r') as f:
    content = f.read()

search = """            if hasattr(self.ball, "speed_multiplier"):
                self.ball.speed_multiplier = max(getattr(self.ball, "speed_multiplier", 1.0), 1.5)"""

# Add a boolean flag so we can restore speed. Or instead of modifying speed_multiplier,
# wait, speed_multiplier is usually recalculated or reset? No, it's persistent.
# How do other boosters revert?
# Looking at crystal_armor:
# self.ball.speed_multiplier /= (0.8 ** 3)
# It's better to use a flag. Or since it's shadow_booster, when it drops below 0:

replace = """            if hasattr(self.ball, "speed_multiplier") and not getattr(self.ball, "shadow_speed_applied", False):
                self.ball.speed_multiplier *= 1.5
                self.ball.shadow_speed_applied = True"""

if search in content:
    content = content.replace(search, replace)
else:
    print("Could not find search block in action.py")

# Now handle the reversion when timer reaches 0
search2 = """            if self.ball.shadow_booster_timer < 0:
                self.ball.shadow_booster_timer = 0.0"""

replace2 = """            if self.ball.shadow_booster_timer <= 0:
                self.ball.shadow_booster_timer = 0.0
                if getattr(self.ball, "shadow_speed_applied", False):
                    if hasattr(self.ball, "speed_multiplier"):
                        self.ball.speed_multiplier /= 1.5
                    self.ball.shadow_speed_applied = False"""

if search2 in content:
    content = content.replace(search2, replace2)
else:
    print("Could not find search2 block in action.py")

with open('src/ai/action.py', 'w') as f:
    f.write(content)
