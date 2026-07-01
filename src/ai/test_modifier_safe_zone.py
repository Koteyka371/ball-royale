import pytest
from ai.game_modes import GAME_MODES

def test_modifier_safe_zone_registered():
    assert "modifier_zones_safe_zone" in GAME_MODES
    mode = GAME_MODES["modifier_zones_safe_zone"]
    assert mode.name == "Modifier Zones Safe Zone"

class MockArena:
    width = 1000
    height = 1000

class MockWorld:
    arena = MockArena()
    def add_event(self, type_name, data):
        pass

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alive = True
        self.ball_type = "test"
        self.team = "test"
        self.hp = 100
        self.max_hp = 100
        self.speed = 100
        self.damage = 10

def test_modifier_safe_zone_tick():
    mode = GAME_MODES["modifier_zones_safe_zone"]
    world = MockWorld()
    balls = [MockBall(500, 500)]
    mode.setup(world, balls)

    # Tick updates zones based on safe zone location
    mode.tick(world, balls, 1.0)

    assert len(mode.zones) == 4

    # Safe zone damage test
    out_of_zone_ball = MockBall(10, 10) # outside 500 radius safe zone (center 500,500)
    balls.append(out_of_zone_ball)
    mode.tick(world, balls, 1.0)
    assert out_of_zone_ball.hp < 100 # Took damage
