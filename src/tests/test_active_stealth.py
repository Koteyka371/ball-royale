import pytest
from ai.action import Action
from ai.perception import Perception

class MockWorld:
    def __init__(self):
        self.balls = []
        self.events = []
        self.grid = None
        self.arena = type('Mock', (), {'hazards': []})()
        self.leaderboard_manager = type('Mock', (), {'data': {'current_season': 4}})()

    def get_nearby_entities(self, ball, radius):
        # Only return the enemies for test
        enemies = [b for b in self.balls if b.id != ball.id]
        return {"enemies": enemies, "allies": [], "boosters": [], "traps": []}

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
        self.skill = "active_stealth"
        self.active_skill = "active_stealth"
        self.skills = ["active_stealth"]
        self.skill_timer = 0.0
        self.active_stealth_active = False
        self.is_blinded = False
        self._base_speed_set = True
        self.has_meta = lambda k: False
        self.use_skill = lambda: None
        for k, v in kwargs.items():
            setattr(self, k, v)

def test_active_stealth():
    world = MockWorld()
    ball = MockBall()
    world.balls.append(ball)
    action = Action(ball, world)

    assert not getattr(ball, "active_stealth_active", False)

    ball.skill = "active_stealth"
    action._use_skill()

    assert ball.active_stealth_active

    for _ in range(6):
        action._update_skill_timer(0.1)

    # 40 stamina per second drain
    assert ball.stamina == 76.0

    # Deactivate skill manually
    action._use_skill()
    assert not ball.active_stealth_active

def test_active_stealth_auto_deactivate_on_no_stamina():
    world = MockWorld()
    ball = MockBall(stamina=10.0)
    world.balls.append(ball)
    action = Action(ball, world)

    ball.skill = "active_stealth"
    action._use_skill() # stamina is 10.0, threshold to activate is 20.0
    assert not getattr(ball, "active_stealth_active", False)

    # Give it stamina to activate
    ball.stamina = 50.0
    action._use_skill()
    assert ball.active_stealth_active

    # Update timer drains stamina to 0
    for _ in range(13):
        action._update_skill_timer(0.1)

    assert not ball.active_stealth_active
    assert ball.stamina == 0.0

def test_active_stealth_perception():
    world = MockWorld()
    b1 = MockBall(x=0, y=0, has_thermal_vision=True)

    b2 = MockBall(x=10, y=10, active_stealth_active=True, id="b2")
    b3 = MockBall(x=10, y=10, active_stealth_active=False, id="b3")

    world.balls = [b1, b2, b3]
    perception = Perception(b1, world)

    data = perception.scan()

    enemy_ids = [e.id for e in data["enemies"]]
    assert "b2" not in enemy_ids
    assert "b3" in enemy_ids
