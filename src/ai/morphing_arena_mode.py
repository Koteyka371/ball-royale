from typing import Any, List
from ai.game_modes import GameMode

class MorphingArenaMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Morphing Arena"
        self.description = "The arena smoothly morphs between different shapes every 60 seconds."

    def setup(self, world: Any, balls: List[Any]) -> None:
        super().setup(world, balls)

        # Override the arena with MorphingArena
        from arena.morphing_arena import MorphingArena
        old_width = getattr(world.arena, 'width', 2000.0)
        world.arena = MorphingArena(arena_size=old_width)
