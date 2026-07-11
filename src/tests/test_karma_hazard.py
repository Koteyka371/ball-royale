import sys
sys.path.append("src")
from ai.action import Action
from arena.procedural_arena import Hazard

class MockBall:
    def __init__(self, id, team, x, y, hp=100, damage=10):
        self.id = id
        self.team = team
        self.ball_type = "test_ball"
        self.x = x
        self.y = y
        self.hp = hp
        self.damage = damage
        self.alive = True

class MockWorld:
    def __init__(self):
        self.balls = []
        self.arena = type("Arena", (object,), {})()
        self.arena.hazards = []
        self.time = 0.0

def test_karma_hazard():
    world = MockWorld()
    b1 = MockBall(1, "red", 0, 0)
    b2 = MockBall(2, "red", 50, 0)
    world.balls = [b1, b2]

    # 1. b1 steps on karma hazard
    world.arena.hazards = [Hazard(1, 0, 0, 20, "karma_hazard", 0.0)]
    ai = Action(b1, world)

    # Run the hazard loop part
    ai.execute(0.1, 0.1)

    assert getattr(b1, "karma_timer", 0.0) > 4.0

    # 2. b1 attempts friendly fire on b2
    old_hp = b1.hp
    b2_hp = b2.hp
    ai._attempt_damage(b1, b2)

    # b1 should take damage, b2 should not
    assert b1.hp == old_hp - b1.damage
    assert b2.hp == b2_hp

    # 3. b2 attempts friendly fire on b1 (b1 has karma_timer, b2 doesn't)
    old_hp2 = b2.hp
    b1_hp2 = b1.hp
    ai2 = Action(b2, world)
    ai2._attempt_damage(b2, b1)

    # b2 should take damage, b1 should not
    assert b2.hp == old_hp2 - b2.damage
    assert b1.hp == b1_hp2
