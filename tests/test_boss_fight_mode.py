import pytest
from ai.game_modes import BossFightMode

class MockArena:
    width = 1000
    height = 1000

class MockWorld:
    arena = MockArena()

class MockBall:
    def __init__(self, id):
        self.id = id
        self.ball_type = "ai"
        self.alive = True
        self.max_hp = 100
        self.hp = 100
        self.damage = 10
        self.radius = 10
        self.base_speed = 50.0
        self.x = 0
        self.y = 0

def test_boss_fight_setup():
    mode = BossFightMode()
    world = MockWorld()
    balls = [MockBall(i) for i in range(5)]

    mode.setup(world, balls)

    assert balls[0].team == "Boss"
    assert balls[0].max_hp == 1000
    assert balls[0].radius == 30
    assert balls[0].base_speed <= 55.0

    for b in balls[1:]:
        assert b.team == "Hunters"

def test_boss_fight_winner():
    mode = BossFightMode()
    world = MockWorld()
    balls = [MockBall(i) for i in range(5)]
    mode.setup(world, balls)

    # All alive
    assert mode.check_winner(world, balls) is None

    # Hunters win
    balls[0].alive = False
    assert mode.check_winner(world, balls) == "Hunters"

    # Boss wins
    balls[0].alive = True
    for b in balls[1:]:
        b.alive = False
    assert mode.check_winner(world, balls) == "Boss"
