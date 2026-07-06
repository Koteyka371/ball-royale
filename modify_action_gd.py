import re

with open('src/ai/action.gd', 'r') as f:
    content = f.read()

# Add sonar_ping_timer logic in execute (at the bottom where skill_timer is updated)
timer_block = """
        if "sonar_ping_timer" in self.ball and self.ball.sonar_ping_timer != null and self.ball.sonar_ping_timer > 0:
            self.ball.sonar_ping_timer -= delta
"""
content = re.sub(
    r'(if "skill_timer" in self\.ball and self\.ball\.skill_timer != null and self\.ball\.skill_timer > 0:\s*self\.ball\.skill_timer -= delta)',
    r'\1' + timer_block,
    content
)

# Add elif skill_name == "sonar_ping":
skill_block = """
        elif skill_name == "sonar_ping":
            if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"):
                self.ball.set_meta("sonar_ping_timer", 5.0)
            elif typeof(self.ball) == TYPE_DICTIONARY:
                self.ball["sonar_ping_timer"] = 5.0
            elif "sonar_ping_timer" in self.ball:
                self.ball.sonar_ping_timer = 5.0

            if self.world.has_method("add_event"):
                var event_payload = {"x": self.ball.x, "y": self.ball.y, "radius": 1500.0}
                if "id" in self.ball: event_payload["source_id"] = self.ball.id
                self.world.add_event("sonar_ping", event_payload)

            var cool = 12.0
            if "skill_cooldown" in self.ball: cool = self.ball.skill_cooldown
            if "skill_timer" in self.ball: self.ball.skill_timer = cool
            elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"): self.ball.set_meta("skill_timer", cool)
"""
content = re.sub(
    r'(elif skill_name == "flare":)',
    skill_block.strip() + '\n        \1',
    content
)

with open('src/ai/action.gd', 'w') as f:
    f.write(content)
