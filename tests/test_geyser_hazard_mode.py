import pytest
from ai.game_modes import GeyserHazardMode

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.damage_dealt = 0

    def _deal_damage(self, attacker, target, damage):
        self.damage_dealt += damage
        target.hp -= damage

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 15.0
        self.alive = True
        self.ball_type = "player"
        self.hp = 100.0
        self.z_height = 0.0
        self.z_velocity = 0.0
        self.is_frictionless = False

def test_geyser_hazard_setup():
    mode = GeyserHazardMode()
    world = MockWorld()
    balls = []
    mode.setup(world, balls)
    assert len(world.arena.hazards) == 3
    assert world.arena.hazards[0].kind == "geyser"

def test_geyser_eruption_and_launch():
    mode = GeyserHazardMode()
    world = MockWorld()
    ball = MockBall(500, 500)
    balls = [ball]
    mode.setup(world, balls)

    # Force a geyser directly under the ball and set it to erupt
    hazard = world.arena.hazards[0]
    hazard.x = 500
    hazard.y = 500
    hazard.is_erupting = True
    hazard.erupt_timer = 2.0

    mode.tick(world, balls, delta=0.1)

    assert ball.z_height > 0
    assert ball.z_velocity == 800.0
    assert ball.is_frictionless is True

def test_geyser_fall_damage():
    mode = GeyserHazardMode()
    world = MockWorld()
    ball = MockBall(500, 500)
    ball.z_height = 1.0
    ball.z_velocity = -200.0 # Falling fast
    balls = [ball]

    mode.tick(world, balls, delta=0.1)

    assert ball.z_height == 0.0
    assert ball.is_frictionless is False
    assert world.damage_dealt > 0
    assert ball.hp < 100.0
