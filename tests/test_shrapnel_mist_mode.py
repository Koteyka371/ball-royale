import pytest
import math
from ai.game_modes import ShrapnelMistMode

class MockWorld:
    def __init__(self):
        self.arena = self.MockArena()

    class MockArena:
        def __init__(self):
            self.hazards = []

class MockBall:
    def __init__(self, x=0.0, y=0.0):
        self.id = id(self)
        self.x = x
        self.y = y
        self.hp = 100.0
        self.alive = True
        self.is_blinded = False
        self.blindness_timer = 0.0

def test_shrapnel_mist_mode():
    mode = ShrapnelMistMode()
    world = MockWorld()
    ball1 = MockBall(150, 150)
    ball2 = MockBall(500, 500)
    balls = [ball1, ball2]

    mode.setup(world, balls)

    # Initial tick, spawns hazard
    mode.tick(world, balls, delta=0.016)
    assert len(world.arena.hazards) == 1
    hazard = world.arena.hazards[0]
    assert hazard.kind == "shrapnel_mist_hazard"

    # Fast forward hazard duration
    hazard.duration = 0.01

    # Next tick should split
    mode.tick(world, balls, delta=0.016)
    # The original hazard is removed, 3 new pieces are added
    assert len(world.arena.hazards) == 3
    for h in world.arena.hazards:
        assert h.kind == "shrapnel_mist_hazard"
        assert h.split_count == 1

    # Split again until max (3 times total)
    world.arena.hazards[0].duration = 0.01
    mode.tick(world, balls, delta=0.016)

    # One split into 3, other 2 are untouched
    assert len(world.arena.hazards) == 5

    # Fast forward all to hit max split (split_count == 3)
    for h in world.arena.hazards:
        h.split_count = 3
        h.duration = 0.01

    mode.tick(world, balls, delta=0.016)

    # Now they should turn into mist clouds
    assert len(world.arena.hazards) == 5
    for h in world.arena.hazards:
        assert h.kind == "shrapnel_mist_cloud"

    # Move ball1 to the center of a mist cloud
    cloud = world.arena.hazards[0]
    ball1.x = cloud.x
    ball1.y = cloud.y

    mode.tick(world, balls, delta=0.016)

    assert ball1.is_blinded == True
    assert ball1.blindness_timer > 0
    assert ball1.hp < 100.0 # Took damage

    # Ball 2 is far away and should not be affected
    # Because hazards spawn at random positions, ball 2 might have randomly spawned inside one of the other 4 clouds.
    # To test it correctly, move it very far away.
    ball2.x = 9000
    ball2.y = 9000
    ball2.is_blinded = False
    ball2.blindness_timer = 0.0
    mode.tick(world, balls, delta=0.016)

    assert ball2.is_blinded == False
    assert ball2.blindness_timer == 0.0
    assert ball2.hp == 100.0
