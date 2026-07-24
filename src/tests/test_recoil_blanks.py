from ai.action import Action
import math

class MockBall:
    def __init__(self, **kwargs):
        self.id = 1
        self.x = 100
        self.y = 100
        self.vx = 0
        self.vy = 0
        self.hp = 100
        self.max_hp = 100
        self.damage = 10
        self.stamina = 100
        self.radius = 10
        self.speed = 100
        self.skill = "recoil_blanks"
        self.skill_timer = 0
        self.is_intangible = False
        self.bounces_left = 0
        for k, v in kwargs.items():
            setattr(self, k, v)
    def has_meta(self, x): return False
    def get_meta(self, x): return None

class MockWorld:
    def __init__(self):
        self.balls = []
        self.arena = type("MockArena", (), {"hazards": []})
        self.events = []

def test_recoil_blanks():
    ball = MockBall(skill="recoil_blanks")
    enemy = MockBall(id=2, x=150, y=100) # enemy to the right
    world = MockWorld()
    world.balls = [ball, enemy]

    action = Action(ball, world)
    action._use_skill()

    assert len(world.arena.hazards) == 3
    hazard = world.arena.hazards[0]
    assert hazard.kind == "blank_burst"
    assert hazard.damage == 0
    assert hazard.vx > 0
    assert ball.vx < 0
    assert ball.skill_timer > 0
