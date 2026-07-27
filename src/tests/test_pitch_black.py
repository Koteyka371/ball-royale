import pytest
import math
from ai.game_modes import PitchBlackIlluminationMode, GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self):
        self.alive = True
        self.x = 100.0
        self.y = 100.0
        self.vx = 50.0
        self.vy = 50.0
        self.hp = 100.0
        self.attack_timer = 0.0
        self.radius = 15.0
        self.ball_type = "warrior"
        self.is_invisible = False

def test_pitch_black_illumination_mode():
    world = MockWorld()
    ball = MockBall()
    mode = PitchBlackIlluminationMode()

    # Test setup
    mode.setup(world, [ball])
    assert world.arena.is_night == True
    assert ball.is_invisible == True

    # Test tick - normal
    mode.tick(world, [ball], 0.016)
    assert ball.is_invisible == True

    # Test tick - damage
    ball.hp = 80.0
    mode.tick(world, [ball], 0.016)
    assert ball.is_invisible == False
    assert getattr(ball, "_pb_vis_timer", 0) > 0

    # Wait for visibility to expire
    for _ in range(100):
        mode.tick(world, [ball], 0.016)
    assert ball.is_invisible == True

    # Test tick - attack
    ball.attack_timer = 0.0
    mode.tick(world, [ball], 0.016)
    ball.attack_timer = 1.0
    mode.tick(world, [ball], 0.016)
    assert ball.is_invisible == False
    assert len(world.arena.hazards) == 1

    flare = world.arena.hazards[0]
    assert flare.kind == "flare"

    # Wait for flare to expire
    for _ in range(200):
        mode.tick(world, [ball], 0.016)
    assert len(world.arena.hazards) == 0
    assert ball.is_invisible == True

    # Test tick - bounce
    ball.x = 10.0
    ball.vx = -50.0
    mode.tick(world, [ball], 0.016)
    ball.vx = 50.0
    mode.tick(world, [ball], 0.016)
    assert ball.is_invisible == False
