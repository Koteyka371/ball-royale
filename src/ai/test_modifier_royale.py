import pytest
from src.ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, ball_id, team=0):
        self.id = ball_id
        self.team = team
        self.alive = True
        self.x = 0.0
        self.y = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.base_speed = 100.0
        self.speed = 100.0
        self.base_damage = 50.0
        self.damage = 50.0
        self.frictionless_modifier_applied = False
        self.ball_type = "player"

class MockWorld:
    def __init__(self):
        self.balls = []
        self.zero_gravity_active = False
        self.events = []

    def add_event(self, type_, data):
        self.events.append((type_, data))

def test_modifier_royale_registered():
    assert "modifier_royale" in GAME_MODES
    mode = GAME_MODES["modifier_royale"]
    assert mode.name == "Modifier Royale"
    assert mode.modifier_timer == 0.0
    assert mode.active_modifier == "none"

def test_modifier_royale_timer():
    mode = GAME_MODES["modifier_royale"]
    mode.modifier_timer = 59.9
    world = MockWorld()

    # Needs a random seed/instance to be consistent, but we can just check if it triggers
    mode.apply_dynamic_traits(world, [], 0.2)
    assert mode.modifier_timer < 1.0
    assert mode.active_modifier in ["double_speed", "half_speed", "double_damage", "zero_gravity", "none"]

def test_modifier_royale_double_speed():
    mode = GAME_MODES["modifier_royale"]
    mode.active_modifier = "double_speed"
    world = MockWorld()
    b = MockBall(1)

    mode.apply_dynamic_traits(world, [b], 0.1)

    assert b.speed == b.base_speed * 2.0
    assert b.damage == b.base_damage
    assert not b.frictionless_modifier_applied

def test_modifier_royale_half_speed():
    mode = GAME_MODES["modifier_royale"]
    mode.active_modifier = "half_speed"
    world = MockWorld()
    b = MockBall(1)

    mode.apply_dynamic_traits(world, [b], 0.1)

    assert b.speed == b.base_speed * 0.5

def test_modifier_royale_double_damage():
    mode = GAME_MODES["modifier_royale"]
    mode.active_modifier = "double_damage"
    world = MockWorld()
    b = MockBall(1)

    mode.apply_dynamic_traits(world, [b], 0.1)

    assert b.damage == b.base_damage * 2.0
    assert b.speed == b.base_speed

def test_modifier_royale_zero_gravity():
    mode = GAME_MODES["modifier_royale"]
    mode.active_modifier = "zero_gravity"
    world = MockWorld()
    b = MockBall(1)

    mode.apply_dynamic_traits(world, [b], 0.1)

    assert world.zero_gravity_active == True
    assert b.frictionless_modifier_applied == True

def test_modifier_royale_none():
    mode = GAME_MODES["modifier_royale"]

    # First set it to something else
    mode.active_modifier = "zero_gravity"
    world = MockWorld()
    b = MockBall(1)
    mode.apply_dynamic_traits(world, [b], 0.1)
    assert b.frictionless_modifier_applied == True

    # Now set to none and check reset
    mode.active_modifier = "none"
    mode.apply_dynamic_traits(world, [b], 0.1)

    assert world.zero_gravity_active == False
    assert b.frictionless_modifier_applied == False
    assert b.speed == b.base_speed
    assert b.damage == b.base_damage
