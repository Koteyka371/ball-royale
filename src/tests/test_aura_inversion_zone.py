import sys
sys.path.append('src')

import pytest
from ai.game_modes import AuraInversionZoneMode

class MockWorld:
    def __init__(self):
        class MockArena:
            def __init__(self):
                self.width = 1000.0
                self.height = 1000.0
                self.hazards = []
        self.arena = MockArena()
        self.balls = []

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.hp = 100.0
        self.alive = True
        self.aura_inversion_timer = 0.0
        self.aura_booster_timer = 0.0
        self.vampiric_aura_timer = 0.0

def test_aura_inversion_zone():
    mode = AuraInversionZoneMode()
    world = MockWorld()
    b_in_nobuff = MockBall(1, 500, 500)
    b_in_buff = MockBall(2, 500, 500)
    b_in_buff.aura_booster_timer = 10.0

    b_out = MockBall(3, 100, 100)

    world.balls = [b_in_nobuff, b_in_buff, b_out]

    mode.setup(world, world.balls)

    # Check if hazard is created
    assert len(world.arena.hazards) == 1
    assert world.arena.hazards[0].kind == "aura_inversion_zone"

    # Run a tick
    mode.tick(world, world.balls, delta=0.1)

    # Ball inside without buff should have inversion timer, but take no damage
    assert b_in_nobuff.aura_inversion_timer > 0
    assert b_in_nobuff.hp == 100.0

    # Ball inside with buff should take damage
    assert b_in_buff.aura_inversion_timer > 0
    assert b_in_buff.hp < 100.0

    # Ball outside should not
    assert b_out.aura_inversion_timer == 0.0
    assert b_out.hp == 100.0
