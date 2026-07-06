import re
with open('src/ai/action.py', 'r') as f:
    content = f.read()

timer_block = """
        if hasattr(self.ball, "sonar_ping_timer") and self.ball.sonar_ping_timer > 0:
            self.ball.sonar_ping_timer -= delta
"""
if "sonar_ping_timer -= delta" not in content:
    content = re.sub(
        r'(if hasattr\(self\.ball, "skill_timer"\) and self\.ball\.skill_timer > 0:\n\s*self\.ball\.skill_timer -= delta)',
        r'\1' + timer_block,
        content
    )

with open('src/ai/action.py', 'w') as f:
    f.write(content)
