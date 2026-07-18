import re

with open("src/ai/action.py", "r") as f:
    text = f.read()

replacement = """                    trap_id = 16000 + len(self.world.arena.hazards) + random.randint(0, 1000)
                    bh = Hazard(trap_id, self.ball.x, self.ball.y, 40.0, "black_hole", 20.0)
                    bh.vx = nx * 50.0
                    bh.vy = ny * 50.0
                    bh.duration = 5.0
                    bh.active = True
                    self.world.arena.hazards.append(bh)"""

text = text.replace("""                    trap_id = 16000 + len(self.world.arena.hazards) + random.randint(0, 1000)
                    bh = Hazard(trap_id, self.ball.x, self.ball.y, 40.0, "black_hole", 20.0)
                    bh.vx = nx * 50.0
                    bh.vy = ny * 50.0
                    bh.duration = 5.0
                    self.world.arena.hazards.append(bh)""", replacement)

with open("src/ai/action.py", "w") as f:
    f.write(text)
