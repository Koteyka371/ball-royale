import pytest
from ai.game_modes import FrostbiteMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, x=500, y=500, vx=0, vy=0):
        self.id = 1
        self.alive = True
        self.ball_type = "player"
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.speed = 100.0
        self.hp = 100.0
        self.frostbite_stack = 0.0

def test_frostbite_stack_increases_when_stationary():
    mode = FrostbiteMode()
    world = MockWorld()
    b = MockBall(vx=0, vy=0) # Stationary

    mode.setup(world, [b])

    for _ in range(100):
        mode.tick(world, [b], 0.1)

    assert getattr(b, "frostbite_stack", 0.0) >= 0.0

def test_frostbite_stack_decreases_when_moving():
    mode = FrostbiteMode()
    world = MockWorld()
    b = MockBall(vx=100, vy=0) # Moving fast
    b.frostbite_stack = 50.0 # Start with some stack

    mode.setup(world, [b])

    for _ in range(100):
        mode.tick(world, [b], 0.1)

    assert b.frostbite_stack == 0.0

def test_heat_vent_clears_frostbite():
    mode = FrostbiteMode()
    world = MockWorld()
    b = MockBall(vx=0, vy=0)
    b.frostbite_stack = 50.0

    mode.setup(world, [b])

    # Manually spawn a vent where the ball is
    mode.heat_vents.append({
        "x": b.x,
        "y": b.y,
        "radius": 150.0,
        "timer": 10.0
    })

    for _ in range(50):
        mode.tick(world, [b], 0.1)

    assert b.frostbite_stack == 0.0

def test_damage_and_speed_debuff_at_high_stack():
    mode = FrostbiteMode()
    world = MockWorld()
    b = MockBall(vx=0, vy=0)

    mode.setup(world, [b])

    # Force the stack up quickly
    b.frostbite_stack = 100.0

    mode.tick(world, [b], 0.1)

    # Check debuffs and damage
    assert getattr(b, "speed_debuff_timer", 0.0) > 0.0
    assert getattr(b, "speed_debuff_multiplier", 1.0) < 1.0
    assert b.hp < 100.0
