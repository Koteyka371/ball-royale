import pytest
import math
from ai.game_modes import GameMode

class MockArena:
    def __init__(self, hazards=None):
        self.hazards = hazards or []

class MockWorld:
    def __init__(self, arena=None):
        self.arena = arena or MockArena()

class MockHazard:
    def __init__(self, weather="", kind="", x=0.0, y=0.0):
        self.weather = weather
        self.kind = kind
        self.x = x
        self.y = y

class MockBall:
    def __init__(self, x=0.0, y=0.0, vx=0.0, vy=0.0, traits=None, speed=100.0, alive=True, ball_type="basic", team="A"):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.traits = traits or []
        self.speed = speed
        self.base_speed = speed
        self.alive = alive
        self.ball_type = ball_type
        self.team = team
        self.id = id(self)

def test_storm_chaser_trait_towards_hazard():
    mode = GameMode()
    h1 = MockHazard(weather="blizzard", x=100, y=100)
    world = MockWorld(arena=MockArena(hazards=[h1]))

    # Moving directly towards hazard (100, 100) from (0,0) -> velocity vector (10, 10)
    b1 = MockBall(x=0, y=0, vx=10, vy=10, traits=["storm_chaser"], speed=100)
    # Moving away
    b2 = MockBall(x=0, y=0, vx=-10, vy=-10, traits=["storm_chaser"], speed=100)
    # No trait
    b3 = MockBall(x=0, y=0, vx=10, vy=10, traits=[], speed=100)

    mode.apply_dynamic_traits(world, [b1, b2, b3], 0.1)

    # b1 should have 1.5x speed
    assert b1.speed == 150.0
    # b2 should have normal speed
    assert b2.speed == 100.0
    # b3 should have normal speed
    assert b3.speed == 100.0

def test_storm_chaser_trait_towards_tornado():
    mode = GameMode()
    h1 = MockHazard(kind="tornado", x=100, y=100)
    world = MockWorld(arena=MockArena(hazards=[h1]))

    b1 = MockBall(x=0, y=0, vx=10, vy=10, traits=["storm_chaser"], speed=100)

    mode.apply_dynamic_traits(world, [b1], 0.1)
    assert b1.speed == 150.0

if __name__ == "__main__":
    pytest.main(["-v", "test_storm_chaser.py"])
