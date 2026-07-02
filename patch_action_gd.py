import re

with open("src/ai/action.gd", "r") as f:
    content = f.read()

# Add to _update_skill_timer
content = content.replace(
    '"clone_booster", "placeable_trap_booster", "nemesis_booster"]',
    '"clone_booster", "placeable_trap_booster", "nemesis_booster", "invert_booster"]'
)

content = content.replace(
    'if "nemesis_booster_timer" in self.ball:',
    'if "invert_timer" in self.ball:\n        var inv_t = float(self.ball.invert_timer)\n        if inv_t > 0:\n            inv_t -= delta\n            if inv_t < 0: inv_t = 0.0\n            self.ball.invert_timer = inv_t\n    elif self.ball.has_method("get_meta") and self.ball.has_meta("invert_timer"):\n        var inv_t = float(self.ball.get_meta("invert_timer"))\n        if inv_t > 0:\n            inv_t -= delta\n            if inv_t < 0: inv_t = 0.0\n            self.ball.set_meta("invert_timer", inv_t)\n\n    if "nemesis_booster_timer" in self.ball:',
    1
)

# Add the booster collection logic
booster_logic = """            elif "kind" in nearest and nearest.kind == "invert_booster":
                if self.world != null and "balls" in self.world:
                    for other in self.world.balls:
                        var my_team = -2
                        if "team" in self.ball: my_team = self.ball.team
                        var other_team = -1
                        if "team" in other: other_team = other.team
                        if other_team != my_team and other.get("hp", 0) > 0:
                            if "invert_timer" in other:
                                other.invert_timer = 5.0
                            elif other.has_method("set_meta"):
                                other.set_meta("invert_timer", 5.0)
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    if self.world.arena.hazards.has(nearest):
                        self.world.arena.hazards.erase(nearest)
                if self.world != null and "boosters" in self.world and self.world.boosters.has(nearest):
                    self.world.boosters.erase(nearest)
"""

content = content.replace(
    '            elif "kind" in nearest and nearest.kind == "nemesis_booster":',
    booster_logic + '            elif "kind" in nearest and nearest.kind == "nemesis_booster":'
)

# Reverse speeds
content = re.sub(
    r'(var step = speed \* delta \* 60\.0)',
    r'\1\n                var inv_t = 0.0\n                if "invert_timer" in self.ball: inv_t = float(self.ball.invert_timer)\n                elif self.ball.has_method("get_meta") and self.ball.has_meta("invert_timer"): inv_t = float(self.ball.get_meta("invert_timer"))\n                if inv_t > 0.0:\n                    step = -step',
    content
)

content = re.sub(
    r'(var step: float = b_speed \* delta \* 60\.0)',
    r'\1\n                var inv_t = 0.0\n                if "invert_timer" in self.ball: inv_t = float(self.ball.invert_timer)\n                elif self.ball.has_method("get_meta") and self.ball.has_meta("invert_timer"): inv_t = float(self.ball.get_meta("invert_timer"))\n                if inv_t > 0.0:\n                    step = -step',
    content
)

content = re.sub(
    r'(var step = b_speed \* delta \* 60\.0)',
    r'\1\n        var inv_t = 0.0\n        if "invert_timer" in ball: inv_t = float(ball.invert_timer)\n        elif ball.has_method("get_meta") and ball.has_meta("invert_timer"): inv_t = float(ball.get_meta("invert_timer"))\n        if inv_t > 0.0:\n            step = -step',
    content
)

with open("src/ai/action.gd", "w") as f:
    f.write(content)
