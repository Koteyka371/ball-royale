from ai.action import Action
import random

class MockArena:
    def __init__(self):
        self.seasonal_modifier = "winter"
        self.hazards = []
    def clamp_position(self, x, y, r): return x, y, False
    def update_zone(self, t, d): pass

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.snowball_event_active = True
        self.events = []
        self.balls = []
    def _deal_damage(self, attacker, target, dmg=None):
        pass
    def get_nearby_entities(self, ball, radius):
        return {"enemies": [], "allies": []}

class MockBall:
    def __init__(self):
        self.x = 50.0
        self.y = 50.0
        self.vx = 50.0
        self.vy = 50.0
        self.radius = 10.0
        self.damage = 10.0
        self.base_radius = 10.0
        self.base_damage = 10.0
        self.ball_type = "normal"
        self.alive = True
        self.id = 1
        self.team = 1
        self.hp = 100
        self.out_of_combat_timer = 0.0

def test_snowball_event_active():
    w = MockWorld()
    b1 = MockBall()
    b2 = MockBall()
    b2.id = 2
    b2.team = 2
    w.balls = [b1, b2]

    act = Action(b1, w)

    assert not hasattr(b2, "snowball_stacks")
    assert not hasattr(b2, "frozen_timer")

    # In our patched logic, we are NOT modifying b1.damage permanently anymore.
    # original_damage *= 0.2 reduces the damage output *in that specific function call*, but doesn't change b1.damage.
    for i in range(4):
        act._attempt_damage(b1, b2)
        assert b2.snowball_stacks == i + 1
        assert b2.slow_timer >= 3.0
        assert getattr(b2, "frozen_timer", 0.0) == 0.0
        assert b1.damage == 10.0  # Assure it is NOT mutated!

    act._attempt_damage(b1, b2)
    assert b2.snowball_stacks == 0
    assert b2.slow_timer == 0.0
    assert b2.frozen_timer >= 3.0
