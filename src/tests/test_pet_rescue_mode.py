import pytest
from ai.game_modes import GAME_MODES

class MockWorld:
    def __init__(self):
        self.arena = type('Arena', (), {'hazards': [], 'items': [], 'width': 1000, 'height': 1000})()
        self.events = []
        self.balls = []

class MockBall:
    def __init__(self):
        self.id = 1
        self.x = 500
        self.y = 500
        self.speed = 100
        self.hp = 90
        self.max_hp = 100
        self.alive = True
        self.ball_type = "player"

def test_pet_rescue_mode():
    world = MockWorld()
    ball = MockBall()
    world.balls.append(ball)

    mode = GAME_MODES["pet_rescue"]
    mode.setup(world, [ball])

    # Tick loop to spawn
    mode.tick(world, [ball], 5.1)

    # Check if a wild_pet spawned
    assert len(world.arena.hazards) > 0
    assert getattr(world.arena.hazards[0], "kind", "") == "wild_pet"
