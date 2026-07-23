import pytest
from ai.action import Action

class MockWorld:
    def __init__(self):
        self.balls = []
        self.events = []
        self.grid = None
        self.arena = type('Mock', (), {'hazards': []})()
        self.leaderboard_manager = type('Mock', (), {'data': {'current_season': 4}})()

    def get_nearby_entities(self, ball, radius):
        return {"balls": [], "boosters": [], "hazards": []}

class MockBall:
    def __init__(self, **kwargs):
        self.id = "b1"
        self.x = 0
        self.y = 0
        self.radius = 10
        self.team = "A"
        self.ball_type = "phantom"
        self.hp = 100
        self.base_hp = 100
        self.stamina = 100.0
        self.max_stamina = 100.0
        self.speed = 100.0
        self.base_speed = 100.0
        self.speed_multiplier = 1.0
        self.damage_multiplier = 1.0
        self.base_damage = 10.0
        self.skill = "phantom_stride"
        self.active_skill = "phantom_stride"
        self.skills = ["phantom_stride"]
        self.skill_timer = 0.0
        self.phantom_stride_active = False
        self.intangible = False
        self.hazard_immunity_timer = 0.0
        self.silence_timer = 0.0
        self.intangible_timer = 0.0
        self.anchor_trap_timer = 0.0
        self.is_blinded = False
        self._base_speed_set = True
        self.has_meta = lambda k: False
        self.use_skill = lambda: None
        for k, v in kwargs.items():
            setattr(self, k, v)

def test_phantom_stride():
    world = MockWorld()
    ball = MockBall()
    world.balls.append(ball)
    action = Action(ball, world)

    assert not ball.phantom_stride_active
    assert not ball.intangible

    ball.skill = "phantom_stride"
    action._use_skill()

    assert ball.phantom_stride_active

    for _ in range(6):
        action._update_skill_timer(0.1)

    ball.skill_timer -= 0.6

    assert ball.phantom_stride_active
    assert ball.intangible
    assert ball.stamina == 76.0
    assert ball.hazard_immunity_timer > 0.0

    # Deactivate skill manually
    action._use_skill()
    assert not ball.phantom_stride_active
    assert not ball.intangible

def test_phantom_stride_auto_deactivate_on_no_stamina():
    world = MockWorld()
    ball = MockBall(stamina=10.0)
    world.balls.append(ball)
    action = Action(ball, world)

    ball.skill = "phantom_stride"
    action._use_skill() # stamina is 10.0, threshold to activate is 20.0
    assert not ball.phantom_stride_active

    # Give it stamina to activate
    ball.stamina = 50.0
    action._use_skill()
    assert ball.phantom_stride_active

    # Update timer drains stamina to 0
    for _ in range(13):
        action._update_skill_timer(0.1)

    assert not ball.phantom_stride_active
    assert not ball.intangible
    assert ball.stamina == 0.0
