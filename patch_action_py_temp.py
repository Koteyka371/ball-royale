import re

with open("src/ai/action.py", "r") as f:
    content = f.read()

exec_start = content.find('    def execute(self, strategy: str, delta: float) -> None:')
assert exec_start != -1

timer_logic_py = """        if hasattr(self.ball, "gravity_boots_timer"):
            if self.ball.gravity_boots_timer > 0.0:
                self.ball.gravity_boots_timer = max(0.0, self.ball.gravity_boots_timer - delta)
                if self.ball.gravity_boots_timer <= 0.0:
                    if hasattr(self.ball, "inventory") and "gravity_boots" in self.ball.inventory:
                        self.ball.inventory.remove("gravity_boots")
"""

nl = content.find('\n', exec_start)
content = content[:nl+1] + timer_logic_py + content[nl+1:]

old_coll_py = """                elif getattr(nearest, "kind", None) == "gravity_boots":
                    if not hasattr(self.ball, "inventory"):
                        self.ball.inventory = []
                    self.ball.inventory.append("gravity_boots")"""

new_coll_py = """                elif getattr(nearest, "kind", None) == "gravity_boots":
                    if not hasattr(self.ball, "inventory"):
                        self.ball.inventory = []
                    if "gravity_boots" not in self.ball.inventory:
                        self.ball.inventory.append("gravity_boots")
                    self.ball.gravity_boots_timer = 15.0"""

content = content.replace(old_coll_py, new_coll_py)

with open("src/ai/action.py", "w") as f:
    f.write(content)

print("patched action.py temp")
