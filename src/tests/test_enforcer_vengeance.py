from ai.action import Action
from system.profile import ProfileManager

class MockBall:
    def __init__(self, ball_type):
        self.ball_type = ball_type
        self.hp = 100.0
        self.max_hp = 100.0
        self.damage = 10.0
        self.speed = 2.0
        self.vx = 0.0
        self.vy = 0.0
        self.perception_radius = 250.0
        self.alive = True
        self.active = True
        self.enforcer_vengeance_stacks = 0
        self.enforcer_aura_timer = 0.0
        self.x = 0
        self.y = 0

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False

class MockWorld:
    def __init__(self):
        self.profile_manager = ProfileManager()
        self.events = []
        self.arena = None

    def _deal_damage(self, attacker, target, damage=None):
        if damage is None:
            damage = attacker.damage
        target.take_damage(damage)

def test_enforcer_vengeance():
    world = MockWorld()
    pm = world.profile_manager
    pm.data["nemeses"] = {"Villain": {"Hero": 2}}
    pm.data["enforcers"] = {"EnforcerBall": "Hero"}
    pm.save()

    action = Action(MockBall("EnforcerBall"), world)
    attacker = action.ball
    attacker.damage = 100.0 # One shot
    target = MockBall("Villain")
    target.hp = 10

    action._attempt_damage(attacker, target)
    assert attacker.enforcer_vengeance_stacks == 1
    assert attacker.enforcer_aura_timer == 7.0 # 5.0 + 2.0

    assert len(world.events) > 0
    assert world.events[-1]["type"] == "visual_effect"
    assert world.events[-1]["data"]["type"] == "enforcer_aura"
    assert world.events[-1]["data"]["stacks"] == 1
