import re

with open("src/ai/action.py", "r") as f:
    content = f.read()

# Add to _update_skill_timer
content = content.replace(
    '"clone_booster", "placeable_trap_booster", "nemesis_booster"]:',
    '"clone_booster", "placeable_trap_booster", "nemesis_booster", "invert_booster"]:'
)

content = content.replace(
    'if hasattr(self.ball, "nemesis_booster_timer") and self.ball.nemesis_booster_timer > 0:',
    'if hasattr(self.ball, "invert_timer") and self.ball.invert_timer > 0:\n            self.ball.invert_timer -= delta\n            if self.ball.invert_timer < 0:\n                self.ball.invert_timer = 0.0\n        if hasattr(self.ball, "nemesis_booster_timer") and self.ball.nemesis_booster_timer > 0:',
    1 # Only replace the first occurrence (in _update_skill_timer, not the one in ripple effect)
)


# Add the booster collection logic
booster_logic = """                elif getattr(nearest, "kind", None) == "invert_booster":
                    if hasattr(self.world, "balls"):
                        for other in self.world.balls:
                            if getattr(other, "team", -1) != getattr(self.ball, "team", -2) and getattr(other, "hp", 0) > 0:
                                other.invert_timer = 5.0
                    if hasattr(self.world, "arena") and hasattr(self.world.arena, "hazards"):
                        if nearest in self.world.arena.hazards:
                            self.world.arena.hazards.remove(nearest)
                    if hasattr(self.world, "boosters") and nearest in self.world.boosters:
                        self.world.boosters.remove(nearest)
"""

content = content.replace(
    '                elif getattr(nearest, "kind", None) == "nemesis_booster":',
    booster_logic + '                elif getattr(nearest, "kind", None) == "nemesis_booster":'
)

# Reverse speeds
content = re.sub(
    r'(speed = getattr\(self\.ball, "speed", 2\.0\)\n\s+step = speed \* delta \* 60\.0)',
    r'\1\n            if getattr(self.ball, "invert_timer", 0.0) > 0:\n                step = -step',
    content
)

content = re.sub(
    r'(step = getattr\(self\.ball, "speed", 2\.0\) \* delta \* 60\.0?)',
    r'\1\n        if getattr(self.ball, "invert_timer", 0.0) > 0:\n            step = -step',
    content
)

content = re.sub(
    r'(step = speed \* delta \* 60\.0?)',
    r'\1\n            if getattr(self.ball, "invert_timer", 0.0) > 0:\n                step = -step',
    content
)


with open("src/ai/action.py", "w") as f:
    f.write(content)
