from src.ai.game_modes import VisionReductionEventMode
from unittest.mock import MagicMock

class MockBall:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.hp = 100
        self.base_perception_radius = 500
        self.perception_radius = 500
        self.alive = True
        self.inventory = ""
        self.mutated_env = ""

def test_vision_reduction_event():
    event = VisionReductionEventMode()
    ball1 = MockBall()
    ball2 = MockBall()
    ball2.inventory = "decoy_flare_item"

    world = {"events": []}
    balls = [ball1, ball2]

    event.setup(world, balls)
    assert ball1.vision_reduction_timer == 30.0
    assert ball1.perception_radius == 250.0
    assert ball1.vision_reduction_applied == True

    assert ball2.vision_reduction_timer == 30.0
    assert ball2.perception_radius == 250.0

    event.tick(world, balls, 1.0)
    assert event.timer == 29.0
    assert ball1.perception_radius == 250.0
    assert ball2.perception_radius == 500.0  # Countered
    assert ball2.vision_reduction_applied == False

    event.tick(world, balls, 29.0)
    assert event.active == False
    assert ball1.perception_radius == 500.0
    assert ball1.vision_reduction_applied == False
