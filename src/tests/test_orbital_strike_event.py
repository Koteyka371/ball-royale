import pytest
from ai.game_modes import OrbitalStrikeEventMode

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.radius = 10.0
        self.hp = 1000.0
        self.alive = True
        self.ball_type = "player"

def test_orbital_strike_event():
    mode = OrbitalStrikeEventMode()
    world = MockWorld()

    # Target in center
    b1 = MockBall(1, 500, 500)
    # Target far away
    b2 = MockBall(2, 100, 100)

    balls = [b1, b2]

    mode.setup(world, balls)

    # Tick to spawn a strike
    # Spawn timer is initially 5.0, so after 5 seconds it spawns
    mode.tick(world, balls, delta=5.0)

    assert len(mode.strikes) == 1
    strike = mode.strikes[0]
    assert strike["state"] == "warning"
    assert strike["timer"] == 3.0

    # Manually move strike to b1
    strike["x"] = b1.x
    strike["y"] = b1.y

    # Tick slightly less than warning duration
    mode.tick(world, balls, delta=2.9)
    assert strike["state"] == "warning"

    # Tick past warning duration to fire
    mode.tick(world, balls, delta=0.2)
    assert strike["state"] == "firing"
    assert strike["timer"] > 0

    # b1 should have taken damage
    assert b1.hp == 500.0 # 1000 - 500
    # b2 should not have taken damage
    assert b2.hp == 1000.0

    # Tick past firing duration
    mode.tick(world, balls, delta=1.5)
    assert len(mode.strikes) == 0
