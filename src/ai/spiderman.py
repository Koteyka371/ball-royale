from typing import Any, List
from ai.game_modes import GameMode

class SpidermanMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Spiderman Mode"
        self.description = "All balls start with a grapple hook and zero friction, relying entirely on grapple points and walls to navigate the arena."

    def setup(self, world: Any, balls: List[Any]) -> None:
        super().setup(world, balls)
        if hasattr(world, "arena") and world.arena:
            world.arena.base_friction = 0.0

        for ball in balls:
            if not hasattr(ball, "inventory"):
                ball.inventory = []
            if "grapple_hook" not in ball.inventory:
                ball.inventory.append("grapple_hook")

            ball.is_frictionless = True
            ball.friction_multiplier = 0.0

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:
        super().tick(world, balls, delta)
        for ball in balls:
            if not getattr(ball, "alive", False):
                continue

            ball.is_frictionless = True
            if not hasattr(ball, "inventory"):
                ball.inventory = []
            if "grapple_hook" not in ball.inventory:
                ball.inventory.append("grapple_hook")
