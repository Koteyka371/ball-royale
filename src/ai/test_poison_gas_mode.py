import pytest
from ai.game_modes import GameMode, GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
        self.dead_balls = []

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

def test_poison_gas_mode():
    mode = GAME_MODES["poison_gas"]
    world = MockWorld()

    ball_center = MockBall(500, 500)
    ball_edge = MockBall(500, 600)
    ball_outside = MockBall(100, 100)

    balls = [ball_center, ball_edge, ball_outside]

    mode.setup(world, balls)
    mode.zone_x = 500.0
    mode.zone_y = 500.0
    mode.zone_radius = 200.0
    mode.outside_damage_per_second = 50.0

    mode.tick(world, balls, delta=1.0)

    # ball_center should be in the safe zone and take no damage
    assert ball_center.hp == 100.0
    assert ball_center.alive == True

    # ball_edge is inside the safe zone (dist 100 < 200) and take no damage
    assert ball_edge.hp == 100.0
    assert ball_edge.alive == True

    # ball_outside is outside the safe zone (dist ~565 > 200) and take damage
    assert ball_outside.hp == 50.0
    assert ball_outside.alive == True

    # One more tick for outside ball to die
    mode.tick(world, balls, delta=1.0)
    assert ball_outside.hp == 0.0
    assert ball_outside.alive == False

    # Check zone shrinking
    old_radius = mode.zone_radius
    mode.shrink_rate = 10.0
    mode.tick(world, balls, delta=1.0)
    assert mode.zone_radius == old_radius - 10.0

def test_poison_gas_mode_shield():
    mode = GAME_MODES["poison_gas"]
    world = MockWorld()

    ball = MockBall(100, 100)
    ball.shield = 25.0
    balls = [ball]

    mode.setup(world, balls)
    mode.zone_x = 500.0
    mode.zone_y = 500.0
    mode.zone_radius = 200.0
    mode.outside_damage_per_second = 50.0

    mode.tick(world, balls, delta=1.0)

    # Shield should take 25 damage, HP should take remaining 25 damage
    assert ball.shield == 0.0
    assert ball.hp == 75.0
