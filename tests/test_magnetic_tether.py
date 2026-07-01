import pytest
from ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self, balls):
        self.balls = balls
        self.arena = MockArena()

    def get_nearby_entities(self, ball, radius):
        return [b for b in self.balls if b != ball]

class MockBall:
    def __init__(self, id, team, x, y, hp=100.0):
        self.id = id
        self.team = team
        self.ball_type = team
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = hp
        self.alive = True
        self.skill = ""
        self.SKILL = ""
        self.skill_timer = 0.0
        self.speed = 100.0
        self.base_speed = 100.0
        self.radius = 20.0
        self.stamina = 100.0
        self.max_stamina = 100.0
        self.traits = []
        self.is_dashing = False
        self.inventory = []
        self.tether_timer = 0.0
        self.tether_target = None

def test_magnetic_tether():
    b1 = MockBall(1, "A", 100, 100)
    b2 = MockBall(2, "B", 400, 100)

    b1.skill = "magnetic_tether"
    b1.SKILL = "magnetic_tether"
    b1.skill_timer = 0

    world = MockWorld([b1, b2])
    action = Action(b1, world)

    action._use_skill()

    # Target should be damaged and tether set
    assert b2.hp == 95.0
    assert b1.tether_timer > 0
    assert b1.tether_target == 2

    # Update timer to pull
    action._update_skill_timer(0.1)

    # 600 * 0.1 = 60 pull
    assert b1.x > 100
    assert b1.x <= 160 # Approx due to min check
