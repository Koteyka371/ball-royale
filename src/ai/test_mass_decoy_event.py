import pytest
from ai.game_modes import MassDecoyEventMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self, balls=None):
        self.balls = balls or []
        self.arena = MockArena()
        self.events = []
        self.next_id = 999

    def add_event(self, name, data):
        self.events.append((name, data))

class MockBall:
    def __init__(self, id, alive=True, is_decoy=False):
        self.id = id
        self.alive = alive
        self.is_decoy = is_decoy
        self.x = 100
        self.y = 100
        self.speed = 10.0
        self.vx = 5.0
        self.vy = 5.0
        self.damage = 20

def test_mass_decoy_event_triggers():
    mode = MassDecoyEventMode()
    b1 = MockBall(1)
    b2 = MockBall(2, alive=False) # Dead ball
    b3 = MockBall(3, is_decoy=True) # Already a decoy
    world = MockWorld([b1, b2, b3])

    # Fast forward timer
    mode.tick(world, world.balls, delta=21.0)

    assert len(world.balls) == 4

    new_decoy = world.balls[-1]
    assert new_decoy.id == 999
    assert new_decoy.is_decoy == True
    assert new_decoy.decoy_timer == 10.0
    assert new_decoy.owner_id == 1
    assert new_decoy.speed == 0.0
    assert new_decoy.vx == 0.0
    assert new_decoy.vy == 0.0
    assert new_decoy.damage == 0
    assert 50 <= new_decoy.x <= 950
    assert 50 <= new_decoy.y <= 950

    assert len(world.events) == 1
    assert world.events[0][0] == "mass_decoy_spawn"
    assert world.events[0][1]["count"] == 1
