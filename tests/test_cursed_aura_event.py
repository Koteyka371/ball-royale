import math
from ai.action import Action
from ai.game_modes import CursedAuraEventMode

class MockArena:
    def __init__(self):
        self.is_night = False

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []

class MockBall:
    def __init__(self, id, team, btype, x, y):
        self.id = id
        self.team = team
        self.ball_type = btype
        self.x = x
        self.y = y
        self.alive = True
        self.base_speed = 2.0
        self.base_damage = 10.0
        self.speed = 2.0
        self.damage = 10.0
        self.hp = 100.0
        self.max_hp = 100.0

def test_cursed_aura_event_mode():
    w = MockWorld()
    b1 = MockBall(1, "A", "type1", 0, 0)
    b2 = MockBall(2, "A", "type2", 10, 0)
    b3 = MockBall(3, "A", "type3", 20, 0)

    w.balls = [b1, b2, b3]

    mode = CursedAuraEventMode()
    mode.event_timer = 40.0
    mode.event_active = True
    mode.event_duration = 10.0

    mode.tick(w, w.balls, 0.016)

    assert getattr(b1, "cursed_aura_event_active", False) == True

    action = Action(b1, w)
    action._apply_friendly_aura(1.0)

    # 3 unique types = 2 stacks
    assert math.isclose(b1.hp, 96.0) # 100 - (2 * 2 stacks)
    assert math.isclose(b1.speed, 2.0 * (1.0 - 0.2)) # 0.8 * 2.0 = 1.6

    # Test night mode
    w.arena.is_night = True
    b_vamp = MockBall(4, "A", "vampire", 0, 0)
    w.balls = [b_vamp, b2, b3]
    mode.tick(w, w.balls, 0.016)

    action2 = Action(b_vamp, w)
    action2._apply_friendly_aura(1.0)

    assert math.isclose(b_vamp.speed, 2.0 * 1.5 * 0.8) # 2.4

def test_cursed_aura_off():
    w = MockWorld()
    b1 = MockBall(1, "A", "type1", 0, 0)
    b2 = MockBall(2, "A", "type2", 10, 0)
    w.balls = [b1, b2]

    mode = CursedAuraEventMode()
    mode.event_timer = 0.0
    mode.event_active = False

    mode.tick(w, w.balls, 0.016)

    action = Action(b1, w)
    action._apply_friendly_aura(1.0)

    # Normal aura regen
    assert math.isclose(b1.hp, 100.0) # bounded by max
