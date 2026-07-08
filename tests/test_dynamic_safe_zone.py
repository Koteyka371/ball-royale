import pytest
from ai.game_modes import GameMode, GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, x, y, alive=True, ball_type="basic", team="A"):
        self.x = x
        self.y = y
        self.alive = alive
        self.hp = 100.0
        self.max_hp = 100.0
        self.speed = 100.0
        self.damage = 10.0
        self.shield = 0.0
        self.ball_type = ball_type
        self.team = team

def test_dynamic_safe_zone_mode():
    mode = GAME_MODES["dynamic_safe_zone"]
    world = MockWorld()

    ball_center = MockBall(500, 500)
    ball_edge = MockBall(500, 600)
    ball_outside = MockBall(100, 100)

    balls = [ball_center, ball_edge, ball_outside]

    mode.setup(world, balls)
    mode.zone_x = 500.0
    mode.zone_y = 500.0
    mode.zone_radius = 200.0
    mode.buff_zone_radius = 75.0

    # Test buff logic
    mode.buff_type = "damage"
    mode.tick(world, balls, delta=1.0)

    # ball_center should be in the buff zone and get damage buff
    assert ball_center.damage > 10.0
    assert getattr(ball_center, "zone_modifier_damage", False) == True

    # ball_edge should be in the safe zone but outside buff zone
    assert ball_edge.damage == 10.0
    assert ball_edge.hp == 100.0

    # ball_outside should take damage
    assert ball_outside.hp < 100.0

    # Swap buff and tick again
    mode.buff_type = "heal"
    mode.tick(world, balls, delta=1.0)

    # ball_center should have damage restored
    assert ball_center.damage == 10.0
    assert not hasattr(ball_center, "zone_modifier_damage")
