import pytest
import math
from ai.game_modes import GameMode
from ai.game_modes import SeasonalCycleMode

class MockWorld:
    def __init__(self):
        self.arena = None
        self.events = []
    def add_event(self, name, data):
        self.events.append((name, data))

class MockBall:
    def __init__(self, ball_type="base", traits=None):
        self.id = 1
        self.ball_type = ball_type
        self.traits = traits or []
        self.base_speed = 100.0
        self.base_max_speed = 100.0
        self.base_damage = 10.0
        self.speed = 100.0
        self.max_speed = 100.0
        self.damage = 10.0
        self.stamina = 100.0
        self.max_stamina = 100.0
        self.alive = True
        self.dash_cooldown = 5.0
        self.skill_timer = 5.0
        self.action_cooldown = 5.0
        self.x = 0.0
        self.y = 0.0
        self.friction_multiplier = 1.0

def test_seasonal():
    mode = SeasonalCycleMode()
    world = MockWorld()
    b1 = MockBall(traits=["nature"]) # Spring aligned
    b2 = MockBall(traits=["fire"]) # Summer aligned

    mode.setup(world, [b1, b2])

    # 0 = Spring
    assert mode.current_season == 0
    mode.tick(world, [b1, b2], 1.0)

    assert abs(b1.speed - (b1.base_speed * 2.0)) < 0.1
    assert abs(b1.damage - (b1.base_damage * 2.0)) < 0.1
    assert abs(b2.speed - b2.base_speed) < 0.1
    assert abs(b2.damage - b2.base_damage) < 0.1

    # Spring cooldown speeds up
    assert b1.dash_cooldown == 5.0 - 2.0 # 2.0 from spring effect
    assert b2.dash_cooldown == 5.0 - 2.0 # Also speeds up for non-aligned

    # Tick exactly to trigger summer change
    for _ in range(9):
        mode.tick(world, [b1, b2], 1.0)
    assert mode.current_season == 1

    # Reset stamina
    b1.stamina = 100.0
    b2.stamina = 100.0

    mode.tick(world, [b1, b2], 1.0)
    assert abs(b1.speed - b1.base_speed) < 0.1
    assert abs(b2.speed - (b2.base_speed * 2.0)) < 0.1

    # Summer drains stamina of non-aligned
    assert b1.stamina == 80.0
    assert b2.stamina == 100.0

    for _ in range(9):
        mode.tick(world, [b1, b2], 1.0)
    assert mode.current_season == 2

    # Autumn wind pushes
    prev_x = b1.x
    prev_y = b1.y
    mode.tick(world, [b1, b2], 1.0)
    # Wind moved it
    assert b1.x != prev_x or b1.y != prev_y

    for _ in range(9):
        mode.tick(world, [b1, b2], 1.0)
    assert mode.current_season == 3

    mode.tick(world, [b1, b2], 1.0)
    assert b1.friction_multiplier == 0.1

    for _ in range(9):
        mode.tick(world, [b1, b2], 1.0)
    assert mode.current_season == 0

    mode.tick(world, [b1, b2], 1.0)
    assert b1.friction_multiplier == 1.0
