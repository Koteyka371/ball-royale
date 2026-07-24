import pytest
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, id_val, x, y):
        self.id = id_val
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.alive = True
        self.ball_type = "normal"
        self.hp = 100.0

def test_huge_tornados_mode():
    mode = GAME_MODES["huge_tornados"]
    world = MockWorld()
    ball = MockBall(1, 500, 500)
    balls = [ball]

    mode.setup(world, balls)
    assert len(world.arena.hazards) == mode.max_tornados

    # Place a ball near a tornado to test pull and damage
    world.arena.hazards = [world.arena.hazards[0]]
    tornado = world.arena.hazards[0]
    tornado.x = 500
    tornado.y = 500
    tornado.vx = 0.0
    tornado.vy = 0.0
    tornado.vx = 0.0
    tornado.vy = 0.0
    ball.x = 400
    ball.y = 500

    initial_x = ball.x
    initial_hp = ball.hp

    mode.tick(world, balls, delta=0.1)

    # Ball should be pulled towards tornado (x should increase)
    assert ball.x > initial_x

    # Move ball inside damage radius
    ball.x = 490
    ball.y = 500
    mode.tick(world, balls, delta=0.1)
    assert ball.hp < initial_hp
