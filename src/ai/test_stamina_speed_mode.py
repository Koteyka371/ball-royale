import pytest
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, hp=100.0, max_stamina=100.0, stamina=100.0, base_speed=100.0, speed=100.0):
        self.hp = hp
        self.max_stamina = max_stamina
        self.stamina = stamina
        self.base_speed = base_speed
        self.speed = speed

class MockWorld:
    def __init__(self):
        pass

def test_stamina_speed_mode():
    mode = GAME_MODES["stamina_speed"]
    world = MockWorld()

    ball1 = MockBall(hp=100.0)
    balls = [ball1]

    mode.setup(world, balls)

    assert ball1.max_stamina == 200.0
    assert ball1.stamina == 200.0
    assert ball1.base_speed == 200.0
    assert ball1.prev_hp == 100.0

    # Tick with no damage
    mode.tick(world, balls)
    assert ball1.max_stamina == 200.0
    assert ball1.base_speed == 200.0

    # Take damage
    ball1.hp = 80.0
    mode.tick(world, balls)
    assert ball1.max_stamina == 180.0
    assert ball1.base_speed == 180.0
    assert ball1.stamina == 180.0 # Stamina also capped

    # Heal should not increase max_stamina
    ball1.hp = 90.0
    mode.tick(world, balls)
    assert ball1.max_stamina == 180.0
    assert ball1.base_speed == 180.0

    # Take more damage
    ball1.hp = 10.0
    mode.tick(world, balls)
    assert ball1.max_stamina == 100.0
    assert ball1.base_speed == 100.0
