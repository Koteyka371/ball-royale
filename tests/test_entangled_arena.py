import pytest
from src.ai.game_modes import EntangledArenaMode

class MockBall:
    def __init__(self, id, ball_type="player"):
        self.id = id
        self.ball_type = ball_type
        self.alive = True
        self.hp = 100.0
        self.max_hp = 100.0
        self.vx = 0.0
        self.vy = 0.0
        self.stun_timer = 0.0
        self.slow_timer = 0.0
        self.poison_timer = 0.0
        self.confusion_timer = 0.0
        self.silence_timer = 0.0

class MockWorld:
    def __init__(self):
        self.events = []
        self.dead_balls = []

def test_entangled_arena_mode_loop():
    mode = EntangledArenaMode()
    world = MockWorld()
    b1 = MockBall(1)
    b2 = MockBall(2)
    balls = [b1, b2]

    mode.setup(world, balls)

    # Assert they are paired
    assert b1.random_entangled_with == b2
    assert b2.random_entangled_with == b1

    # Tick to initialize states properly across all entities
    mode.tick(world, balls)

    # Ball 1 takes damage (100 -> 90, so 10 damage)
    b1.hp = 90.0

    # Tick - Ball 2 should mirror 50% of it and drop to 95
    mode.tick(world, balls)
    assert b2.hp == 95.0

    # Tick again - we should NOT infinitely loop. Both should stay at 90 and 95.
    mode.tick(world, balls)
    assert b1.hp == 90.0
    assert b2.hp == 95.0

def test_entangled_arena_healing():
    mode = EntangledArenaMode()
    world = MockWorld()
    b1 = MockBall(1)
    b2 = MockBall(2)
    b1.hp = 50.0
    b2.hp = 50.0
    balls = [b1, b2]

    mode.setup(world, balls)
    mode.tick(world, balls)

    # Ball 1 heals (50 -> 70, so 20 healing)
    b1.hp = 70.0

    # Tick - Ball 2 should mirror the FULL heal (from task description "share healing and buffs")
    mode.tick(world, balls)
    assert b2.hp == 70.0
