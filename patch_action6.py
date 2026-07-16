import re

with open("src/ai/action.py", "r") as f:
    content = f.read()

# Fix the stun clearing logic in action.py
search_str = """    def execute(self, strategy: str, delta: float) -> None:
        if getattr(self.ball, "wall_stick_timer", 0.0) > 0.0:
            self.ball.wall_stick_timer -= delta
            if self.ball.wall_stick_timer <= 0.0:
                self.ball.is_stunned = False"""

replace_str = """    def execute(self, strategy: str, delta: float) -> None:
        if getattr(self.ball, "wall_stick_timer", 0.0) > 0.0:
            self.ball.wall_stick_timer -= delta
            if self.ball.wall_stick_timer <= 0.0:
                if getattr(self.ball, "stun_timer", 0.0) <= 0.0:
                    self.ball.is_stunned = False"""

if search_str in content:
    content = content.replace(search_str, replace_str)
    print("Action.py patch 6 applied!")
else:
    print("Search string not found in action.py")

with open("src/ai/action.py", "w") as f:
    f.write(content)
