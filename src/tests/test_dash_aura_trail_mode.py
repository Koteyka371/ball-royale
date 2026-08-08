import pytest
from ai.game_modes import DashAuraTrailMode

class MockBall:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y
        self.alive = True
        self.radius = 15.0
        self.speed = 250.0

class MockWorld:
    def __init__(self):
        self.time = 0.0

def test_setup_assigns_aura_color():
    mode = DashAuraTrailMode()
    world = MockWorld()
    ball = MockBall()
    mode.setup(world, [ball])

    assert hasattr(ball, "cosmetic_aura_color")
    assert ball.cosmetic_aura_color in [(1.0, 0.0, 0.0, 1.0), (0.0, 1.0, 0.0, 1.0), (0.0, 0.0, 1.0, 1.0), (1.0, 1.0, 0.0, 1.0)]
    assert hasattr(world, "aura_trails")
    assert world.aura_trails == []

def test_dashing_spawns_trail():
    mode = DashAuraTrailMode()
    world = MockWorld()
    ball = MockBall(0.0, 0.0)
    mode.setup(world, [ball])

    # Tick without dashing
    mode.tick(world, [ball], 0.1)
    assert len(world.aura_trails) == 0

    # Tick with dashing
    ball.is_dashing = True
    world.time += 0.2
    mode.tick(world, [ball], 0.1)
    assert len(world.aura_trails) == 1

    trail = world.aura_trails[0]
    assert trail.x == ball.x
    assert trail.y == ball.y
    assert trail.color == ball.cosmetic_aura_color
    assert trail.source_id == id(ball)

def test_stepping_on_same_color_trail():
    mode = DashAuraTrailMode()
    world = MockWorld()

    b1 = MockBall(0.0, 0.0)
    b2 = MockBall(10.0, 10.0)

    mode.setup(world, [b1, b2])

    # Force same color
    b1.cosmetic_aura_color = (1.0, 0.0, 0.0, 1.0)
    b2.cosmetic_aura_color = (1.0, 0.0, 0.0, 1.0)

    # Spawn a trail from b1
    b1.is_dashing = True
    world.time += 0.2
    mode.tick(world, [b1, b2], 0.1)
    assert len(world.aura_trails) == 1

    b1.is_dashing = False

    # Move b2 onto b1's trail
    world.time += 1.0 # Debounce
    b2.x = 0.0
    b2.y = 0.0
    mode.tick(world, [b1, b2], 0.1)

    # b2 should get a speed boost
    assert getattr(b2, "aura_speed_buff_timer", 0.0) == 2.0
    mode.tick(world, [b1, b2], 0.1)
    assert b2.speed > 400.0

def test_stepping_on_different_color_trail():
    mode = DashAuraTrailMode()
    world = MockWorld()

    b1 = MockBall(0.0, 0.0)
    b2 = MockBall(10.0, 10.0)

    mode.setup(world, [b1, b2])

    # Force different colors
    b1.cosmetic_aura_color = (1.0, 0.0, 0.0, 1.0)
    b2.cosmetic_aura_color = (0.0, 1.0, 0.0, 1.0)

    # Spawn a trail from b1
    b1.is_dashing = True
    world.time += 0.2
    mode.tick(world, [b1, b2], 0.1)
    assert len(world.aura_trails) == 1

    b1.is_dashing = False

    # Move b2 onto b1's trail
    world.time += 1.0 # Debounce
    b2.x = 0.0
    b2.y = 0.0
    mode.tick(world, [b1, b2], 0.1)

    # b2 should be stunned
    assert getattr(b2, "stun_timer", 0.0) == 1.0
    assert getattr(b2, "aura_speed_buff_timer", 0.0) == 0.0
