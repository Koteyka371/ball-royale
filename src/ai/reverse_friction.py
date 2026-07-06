from typing import Any, List
import math

class ReverseFrictionMode:
    def __init__(self):
        self.name = "Reverse Friction Mode"
        self.description = "Balls continuously accelerate as long as they are moving, turning the arena into a high-speed ping-pong match. Collisions deal extra damage based on speed."

    def setup(self, world: Any, balls: List[Any]) -> None:
        if not hasattr(world, "dead_balls"):
            world.dead_balls = []
        # Store initial damage/speed values
        for b in balls:
            if not hasattr(b, "base_damage"):
                b.base_damage = getattr(b, "damage", 10.0)
            if not hasattr(b, "base_speed"):
                b.base_speed = getattr(b, "speed", 100.0)

            # Make sure frictionless is allowed to build up
            b.is_frictionless = True

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:
        for b in balls:
            if getattr(b, "alive", False):
                vx = getattr(b, "vx", 0.0)
                vy = getattr(b, "vy", 0.0)

                # Continuously re-apply frictionless in case Action resets it
                b.is_frictionless = True

                # Check if moving
                velocity_sq = vx*vx + vy*vy
                if velocity_sq > 1.0: # small epsilon
                    # Accelerate in direction of movement
                    velocity = math.sqrt(velocity_sq)

                    # Add acceleration (e.g. 50 units per second squared)
                    acceleration = 50.0 * delta

                    # Normalize and add
                    b.vx += (vx / velocity) * acceleration
                    b.vy += (vy / velocity) * acceleration

                    current_speed = math.sqrt(b.vx**2 + b.vy**2)
                    base_speed = getattr(b, "base_speed", 100.0)

                    speed_ratio = current_speed / base_speed if base_speed > 0 else 1.0
                    if speed_ratio < 1.0:
                        speed_ratio = 1.0

                    # Cap speed ratio for damage scaling to avoid instakills
                    speed_ratio = min(speed_ratio, 5.0)

                    base_damage = getattr(b, "base_damage", 10.0)
                    b.damage = base_damage * speed_ratio
                else:
                    # Reset damage if not moving
                    b.damage = getattr(b, "base_damage", 10.0)
