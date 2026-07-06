import re

with open('src/ai/action.py', 'r') as f:
    content = f.read()

# Add sonar_ping_timer decrement in execute
# Looking for self._chrono_slow = 0.0 or similar to add it near the top of execute()
# wait, there's `skill_timer = getattr(self.ball, "skill_timer", 0.0)` block
if "def execute(self, delta: float) -> None:" in content:
    # let's add it right after `if hasattr(self.ball, "anchor_booster_timer"):` or similar
    # or just find `skill_timer = getattr(self.ball, "skill_timer", 0.0)` in execute
    content = re.sub(
        r'(if hasattr\(self\.ball, "skill_timer"\) and self\.ball\.skill_timer > 0:\s*self\.ball\.skill_timer -= delta)',
        r'\1\n        if hasattr(self.ball, "sonar_ping_timer") and self.ball.sonar_ping_timer > 0:\n            self.ball.sonar_ping_timer -= delta',
        content
    )

# Add elif skill_name == "sonar_ping":
skill_block = """
            elif skill_name == "sonar_ping":
                setattr(self.ball, "sonar_ping_timer", 5.0)
                if hasattr(self.world, "add_event"):
                    self.world.add_event("sonar_ping", {"x": self.ball.x, "y": self.ball.y, "radius": 1500.0, "source_id": getattr(self.ball, "id", None)})
                self.ball.skill_timer = getattr(self.ball, "skill_cooldown", 12.0)
"""
content = re.sub(
    r'(elif skill_name == "flare":)',
    skill_block.strip() + '\n            \1',
    content
)

with open('src/ai/action.py', 'w') as f:
    f.write(content)
