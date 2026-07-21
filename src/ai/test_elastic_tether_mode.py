import pytest
import math
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.dead_balls = []
        self._deal_damage_calls = []

    def _deal_damage(self, attacker, target, damage=None):
        if damage is None:
            damage = 10.0
        self._deal_damage_calls.append((attacker, target, damage))
        target.hp -= damage
        if target.hp <= 0:
            target.alive = False

class MockBall:
    def __init__(self, id, x, y, team=None):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.team = team
        self.alive = True
        self.hp = 100.0
        self.radius = 15.0
        self.ball_type = "basic"
        self.tether_target = None
        self.tether_cooldown = 0.0

def test_elastic_tether_pull_force():
    mode = GAME_MODES.get("elastic_tether")
    assert mode is not None, "Elastic Tether mode not found"

    world = MockWorld()
    b1 = MockBall(1, 100.0, 100.0)
    b2 = MockBall(2, 500.0, 100.0) # Distance 400, > 250 max_distance
    b3 = MockBall(3, 100.0, 200.0)
    b4 = MockBall(4, 200.0, 200.0) # Distance 100, < 250

    balls = [b1, b2, b3, b4]
    mode.setup(world, balls)

    # After setup, pairs should be tethered
    assert b1.tether_target is not None
    assert b3.tether_target is not None

    # Tick to apply forces
    mode.tick(world, balls, 0.1)

    # Find paired balls
    pair_1_2 = False
    if b1.tether_target == b2:
        assert b1.vx > 0 and b2.vx < 0
        pair_1_2 = True
    elif b1.tether_target == b3:
        pass # Handle random pairing if needed, but we check if they are pulled when far

    # We can just verify that for balls that are far apart, they have non-zero velocity
    # For balls close together, their velocities are still 0
    # To be precise, setup assigns them in order:
    # 0 -> 1, 2 -> 3

    if b1.tether_target == b2:
        assert b1.vx > 0
        assert b2.vx < 0
    if b3.tether_target == b4:
        assert b3.vx == 0
        assert b4.vx == 0

def test_elastic_tether_collision_damage():
    mode = GAME_MODES.get("elastic_tether")
    assert mode is not None, "Elastic Tether mode not found"

    world = MockWorld()
    b1 = MockBall(1, 100.0, 100.0)
    b2 = MockBall(2, 110.0, 100.0) # Distance 10, < 35 (radius*2+5)

    balls = [b1, b2]
    mode.setup(world, balls)

    # Clear any potential initial velocities
    b1.vx, b1.vy = 0.0, 0.0
    b2.vx, b2.vy = 0.0, 0.0

    mode.tick(world, balls, 0.1)

    # Damage should be dealt
    assert len(world._deal_damage_calls) == 2
    # Check cooldown is set
    assert b1.tether_cooldown > 0.0
    assert b2.tether_cooldown > 0.0

    # Next tick shouldn't deal damage because of cooldown
    world._deal_damage_calls = []
    mode.tick(world, balls, 0.1)
    assert len(world._deal_damage_calls) == 0

if __name__ == "__main__":
    pytest.main(["-v", "src/ai/test_elastic_tether_mode.py"])
