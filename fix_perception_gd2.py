import re
with open('src/ai/perception.gd', 'r') as f:
    content = f.read()

sonar_block = """
    var has_sonar = false
    if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("get_meta") and self.ball.has_meta("sonar_ping_timer"):
        has_sonar = float(self.ball.get_meta("sonar_ping_timer")) > 0
    elif typeof(self.ball) == TYPE_DICTIONARY and "sonar_ping_timer" in self.ball:
        has_sonar = float(self.ball["sonar_ping_timer"]) > 0
    elif "sonar_ping_timer" in self.ball and self.ball.sonar_ping_timer != null:
        has_sonar = float(self.ball.sonar_ping_timer) > 0

    if has_sonar:
        perception_radius = max(perception_radius, 1500.0)
"""

content = re.sub(
    r'(var perception_radius = 300\.0\n\s*if "perception_radius" in self\.ball:\n\s*perception_radius = self\.ball\.perception_radius\n)',
    r'\1' + sonar_block,
    content
)

if "if has_sonar:\n            filtered_enemies.append(e)\n            continue" not in content:
    content = re.sub(
        r'(for e in entities\.get\("enemies", \[\]\):\n\s*if intersects_smoke\.call\(e\):\n\s*continue\n)',
        r'\1\n        if has_sonar:\n            filtered_enemies.append(e)\n            continue\n',
        content
    )

with open('src/ai/perception.gd', 'w') as f:
    f.write(content)
