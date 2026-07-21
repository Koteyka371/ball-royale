import re

with open("src/ai/action.py", "r") as f:
    content = f.read()

# Fix the duplicate block
duplicate_block = """        if getattr(self.ball, "ball_type", getattr(self.ball.__class__, "BALL_TYPE", "")).lower() == "mirror":
            negative_statuses = ["emp_timer", "poison_timer", "slow_timer", "burn_timer", "confusion_timer", "blindness_timer", "frozen_timer", "stun_timer", "silence_timer"]
            has_status = False
            for stat in negative_statuses:
                if getattr(self.ball, stat, 0.0) > 0:
                    has_status = True
                    break
            if has_status:
                nearest_enemy = None
                min_dist = float('inf')
                if hasattr(self.world, "balls"):
                    for b in self.world.balls:
                        if getattr(b, "alive", True) and b.id != getattr(self.ball, "id", None) and getattr(b, "team", getattr(b, "ball_type", "")) != getattr(self.ball, "team", "mirror"):
                            dist = (b.x - self.ball.x)**2 + (b.y - self.ball.y)**2
                            if dist < min_dist:
                                min_dist = dist
                                nearest_enemy = b
                if nearest_enemy:
                    for stat in negative_statuses:
                        val = getattr(self.ball, stat, 0.0)
                        if val > 0:
                            setattr(nearest_enemy, stat, max(getattr(nearest_enemy, stat, 0.0), val))
                            setattr(self.ball, stat, 0.0)
                    if getattr(self.ball, "is_emped", False):
                        nearest_enemy.is_emped = True
                        self.ball.is_emped = False
                    if getattr(self.ball, "is_stunned", False):
                        nearest_enemy.is_stunned = True
                        self.ball.is_stunned = False

"""

content = content.replace(duplicate_block + duplicate_block, duplicate_block)
with open("src/ai/action.py", "w") as f:
    f.write(content)
