import pytest
from ai.game_modes import OrbitingChaosOrbsMode

class MockBall:
    def __init__(self, id, x, y, alive=True, ball_type="player"):
        self.id = id
        self.x = x
        self.y = y
        self.alive = alive
        self.ball_type = ball_type
        self.radius = 10.0
        self.hp = 100.0

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
    def add_event(self, type, data):
        self.events.append({"type": type, "data": data})

def test_orbiting_chaos_orbs_mode():
    mode = OrbitingChaosOrbsMode()
    world = MockWorld()
    b1 = MockBall(1, 100.0, 100.0)
    b2 = MockBall(2, 200.0, 200.0)
    balls = [b1, b2]

    mode.setup(world, balls)
    assert len(mode.orbs) == 0

    mode.spawn_timer = 0.0 # Force spawn
    mode.tick(world, balls, 0.016)

    assert len(mode.orbs) == 2
    assert len(world.arena.hazards) == 2

    orb = mode.orbs[0]
    assert orb.active == True
    assert orb.kind == "chaos_orb"

    # Move b2 to touch b1's orb
    b2.x = orb.x
    b2.y = orb.y

    mode.tick(world, balls, 0.016)

    # b2 should take damage and orb should become inactive
    assert b2.hp == 75.0
    assert orb.active == False

    # Next tick, orb should be removed
    mode.tick(world, balls, 0.016)
    assert orb not in mode.orbs
    assert orb not in world.arena.hazards
