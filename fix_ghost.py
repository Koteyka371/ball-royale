with open("src/ai/action.py", "r") as f:
    content = f.read()

# Remove the bad replacement from _get_enemies
bad_block = """    def _get_enemies(self) -> list:
        if getattr(self.ball, "ghost_mode_timer", 0.0) > 0.0:
            self.ball.ghost_mode_timer -= delta
            if self.ball.ghost_mode_timer <= 0.0:
                self.ball.ghost_mode_timer = 0.0
                if getattr(self.ball, "ghost_mode_active", False):
                    self.ball.intangible = False
                    self.ball.ghost_mode_active = False"""
good_block = """    def _get_enemies(self) -> list:"""
content = content.replace(bad_block, good_block)

with open("src/ai/action.py", "w") as f:
    f.write(content)
