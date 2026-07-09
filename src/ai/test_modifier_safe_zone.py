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

    assert len(mode.zones) == 5

    # Safe zone damage test
    out_of_zone_ball = MockBall(10, 10) # outside 500 radius safe zone (center 500,500)
    balls.append(out_of_zone_ball)
    mode.tick(world, balls, 1.0)
    assert out_of_zone_ball.hp < 100 # Took damage

def test_modifier_safe_zone_shrink():
    mode = GAME_MODES["modifier_safe_zone"]
    world = MockWorld()
    b1 = MockBall(500, 500)
    balls = [b1]

    mode.setup(world, balls)

    assert mode.zone_radius == 500.0

    # Tick to shrink
    mode.tick(world, balls, delta=1.0)

    assert mode.zone_radius < 500.0
    assert mode.zone_radius == 500.0 - (mode.shrink_rate * 1.0 * 1.0) # 1 player inside

def test_modifier_safe_zone_outside_damage():
    mode = GAME_MODES["modifier_safe_zone"]
    world = MockWorld()
    # Put ball outside the zone
    b1 = MockBall(10, 10)
    balls = [b1]

    mode.setup(world, balls)

    initial_hp = b1.hp
    # Tick multiple times
    mode.tick(world, balls, delta=1.0)

    assert b1.hp < initial_hp
    assert b1.hp == initial_hp - (mode.outside_damage_per_second * 1.0)

def test_modifier_safe_zone_applies_modifier():
    mode = GAME_MODES["modifier_safe_zone"]
    world = MockWorld()
    # Put ball inside the zone
    b1 = MockBall(500, 500)
    balls = [b1]

    mode.setup(world, balls)

    # Fast forward modifier timer
    mode.modifier_timer = 0.1
    mode.tick(world, balls, delta=0.2)

    assert mode.active_modifier is not None

    # Check if modified
    # We can't know which random modifier was chosen, but we can verify it changed stats or healed
    if mode.active_modifier == "speed_boost":
        assert b1.speed > 100.0
    elif mode.active_modifier == "slow":
        assert b1.speed < 100.0
    elif mode.active_modifier == "damage_boost":
        assert b1.damage == 15.0 or b1.damage > 10.0
