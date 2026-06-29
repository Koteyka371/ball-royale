import sys

with open('src/ai/action.py', 'r') as f:
    content = f.read()

target = """        if hasattr(self.world, "balls"):
            for b in self.world.balls:
                if getattr(b, "is_decoy", False) and getattr(b, "alive", True) and b not in enemies:
                    if getattr(b, "ball_type", None) != self.ball.ball_type:
                        dx = getattr(b, "x", 0) - self.ball.x
                        dy = getattr(b, "y", 0) - self.ball.y
                        if dx*dx + dy*dy <= perception_radius*perception_radius:
                            enemies.append(b)


        if hasattr(self.world, "balls"):
            for b in self.world.balls:
                if getattr(b, "is_decoy", False) and getattr(b, "alive", True) and b not in enemies:
                    if getattr(b, "ball_type", None) != self.ball.ball_type:
                        dx = getattr(b, "x", 0) - self.ball.x
                        dy = getattr(b, "y", 0) - self.ball.y
                        if dx*dx + dy*dy <= perception_radius*perception_radius:
                            enemies.append(b)"""

replacement = """        if hasattr(self.world, "balls"):
            for b in self.world.balls:
                if getattr(b, "is_decoy", False) and getattr(b, "alive", True) and b not in enemies:
                    if getattr(b, "ball_type", None) != self.ball.ball_type:
                        dx = getattr(b, "x", 0) - self.ball.x
                        dy = getattr(b, "y", 0) - self.ball.y
                        if dx*dx + dy*dy <= perception_radius*perception_radius:
                            enemies.append(b)"""

content = content.replace(target, replacement)

with open('src/ai/action.py', 'w') as f:
    f.write(content)
