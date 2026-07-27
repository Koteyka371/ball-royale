import sys
sys.path.append("src")
from ai.game_modes import GameMode, GAME_MODES
import math

class MockBall:
    def __init__(self):
        self.x = 200
        self.y = 200
        self.hp = 100
        self.alive = True
    def take_damage(self, amount):
        self.hp -= amount

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
        self.dead_balls = []

def test_shrapnel_mist_mode():
    mode = GAME_MODES["shrapnel_mist_mode"]
    world = MockWorld()
    ball = MockBall()
    mode.setup(world, [ball])

    # Tick slightly to spawn hazard but not process it too long
    mode.tick(world, [ball], 5.1)
    # Filter to main hazards only since it might have processed split in same tick
    main_hazards = [h for h in world.arena.hazards if h.split_count == 0]

    if len(main_hazards) == 0:
        # Check if they already split
        assert len(world.arena.hazards) >= 3
    else:
        assert len(main_hazards) == 1
        assert main_hazards[0].kind == "shrapnel_mist_hazard"

        # Fast forward to split
        main_hazards[0].duration = -1.0
        mode.tick(world, [ball], 0.1)

    split_hazards = [h for h in world.arena.hazards if h.split_count == 1]
    assert len(split_hazards) >= 3
    for h in split_hazards:
        assert h.kind == "shrapnel_mist_hazard"

    # Fast forward to mist cloud
    for h in world.arena.hazards:
        h.duration = -1.0
        h.split_count = 3
    mode.tick(world, [ball], 0.1)

    mist_clouds = [h for h in world.arena.hazards if getattr(h, "kind", "") == "shrapnel_mist_cloud"]
    assert len(mist_clouds) > 0
    for h in mist_clouds:
        h.x = 200
        h.y = 200

    # Mist cloud damage
    mode.tick(world, [ball], 1.0)
    assert ball.hp < 100
