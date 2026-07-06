from typing import Any, List
try:
    from .game_modes import GameMode
except ImportError:
    # Fallback for testing directly if needed
    class GameMode:
        def setup(self, world: Any, balls: List[Any]) -> None:
            pass
        def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:
            pass

class ReverseFrictionMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Reverse Friction"
        self.description = "Balls continuously accelerate as long as they are moving, turning the arena into a high-speed ping-pong match. Collisions deal extra damage based on speed."
        self.acceleration_rate = 0.5 # 50% increase per second

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:
        super().tick(world, balls, delta)

        for b in balls:
            if getattr(b, "alive", False) and getattr(b, "ball_type", "") != "spectator":
                # Accelerate if moving
                vx = getattr(b, "vx", 0.0)
                vy = getattr(b, "vy", 0.0)

                # Check if it's moving at least a tiny bit
                if abs(vx) > 0.1 or abs(vy) > 0.1:
                    b.vx = vx * (1.0 + self.acceleration_rate * delta)
                    b.vy = vy * (1.0 + self.acceleration_rate * delta)
