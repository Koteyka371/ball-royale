import pytest
from ai.action import Action

class MockBall:
    def __init__(self, x=0, y=0, hp=100.0, max_hp=100.0, id=1, team=1):
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = max_hp
        self.id = id
        self.team = team
        self.alive = True
        self.vx = 0.0
        self.vy = 0.0
        self.speed = 100.0
        self.stamina = 100.0
        self.is_player = True
        self.is_minion = False
        self.speed_debuff_timer = 0.0
        self.speed_debuff_multiplier = 1.0
        self.stun_timer = 0.0

    def get(self, attr, default=None):
        return getattr(self, attr, default)

    def clamp_position(self, *args, **kwargs):
        pass

class MockWorld:
    def __init__(self, balls=None):
        self.balls = balls or []
        self.events = []
        self.tick = 0
        self.booster_manager = None
        self.arena = MockArena()

class MockArena:
    def __init__(self):
        self.hazards = []

def test_leech_tether_slowing_and_draining():
    b1 = MockBall(0, 0, id=1, team=1)
    b2 = MockBall(50, 0, id=2, team=2)
    world = MockWorld([b1, b2])

    action = Action(b1, world)

    # Cast skill
    b1.skill = "leech_tether"
    action.execute("action_skill", 0.1)
    action._get_enemies = lambda: [b2]
    action._use_skill() # Force use

    assert getattr(b1, "leech_tether_target", None) == b2
    assert getattr(b1, "leech_tether_timer", 0.0) == 3.0

    # Simulate tick
    b1.hp = 90.0 # Make sure we can see healing
    b1.skill = "idle"
    action.execute("idle", 0.1)

    assert b1.hp > 90.0
    assert b2.hp < 100.0
    assert getattr(b2, "speed_debuff_timer", 0.0) > 0.0
    assert getattr(b2, "speed_debuff_multiplier", 1.0) == 0.5
    assert getattr(b2, "stun_timer", 0.0) == 0.0 # Should not be stunning

def test_leech_tether_manual_targeting():
    b1 = MockBall(0, 0, id=1, team=1)
    b2 = MockBall(50, 0, id=2, team=2) # Closer
    b3 = MockBall(100, 0, id=3, team=2) # Farther
    world = MockWorld([b1, b2, b3])

    action = Action(b1, world)

    # Cast skill with manual target
    b1.leech_tether_target_id = 3
    b1.skill = "leech_tether"
    action._use_skill()

    assert getattr(b1, "leech_tether_target", None) == b3
    assert getattr(b1, "leech_tether_timer", 0.0) == 3.0
