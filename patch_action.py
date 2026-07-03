import re

with open("src/ai/action.py", "r") as f:
    py_content = f.read()

# 1. Add _collect_booster logic for disruptor_booster
booster_logic = """
                elif getattr(nearest, "kind", None) == "disruptor_booster":
                    self.ball.disruptor_aura_timer = 5.0
                    if hasattr(self.world, "arena") and hasattr(self.world.arena, "hazards"):
                        if nearest in self.world.arena.hazards:
                            self.world.arena.hazards.remove(nearest)
                    if hasattr(self.world, "boosters") and nearest in self.world.boosters:
                        self.world.boosters.remove(nearest)
                elif getattr(nearest, "kind", None) == "vision_booster":"""
py_content = py_content.replace('                elif getattr(nearest, "kind", None) == "vision_booster":', booster_logic)

# 2. Add update_skill_timer logic
timer_logic = """    def _update_skill_timer(self, delta: float) -> None:
        if getattr(self.ball, "disruptor_aura_timer", 0.0) > 0:
            self.ball.disruptor_aura_timer -= delta
            if self.ball.disruptor_aura_timer < 0:
                self.ball.disruptor_aura_timer = 0.0
            if hasattr(self.world, "balls"):
                my_team = getattr(self.ball, "team", getattr(self.ball, "ball_type", ""))
                for other in self.world.balls:
                    if getattr(other, "alive", True) and getattr(other, "id", None) != getattr(self.ball, "id", None):
                        other_team = getattr(other, "team", getattr(other, "ball_type", ""))
                        if other_team != my_team:
                            dx = self.ball.x - other.x
                            dy = self.ball.y - other.y
                            if (dx*dx + dy*dy) <= 22500.0:  # 150^2
                                other.aura_disruption_timer = 0.5

        if getattr(self.ball, "aura_disruption_timer", 0.0) > 0:
            self.ball.aura_disruption_timer -= delta
            if self.ball.aura_disruption_timer < 0:
                self.ball.aura_disruption_timer = 0.0

"""
py_content = py_content.replace('    def _update_skill_timer(self, delta: float) -> None:\n', timer_logic)

# 3. Add aura logic
aura_logic = """        # Determine aura properties
        aura_radius = 150.0
        if getattr(self.ball, "aura_disruption_timer", 0.0) > 0:
            aura_radius = 0.0

        # Check nearby friendly balls"""
py_content = py_content.replace('        # Determine aura properties\n        aura_radius = 150.0\n\n        # Check nearby friendly balls', aura_logic)

# 4. Add to ignore lists
py_content = py_content.replace('"anchor_booster"]:', '"anchor_booster", "disruptor_booster"]:')


with open("src/ai/action.py", "w") as f:
    f.write(py_content)

print("action.py patched")
