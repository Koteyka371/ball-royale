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
        self.events = []
        self._deal_damage_calls = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

    def _deal_damage(self, attacker, target, damage=None):
        if damage is None:
            damage = 10.0
        self._deal_damage_calls.append((attacker, target, damage))
        target.hp -= damage
        if target.hp <= 0:
            target.alive = False

class MockBall:
    def __init__(self, id, x, y, team):
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

    def __eq__(self, other):
        if isinstance(other, MockBall):
            return self.id == other.id
        return False

def test_rubber_band_mode_velocity_snap():
    mode = GAME_MODES.get("rubber_band")
    assert mode is not None, "Rubber Band mode not found"

    world = MockWorld()
    b1 = MockBall(1, 100.0, 100.0, "TeamA")
    b2 = MockBall(2, 500.0, 100.0, "TeamA") # Distance is 400, > 300
    b3 = MockBall(3, 100.0, 200.0, "TeamB")
    b4 = MockBall(4, 150.0, 200.0, "TeamB") # Distance is 50, < 300

    balls = [b1, b2, b3, b4]

    mode.setup(world, balls)
    mode.tick(world, balls, 0.1)

    # b1 and b2 should have velocity pointing towards each other
    assert b1.vx > 0
    assert b2.vx < 0

    # b3 and b4 are close, should not have velocity changes
    assert b3.vx == 0
    assert b4.vx == 0

def test_rubber_band_mode_damage():
    mode = GAME_MODES.get("rubber_band")
    assert mode is not None, "Rubber Band mode not found"

    world = MockWorld()
    # Snap on X axis
    b1 = MockBall(1, 100.0, 100.0, "TeamA")
    b2 = MockBall(2, 500.0, 100.0, "TeamA") # Distance 400

    # enemy exactly in the middle of them on the line
    enemy = MockBall(3, 300.0, 100.0, "TeamB")

    balls = [b1, b2, enemy]
    mode.setup(world, balls)
    mode.tick(world, balls, 0.1)

    # Enemy should have taken damage
    assert len(world._deal_damage_calls) > 0
    # Expected damage = damage * delta * 60 = 50 * 0.1 * 60 = 300
    attacker, target, damage = world._deal_damage_calls[0]
    assert target == enemy
    assert damage > 0

def test_rubber_band_mode_no_damage_if_not_on_line():
    mode = GAME_MODES.get("rubber_band")
    world = MockWorld()
    b1 = MockBall(1, 100.0, 100.0, "TeamA")
    b2 = MockBall(2, 500.0, 100.0, "TeamA")

    # enemy far away from the line segment
    enemy = MockBall(3, 300.0, 300.0, "TeamB")

    balls = [b1, b2, enemy]
    mode.setup(world, balls)
    mode.tick(world, balls, 0.1)

    assert len(world._deal_damage_calls) == 0

if __name__ == "__main__":
    pytest.main(["-v", "src/ai/test_rubber_band_mode.py"])
