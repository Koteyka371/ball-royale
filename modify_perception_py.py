import re

with open('src/ai/perception.py', 'r') as f:
    content = f.read()

# At the top of `def scan(self) -> Dict[str, Any]:`
# Add checking for sonar_ping_timer
sonar_block = """
        has_sonar = getattr(self.ball, "sonar_ping_timer", 0.0) > 0
        if has_sonar:
            perception_radius = max(perception_radius, 1500.0)
"""
if "has_sonar" not in content:
    content = re.sub(
        r'(perception_radius = getattr\(self\.ball, "perception_radius", 300\.0\))',
        r'\1\n' + sonar_block,
        content
    )

# In `intersects_smoke` logic, if has_sonar, bypass
if "if has_sonar:\n                return False" not in content:
    content = re.sub(
        r'(def intersects_smoke\(ent\):\n\s*)(ex, ey)',
        r'\1if has_sonar:\n                return False\n            \2',
        content
    )

# In enemy stealth checks, if has_sonar, bypass
if "if has_sonar:\n                filtered_enemies.append(e)\n                continue" not in content:
    content = re.sub(
        r'(for e in entities\.get\("enemies", \[\]\):\n\s*if intersects_smoke\(e\):\n\s*continue\n)',
        r'\1\n            if has_sonar:\n                filtered_enemies.append(e)\n                continue\n',
        content
    )

with open('src/ai/perception.py', 'w') as f:
    f.write(content)
