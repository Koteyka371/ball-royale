import re

with open("src/ai/action.py", "r") as f:
    content = f.read()

# Check suspended projectiles logic
matches = re.findall(r'for sp in list\(self.ball.suspended_projectiles\):.*?(?=if getattr\(self.ball, "_aura_explosion_cd")', content, re.DOTALL)
if matches:
    print(matches[0])
else:
    print("Not found")
