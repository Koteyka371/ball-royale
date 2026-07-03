with open("src/ai/action.py", "r") as f:
    content = f.read()

target = """            if getattr(self.world.arena, "is_raining", False) and not ignores_mud and not is_wind_riding:
                # Slippery: apply momentum (friction slide)
                self.ball.x += getattr(self.ball, "vx", 0.0) * delta * 0.5
                self.ball.y += getattr(self.ball, "vy", 0.0) * delta * 0.5"""

replacement = """            if getattr(self.world.arena, "is_raining", False) and not ignores_mud and not is_wind_riding:
                # Slippery: apply momentum (friction slide)
                self.ball.x += getattr(self.ball, "vx", 0.0) * delta * 0.5
                self.ball.y += getattr(self.ball, "vy", 0.0) * delta * 0.5

                # Mud slowdown on dirt/sand
                if getattr(self.world.arena, "terrain_type", "grass") in ["dirt", "sand"]:
                    ball_type = getattr(self.ball, "ball_type", getattr(self.ball, "BALL_TYPE", "")).lower()
                    is_water_or_swamp = ball_type in ["elementalist", "healer", "trickster"] or "swamp" in ball_type or "water" in ball_type
                    if not is_water_or_swamp:
                        self.ball.speed = getattr(self.ball, "base_speed", 100.0) * 0.5"""

content = content.replace(target, replacement)
with open("src/ai/action.py", "w") as f:
    f.write(content)
