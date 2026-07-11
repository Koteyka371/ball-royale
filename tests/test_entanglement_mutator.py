import pytest
from ai.game_modes import EntanglementMutatorMode

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

def test_entanglement_mutator_loop():
    mode = EntanglementMutatorMode()
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

    # Ball 1 takes damage
    b1.hp = 90.0

    # Tick - Ball 2 should mirror it and also drop to 90
    mode.tick(world, balls)
    assert b2.hp == 90.0

    # Tick again - we should NOT infinitely loop. Both should stay at 90.
    mode.tick(world, balls)
    assert b1.hp == 90.0
    assert b2.hp == 90.0

def test_entanglement_mutator_healing():
    mode = EntanglementMutatorMode()
    world = MockWorld()
    b1 = MockBall(1)
    b2 = MockBall(2)
    b1.hp = 50.0
    b2.hp = 50.0
    balls = [b1, b2]

    mode.setup(world, balls)

    # Tick to initialize states
    mode.tick(world, balls)

    # Ball 1 heals
    b1.hp = 70.0

    # Tick - Ball 2 should mirror the heal
    mode.tick(world, balls)
    assert b2.hp == 70.0

    # Tick again - should stay at 70
    mode.tick(world, balls)
    assert b1.hp == 70.0
    assert b2.hp == 70.0
