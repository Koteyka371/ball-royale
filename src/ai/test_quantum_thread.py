import pytest
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, id, x=0, y=0, hp=100.0, ball_type="warrior"):
        self.id = id
        self.x = x
        self.y = y
        self.hp = hp
        self.alive = True
        self.ball_type = ball_type
        self.quantum_paired_with = None
        self.stun_timer = 0.0
        self.defense_multiplier = 1.0
        self.speed_booster_timer = 0.0

class MockWorld:
    def __init__(self):
        self.events = []

def test_quantum_thread_setup():
    mode = GAME_MODES["quantum_thread_mode"]
    b1 = MockBall(1)
    b2 = MockBall(2)
    b3 = MockBall(3)
    b4 = MockBall(4, ball_type="spectator")

    world = MockWorld()
    mode.setup(world, [b1, b2, b3, b4])

    # 3 active balls. 2 should be paired, 1 should be paired with None
    paired = [b for b in [b1, b2, b3] if b.quantum_paired_with is not None]
    unpaired = [b for b in [b1, b2, b3] if b.quantum_paired_with is None]

    assert len(paired) == 2
    assert len(unpaired) == 1
    assert paired[0].quantum_paired_with == paired[1]
    assert paired[1].quantum_paired_with == paired[0]

def test_quantum_thread_damage_transfer():
    mode = GAME_MODES["quantum_thread_mode"]
    b1 = MockBall(1)
    b2 = MockBall(2)

    world = MockWorld()
    mode.setup(world, [b1, b2])

    # b1 gets damaged by 20 outside of mode
    b1.hp = 80.0
    mode.tick(world, [b1, b2])

    # b2 should lose 50% of 20 = 10 hp
    assert b2.hp == pytest.approx(90.0)

def test_quantum_thread_heal_transfer():
    mode = GAME_MODES["quantum_thread_mode"]
    b1 = MockBall(1, hp=50.0)
    b2 = MockBall(2, hp=50.0)

    world = MockWorld()
    mode.setup(world, [b1, b2])

    # b1 gets healed by 30
    b1.hp = 80.0
    mode.tick(world, [b1, b2])

    # b2 should heal by 50% of 30 = 15 hp
    assert b2.hp == pytest.approx(65.0)

def test_quantum_thread_booster_transfer():
    mode = GAME_MODES["quantum_thread_mode"]
    b1 = MockBall(1)
    b2 = MockBall(2)

    world = MockWorld()
    mode.setup(world, [b1, b2])

    b1.speed_booster_timer = 10.0
    mode.tick(world, [b1, b2])

    assert b2.speed_booster_timer == pytest.approx(5.0)

def test_quantum_thread_break():
    mode = GAME_MODES["quantum_thread_mode"]
    b1 = MockBall(1, x=0, y=0)
    b2 = MockBall(2, x=0, y=0)

    world = MockWorld()
    mode.setup(world, [b1, b2])

    b1.x = 700.0 # greater than 600
    mode.tick(world, [b1, b2])

    assert b1.quantum_paired_with is None
    assert b2.quantum_paired_with is None
    assert b1.stun_timer == pytest.approx(2.0)
    assert b2.stun_timer == pytest.approx(2.0)
    assert b1.defense_multiplier == pytest.approx(0.7) # 1.0 - 0.3
    assert b2.defense_multiplier == pytest.approx(0.7)
