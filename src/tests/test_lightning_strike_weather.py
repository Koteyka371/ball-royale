import pytest
from ai.game_modes import GameMode

class MockArena:
    def __init__(self, is_raining=False, weather=""):
        self.is_raining = is_raining
        self.weather = weather

class MockWorld:
    def __init__(self, arena=None):
        self.arena = arena
        self.events = []
        self.dead_balls = []

    def add_event(self, name, data):
        self.events.append((name, data))

class MockBall:
    def __init__(self, x=0.0, y=0.0, hp=100.0, alive=True):
        self.x = x
        self.y = y
        self.hp = hp
        self.alive = alive
        self.speed = 100.0
        self.base_speed = 100.0
        self.cooldown_multiplier = 1.0

def test_lightning_strike_highest_cluster():
    mode = GameMode()
    mode.weather = "thunderstorm"
    world = MockWorld(arena=MockArena())

    # cluster 1 (2 balls)
    b1 = MockBall(0.0, 0.0)
    b2 = MockBall(10.0, 10.0)

    # cluster 2 (3 balls) - should be targeted
    b3 = MockBall(500.0, 500.0)
    b4 = MockBall(510.0, 510.0)
    b5 = MockBall(505.0, 495.0)

    # far away ball
    b6 = MockBall(1000.0, 1000.0)

    balls = [b1, b2, b3, b4, b5, b6]

    world.lightning_strike_timer = 14.9
    mode.tick(world, balls, delta=0.2)

    assert world.lightning_strike_timer < 1.0 # reset
    assert len(world.events) == 1
    ev_name, ev_data = world.events[0]
    assert ev_name == "lightning_strike"
    assert abs(ev_data["x"] - 500.0) < 50.0

    # cluster 2 damaged
    assert b3.hp == 50.0
    assert b4.hp == 50.0
    assert b5.hp == 50.0

    # cluster 1 unaffected
    assert b1.hp == 100.0
    assert b2.hp == 100.0
    assert b6.hp == 100.0

    # overcharged buffs on cluster 2
    assert getattr(b3, "is_overcharged", False)
    assert b3.speed == 200.0
    assert b3.cooldown_multiplier == 0.5

    # check overcharge decays
    mode.tick(world, balls, delta=6.0)
    assert not getattr(b3, "is_overcharged", False)
    assert b3.speed == 100.0
    assert b3.cooldown_multiplier == 1.0
