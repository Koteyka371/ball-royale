import pytest
from unittest.mock import MagicMock

from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 2000.0
        self.height = 2000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.add_event = MagicMock()

def test_volcanic_eruption_event():
    mode = GAME_MODES['volcanic_eruption_event']
    assert mode.name == "Volcanic Eruption Event"

    world = MockWorld()
    balls = []

    # Fast forward to eruption
    mode.eruption_timer = 0.01
    mode.tick(world, balls, delta=0.016)

    assert mode.is_erupting == True
    world.add_event.assert_called_with("volcanic_eruption_start", {"message": "The arena center is erupting!"})

    # Spawn a projectile
    mode.projectile_spawn_timer = 0.01
    mode.tick(world, balls, delta=0.016)

    assert len(world.arena.hazards) > 0
    projectile = world.arena.hazards[0]
    assert getattr(projectile, "kind") == "lava_projectile"

    # Fast forward projectile duration
    setattr(projectile, "duration", 0.01)
    mode.tick(world, balls, delta=0.016)

    # Should be replaced by lava
    assert len(world.arena.hazards) > 0
    has_lava = False
    for h in world.arena.hazards:
        if getattr(h, "kind") == "lava":
            has_lava = True
    assert has_lava
