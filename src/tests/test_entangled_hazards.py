import pytest
from ai.game_modes import EntangledHazardsMode
from arena.procedural_arena import Hazard
import math

class MockBall:
    def __init__(self, ball_id, x, y):
        self.id = ball_id
        self.x = x
        self.y = y
        self.radius = 15.0
        self.alive = True
        self.ball_type = "normal"
        self.hp = 100.0
        self.stun_timer = 0.0
        self.burn_timer = 0.0
        self.poison_timer = 0.0
        self.blindness_timer = 0.0
        self.confusion_timer = 0.0
        self.slow_timer = 0.0
        self.frozen_timer = 0.0
        self.silence_timer = 0.0

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

def test_entangled_hazards():
    mode = EntangledHazardsMode()
    b1 = MockBall(1, 100, 100)
    b2 = MockBall(2, 200, 200)

    world = MockWorld()
    mode.setup(world, [b1, b2])

    assert len(world.arena.hazards) == 4 # 2 pairs

    # Force positions to be exactly on the first pair of hazards
    h1 = world.arena.hazards[0]
    paired_id = getattr(h1, 'paired_hazard_id', None)
    assert paired_id is not None
    h2 = [h for h in world.arena.hazards if getattr(h, "id", None) == paired_id][0]

    h1.radius = 50.0
    h2.radius = 50.0

    b1.x, b1.y = h1.x, h1.y
    b2.x, b2.y = h2.x, h2.y

    mode.tick(world, [b1, b2], 0.1) # init tick

    # Deal damage and status effect to b1
    b1.take_damage(20.0)
    b1.stun_timer += 4.0

    mode.tick(world, [b1, b2], 0.1)

    # Verify that b2 took half the damage and half the status effect
    assert math.isclose(b2.hp, 100.0 - (20.0 * 0.5), rel_tol=1e-5)
    assert math.isclose(b2.stun_timer, 4.0 * 0.5, rel_tol=1e-5)

    # Deal damage to b2
    b2.take_damage(10.0)
    b2.burn_timer += 2.0

    mode.tick(world, [b1, b2], 0.1)

    assert math.isclose(b1.hp, 80.0 - (10.0 * 0.5), rel_tol=1e-5)
    assert math.isclose(b1.burn_timer, 2.0 * 0.5, rel_tol=1e-5)

def test_entangled_hazards_no_effect_if_outside():
    mode = EntangledHazardsMode()
    b1 = MockBall(1, 100, 100)
    b2 = MockBall(2, 200, 200)

    world = MockWorld()
    mode.setup(world, [b1, b2])

    # Put b1 on hazard 1, b2 far away
    h1 = world.arena.hazards[0]
    b1.x, b1.y = h1.x, h1.y
    b2.x, b2.y = 9999, 9999 # Outside any hazard

    mode.tick(world, [b1, b2], 0.1)

    b1.take_damage(20.0)
    mode.tick(world, [b1, b2], 0.1)

    # b2 should NOT take damage because it is not on the paired hazard
    assert b2.hp == 100.0
