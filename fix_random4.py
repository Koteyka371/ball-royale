with open("src/ai/action.py", "r") as f:
    content = f.read()

# mypy doesn't like importing inside functions if it masks global imports, but it's fine if we just import locally when needed.
import re
content = re.sub(r'decoy\.id = getattr\(self\.world, "next_id", random\.randint\(10000, 99999\)\)',
                 r'import random\n                    decoy.id = getattr(self.world, "next_id", random.randint(10000, 99999))', content)
content = re.sub(r'angle = random\.uniform\(0, 2 \* math\.pi\)',
                 r'import random\n                    angle = random.uniform(0, 2 * math.pi)', content)
content = re.sub(r'trap_id = len\(self\.world\.arena\.hazards\) \+ random\.randint\(1000, 9999\)',
                 r'import random\n                    trap_id = len(self.world.arena.hazards) + random.randint(1000, 9999)', content)

with open("src/ai/action.py", "w") as f:
    f.write(content)
