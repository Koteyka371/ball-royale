import pytest

class MockBall:
    def __init__(self, bid, x, y):
        self.id = bid
        self.x = x
        self.y = y
        self.alive = True
        self.radius = 15
        self.max_hp = 100.0
        self.hp = 100.0
        self.base_speed = 100.0
        self.base_damage = 10.0
        self.ball_type = "basic"

class MockWorld:
    def __init__(self):
        self.width = 800
        self.height = 600
        self.events = []

from ai.game_modes import GAME_MODES

def test_chaotic_artifact():
    mode = GAME_MODES["chaotic_artifact"]
    world = MockWorld()
    balls = [MockBall(1, 100, 100), MockBall(2, 700, 100)]

    mode.setup(world, balls)
    assert mode.artifact_spawned
    assert mode.artifact_holder_id is None

    # Tick without touching artifact
    mode.apply_dynamic_traits(world, balls, 0.1)
    assert mode.artifact_holder_id is None
    assert len(world.events) == 1

    # Move ball 1 to artifact
    balls[0].x = mode.artifact_x
    balls[0].y = mode.artifact_y

    mode.apply_dynamic_traits(world, balls, 0.1)
    assert mode.artifact_holder_id == 1

    # Check massive buff
    assert balls[0].max_hp == 300.0
    assert balls[0].base_speed == 150.0
    assert balls[0].base_damage == 20.0

    # Fast forward time
    mode.apply_dynamic_traits(world, balls, 10.1)

    # Wait, 10.1 seconds means randomize triggers
    print(balls[0].ball_type)
    assert balls[0].ball_type in mode.ball_types
    assert balls[0].base_speed >= 150.0
