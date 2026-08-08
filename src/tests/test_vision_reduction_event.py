from ai.game_modes import PeriodicVisionReductionEventMode
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

class MockWorld:
    def __init__(self):
        self.events = []

    def add_event(self, type, data):
        self.events.append((type, data))

def test_periodic_vision_reduction_event():
    event = PeriodicVisionReductionEventMode()
    event.interval = 15.0
    event.duration = 5.0
    ball1 = MockBall()
    ball2 = MockBall()
    ball2.inventory = "decoy_flare_item"

    world = MockWorld()
    balls = [ball1, ball2]

    event.setup(world, balls)
    assert event.timer == 15.0
    assert event.active_effect == False

    # Tick to just before the event
    event.tick(world, balls, 14.9)
    assert event.active_effect == False

    # Tick to trigger the event
    event.tick(world, balls, 0.2)
    assert event.active_effect == True
    assert event.effect_timer > 0

    assert ball1.vision_reduction_timer == 5.0
    assert ball1.perception_radius == 250.0
    assert ball1.vision_reduction_applied == True

    assert ball2.vision_reduction_timer == 0.0 # countered
    assert ball2.perception_radius == 500.0

    # Tick within the event
    event.tick(world, balls, 1.0)
    assert event.active_effect == True
    assert ball1.perception_radius == 250.0
    assert ball2.perception_radius == 500.0  # Countered
    assert ball2.vision_reduction_applied == False

    # Tick past the event
    event.tick(world, balls, 4.1)
    assert event.active_effect == False
    assert ball1.perception_radius == 500.0
    assert ball1.vision_reduction_applied == False