import pytest
from ai.action import Action

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []

class MockArena:
    def __init__(self):
        self.hazards = []

class MockBall:
    def __init__(self, x=0.0, y=0.0):
        self.id = 1
        self.x = x
        self.y = y
        self.skill = "deploy_fake_booster"
        self.skill_timer = 0.0
        self.skill_cooldown = 5.0
        self.stun_timer = 0.0
        self.hp = 100.0
        self.SKILL_COOLDOWN = 5.0
        self.max_hp = 100.0
        self.base_speed = 5.0
        self._base_speed_set = True

    def take_damage(self, amount):
        self.hp -= amount

class MockEntity:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.damage = 50.0
        self.radius = 15.0
        self.owner_id = 99

def test_deploy_fake_booster():
    ball = MockBall()
    world = MockWorld()
    action = Action(ball, world)

    # action.execute decreases skill_timer by delta (0.1), so we execute with 0 or expect 4.9
    action.execute("use_skill", 0.0)

    assert len(world.arena.hazards) == 1
    assert world.arena.hazards[0].kind == "fake_booster"
    assert ball.skill_timer == 5.0

def test_collect_fake_booster():
    ball = MockBall(0.0, 0.0)
    world = MockWorld()
    fake_booster = MockEntity(0.0, 0.0, "fake_booster")
    world.arena.hazards.append(fake_booster)

    action = Action(ball, world)
    action.perception_data = {"boosters": [fake_booster], "enemies": [], "traps": []}

    action._get_boosters = lambda: [fake_booster]

    action.execute("collect_booster", 0.1)

    assert ball.hp == 50.0
    assert ball.stun_timer == 2.0
    assert len(world.arena.hazards) == 0
