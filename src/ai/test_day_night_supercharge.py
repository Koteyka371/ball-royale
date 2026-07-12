import pytest

def test_day_night_supercharge():
    from ai.game_modes import DayNightMode
    world = type('MockWorld', (), {})()
    world.arena = type('MockArena', (), {'is_night': False, 'width': 1000, 'height': 1000})()

    mode = DayNightMode()
    mode.setup(world, [])

    b = type('MockBall', (), {'id': 1, 'alive': True, 'ball_type': 'normal', 'x': 500.0, 'y': 500.0, 'hp': 100.0, 'speed': 100.0, 'damage': 10.0, 'base_speed': 100.0, 'base_damage': 10.0, 'supercharge_timer': 0.0})()

    import random
    original_random = random.random
    try:
        # Force the random.random() check to succeed to give the supercharge buff
        random.random = lambda: 0.0000001

        mode.tick(world, [b], delta=1.0)

        assert b.supercharge_timer > 0.0
        assert b.speed == 250.0
        assert b.damage == 25.0

    finally:
        random.random = original_random

def test_day_night_supercharge_decay():
    from ai.game_modes import DayNightMode
    world = type('MockWorld', (), {})()
    world.arena = type('MockArena', (), {'is_night': False, 'hazards': [], 'width': 1000, 'height': 1000})()

    mode = DayNightMode()
    mode.setup(world, [])

    b = type('MockBall', (), {'id': 1, 'alive': True, 'ball_type': 'normal', 'x': 500.0, 'y': 500.0, 'hp': 100.0, 'speed': 250.0, 'damage': 25.0, 'base_speed': 100.0, 'base_damage': 10.0, 'supercharge_timer': 1.0})()

    import random
    original_random = random.random
    try:
        # Force no new buffs
        random.random = lambda: 1.0

        mode.tick(world, [b], delta=1.0)

        # Timer should be 0 and stats reverted
        assert b.supercharge_timer == 0.0
        assert b.speed == 100.0
        assert b.damage == 10.0

    finally:
        random.random = original_random

def test_day_night_supercharge_double_damage():
    from ai.game_modes import DayNightMode
    world = type('MockWorld', (), {})()
    world.arena = type('MockArena', (), {'is_night': False, 'hazards': [], 'width': 1000, 'height': 1000})()

    mode = DayNightMode()
    mode.setup(world, [])

    b = type('MockBall', (), {'id': 1, 'alive': True, 'ball_type': 'normal', 'x': 500.0, 'y': 500.0, 'hp': 100.0, 'supercharge_timer': 5.0})()

    # put a beam exactly on the ball
    mode.active_sunlight_beams.append({'x': 500.0, 'y': 500.0, 'radius': 150.0, 'duration': 2.0})

    mode.tick(world, [b], delta=1.0)

    # Normal beam damage per frame (delta) is 50.0 * 1.0 = 50.0
    # Supercharged ball takes double = 100.0
    # So hp should drop from 100.0 to 0.0
    assert b.hp <= 0.0
