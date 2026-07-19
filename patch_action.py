with open("src/ai/action.py", "r") as f:
    content = f.read()

# Replace the boundary reflection code in _clamp_position
search = """        # Reflect projectiles and entities with increased speed upon hitting the boundary
        if bounced_wall:
            self.ball.bumper_combo = 0
            import math as _math
            vx = getattr(self.ball, "vx", 0.0)
            vy = getattr(self.ball, "vy", 0.0)
            speed_sq = vx*vx + vy*vy

            # Determine which wall was hit based on coordinates
            margin = getattr(self.ball, "radius", 10.0) + 5.0
            hit_wall = None
            if self.ball.y <= margin:
                hit_wall = "top"
            elif self.ball.y >= getattr(self.world, "height", 1000) - margin:
                hit_wall = "bottom"
            elif self.ball.x <= margin:
                hit_wall = "left"
            elif self.ball.x >= getattr(self.world, "width", 1000) - margin:
                hit_wall = "right"

            wall_state = "normal"
            if hit_wall and hasattr(self.world, "arena") and hasattr(self.world.arena, "boundary_states"):
                wall_state = self.world.arena.boundary_states.get(hit_wall, "normal")

                speed_sq = vx*vx + vy*vy
                if speed_sq > 0:
                    speed = _math.sqrt(speed_sq)
                else:
                    speed = 0.0

                if speed > 800.0 and hasattr(self.world.arena, "boundary_health"):
                    health = self.world.arena.boundary_health.get(hit_wall, 2000.0)
                    health -= speed * 0.2
                    self.world.arena.boundary_health[hit_wall] = health

                    if health <= 0.0:
                        import random
                        new_state = random.choice(["abyss", "spikes"])
                        self.world.arena.boundary_states[hit_wall] = new_state
                        wall_state = new_state
                    elif health < 1000.0:
                        wall_state = "damaged_bouncy"

            if wall_state == "sticky":
"""

replace = search

# The logic is actually in action.py at line 8572.
# Wait, it's ALREADY there in action.py! Let me verify
