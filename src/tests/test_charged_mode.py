import pytest
from unittest.mock import MagicMock
from ai.game_modes import ChargedMode

class MockBall:
    def __init__(self, id, x, y, alive=True, ball_type="default"):
        self.id = id
        self.x = x
        self.y = y
        self.alive = alive
        self.ball_type = ball_type

        # Essential attributes
        self.max_stamina = 100.0
        self.stamina = 100.0
        self.base_speed = 100.0
        self.speed = 100.0
        self.base_damage = 10.0
        self.original_base_damage = 10.0
        self.traits = []
        self.weather_immunity_timer = 999.0
        self.in_mirror_dimension = False
        self.intangible = False
        self.vision_radius = 50.0
        self.invisible = False
        self.radius = 10.0
        self.vx = 0.0
        self.vy = 0.0

def test_charged_mode_initial_assignment():
    mode = ChargedMode()
    mode.apply_dynamic_traits = lambda w, b, d: None

    b1 = MockBall(1, 0, 0)
    b2 = MockBall(2, 100, 100)

    world = MagicMock()

    mode.tick(world, [b1, b2], 0.1)

    assert hasattr(b1, "charge")
    assert b1.charge in ["positive", "negative"]
    assert hasattr(b2, "charge")
    assert b2.charge in ["positive", "negative"]

def test_charged_mode_repel():
    mode = ChargedMode()
    mode.apply_dynamic_traits = lambda w, b, d: None

    b1 = MockBall(1, 100, 100)
    b1.charge = "positive"

    b2 = MockBall(2, 101, 100) # Right next to each other
    b2.charge = "positive"

    world = MagicMock()

    mode.tick(world, [b1, b2], 0.016)

    # Assert they moved apart
    import math
    dist = math.sqrt((b2.x - b1.x)**2 + (b2.y - b1.y)**2)
    assert dist > 1.0 # Initial distance was 1.0

def test_charged_mode_attract():
    mode = ChargedMode()
    mode.apply_dynamic_traits = lambda w, b, d: None

    b1 = MockBall(1, 100, 100)
    b1.charge = "positive"

    b2 = MockBall(2, 110, 100) # Close to each other
    b2.charge = "negative"

    world = MagicMock()

    mode.tick(world, [b1, b2], 0.016)

    # Assert they moved closer
    import math
    dist = math.sqrt((b2.x - b1.x)**2 + (b2.y - b1.y)**2)
    assert dist < 10.0 # Initial distance was 10.0

def test_charged_mode_flip():
    mode = ChargedMode()
    mode.apply_dynamic_traits = lambda w, b, d: None

    b1 = MockBall(1, 0, 0)
    b1.charge = "positive"

    world = MagicMock()

    mode.charge_flip_timer = 9.9
    mode.tick(world, [b1], 0.2) # pushes over 10.0

    assert mode.charge_flip_timer < 10.0 # Resets
    assert b1.charge == "negative" # Flipped
