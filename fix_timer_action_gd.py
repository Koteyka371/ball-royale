import re
with open('src/ai/action.gd', 'r') as f:
    content = f.read()

timer_block = """
func _update_skill_timer(delta: float) -> void:
    if "skill_timer" in self.ball and self.ball.skill_timer != null and self.ball.skill_timer > 0:
        self.ball.skill_timer -= delta

    if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("get_meta") and self.ball.has_meta("sonar_ping_timer"):
        var spt = self.ball.get_meta("sonar_ping_timer")
        if spt > 0: self.ball.set_meta("sonar_ping_timer", spt - delta)
    elif typeof(self.ball) == TYPE_DICTIONARY and "sonar_ping_timer" in self.ball:
        var spt = self.ball["sonar_ping_timer"]
        if spt > 0: self.ball["sonar_ping_timer"] = spt - delta
    elif "sonar_ping_timer" in self.ball and self.ball.sonar_ping_timer != null and self.ball.sonar_ping_timer > 0:
        self.ball.sonar_ping_timer -= delta
"""
# Let's replace func _update_skill_timer
if "func _update_skill_timer(delta: float) -> void:" in content:
    content = re.sub(
        r'func _update_skill_timer\(delta: float\) -> void:\s*if "skill_timer" in self\.ball and self\.ball\.skill_timer != null and self\.ball\.skill_timer > 0:\s*self\.ball\.skill_timer -= delta',
        timer_block.strip(),
        content
    )

with open('src/ai/action.gd', 'w') as f:
    f.write(content)
