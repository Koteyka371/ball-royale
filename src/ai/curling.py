from typing import Any, List, Optional
import math

try:
    from .game_modes import GameMode
except ImportError:
    class GameMode:
        def __init__(self):
            self.name = "Unknown"
            self.description = "Base game mode"
        def setup(self, world: Any, balls: List[Any]) -> None:
            pass
        def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:
            pass
        def check_winner(self, world: Any, balls: List[Any]) -> Optional[str]:
            return None

class CurlingMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Curling"
        self.description = "Balls must land as close to a target as possible with ultra-low friction."
        self.timer = 15.0
        self.target_x = 0.0
        self.target_y = 0.0

    def setup(self, world: Any, balls: List[Any]) -> None:
        if hasattr(world, "arena"):
            world.arena.base_friction = 0.05
            self.target_x = getattr(world.arena, "width", 1000) / 2.0
            self.target_y = getattr(world.arena, "height", 1000) / 2.0

            # Add target marker
            class TargetMarker:
                def __init__(self, x, y):
                    self.x = x
                    self.y = y
                    self.radius = 20.0
                    self.kind = "target_marker"
                    self.active = True

            if not hasattr(world.arena, "hazards"):
                world.arena.hazards = []
            world.arena.hazards.append(TargetMarker(self.target_x, self.target_y))
        else:
            self.target_x = 500.0
            self.target_y = 500.0

        for b in balls:
            b.friction_multiplier = 0.05
            # Reset velocities to prevent initial chaos if needed
            b.vx = 0.0
            b.vy = 0.0

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:
        self.timer -= delta
        for b in balls:
            if getattr(b, "alive", False):
                b.friction_multiplier = 0.05
                # Curling usually has sliding, so let's set is_frictionless for action.py to not instantly stop them
                b.is_frictionless = True

    def check_winner(self, world: Any, balls: List[Any]) -> Optional[str]:
        if self.timer > 0:
            return None

        closest_dist = float('inf')
        winner_team = None

        for b in balls:
            if getattr(b, "alive", False) and getattr(b, "ball_type", "") != "spectator":
                dist = math.hypot(getattr(b, "x", 0.0) - self.target_x, getattr(b, "y", 0.0) - self.target_y)
                if dist < closest_dist:
                    closest_dist = dist
                    winner_team = getattr(b, "team", None)

        return winner_team
