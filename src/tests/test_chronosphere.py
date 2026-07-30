import pytest
import pytest
import pytest
from ai.action import Action

class MockBall:
    def __init__(self, x, y, team=1):
        self.x = x
        self.y = y
        self.team = team
        self.inventory = []
        self.skill_timer = 5.0
        self.speed = 100.0
        self.radius = 10.0
        self.max_hp = 100.0
        self.hp = 100.0
        self.ball_type = "test"
        self.alive = True

class MockBooster:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = 15.0

class MockArena:
    def __init__(self):
        self.hazards = []

    def clamp_position(self, x, y, r):
        return x, y, False

class MockWorld:
    def __init__(self):
        self.balls = []
        self.boosters = []
        self.events = []
        self.arena = MockArena()

    def get_nearby_entities(self, ball, radius):
        return {
            "boosters": self.boosters,
            "hazards": self.arena.hazards,
            "enemies": [b for b in self.balls if b != ball and b.team != ball.team],
            "allies": [b for b in self.balls if b != ball and b.team == ball.team],
            "items": []
        }

def test_chronosphere_aura():
    ball1 = MockBall(0, 0, 1) # Has chronosphere
    ball1.skill_timer = 5.0

    ball2 = MockBall(50, 0, 1) # Ally, within range
    ball2.skill_timer = 10.0

    ball3 = MockBall(500, 0, 1) # Ally, out of range
    ball3.skill_timer = 10.0

    ball4 = MockBall(0, 50, 2) # Enemy, within range
    ball4.skill_timer = 10.0

    booster = MockBooster(0, 0, "chronosphere_booster")

    world = MockWorld()
    world.balls = [ball1, ball2, ball3, ball4]
    world.boosters = [booster]

    action = Action(ball1, world)
    action._collect_booster(0.1)

    assert getattr(ball1, "chronosphere_timer", 0) == 5.0

    # Self cooldown acceleration
    action._update_skill_timer(1.0)
    assert ball1.skill_timer == 0.0 # 5.0 - 1.0 * 5.0 = 0.0

    # Ally cooldown acceleration
    action2 = Action(ball2, world)
    action2._update_skill_timer(1.0)
    assert ball2.skill_timer == 5.0 # 10.0 - 1.0 * 5.0 = 5.0

    # Out of range ally unaffected (normal cd rate)
    action3 = Action(ball3, world)
    action3._update_skill_timer(1.0)
    assert ball3.skill_timer == 9.0 # 10.0 - 1.0 = 9.0

    # Enemy cooldown deceleration (frozen/very slow)
    action4 = Action(ball4, world)
    action4._update_skill_timer(1.0)
    assert ball4.skill_timer == 9.8 # 10.0 - 1.0 * 0.2 = 9.8
