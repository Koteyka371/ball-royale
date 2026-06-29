import sys
sys.path.insert(0, 'src')
from ai.decision import Decision
from ai.action import Action
from ai.ball_types_tank import Tank

class MockEnemy:
    def __init__(self, hp, max_hp, x, y):
        self.hp = hp
        self.max_hp = max_hp
        self.x = x
        self.y = y
        self.radius = 10
        self.alive = True
        self.ball_type = "enemy"

class MockWorld:
    def __init__(self, enemies, allies=None):
        if allies is None:
            allies = []
        self.enemies = enemies
        self.allies = allies
        self.width = 1000
        self.height = 1000

    def get_nearby_entities(self, ball, radius):
        return {"enemies": self.enemies, "allies": self.allies}

    def _deal_damage(self, attacker, target):
        pass

class MockAlly:
    def __init__(self, ball_type, hp, max_hp, x, y):
        self.ball_type = ball_type
        self.hp = hp
        self.max_hp = max_hp
        self.x = x
        self.y = y
        self.radius = 10
        self.alive = True

def test_tank_target_strong_attack():
    tank = Tank(1, 0, 0)
    tank.speed = 10
    tank.x = 100
    tank.y = 100
    tank.attack_timer = 0
    weak_enemy = MockEnemy(10, 10, 200, 100)
    strong_enemy = MockEnemy(100, 100, 0, 100)
    world = MockWorld([weak_enemy, strong_enemy])

    action = Action(tank, world)
    action.execute("attack", 1.0)

    # Tank should move toward strong_enemy (0, 100)
    assert tank.x < 100, f"Tank x={tank.x}, expected < 100. It moved toward weak enemy."
    assert tank.x == 10.0, f"Tank x={tank.x}, expected 10.0"

def test_tank_target_strong_chase():
    tank = Tank(1, 0, 0)
    tank.speed = 10
    tank.x = 100
    tank.y = 100
    tank.attack_timer = 0
    weak_enemy = MockEnemy(10, 10, 200, 100)
    strong_enemy = MockEnemy(100, 100, 0, 100)
    world = MockWorld([weak_enemy, strong_enemy])

    action = Action(tank, world)
    action.execute("chase", 1.0)

    assert tank.x < 100, f"Tank x={tank.x}, expected < 100. It moved toward weak enemy."

def test_tank_target_strong_defend():
    tank = Tank(1, 0, 0)
    tank.speed = 10
    tank.x = 100
    tank.y = 100
    tank.attack_timer = 0
    tank.personality = "tank"
    weak_enemy = MockEnemy(10, 10, 200, 100)
    strong_enemy = MockEnemy(100, 100, 0, 100)
    world = MockWorld([weak_enemy, strong_enemy])

    action = Action(tank, world)
    action.execute("defend", 1.0)

    assert tank.x < 100, f"Tank x={tank.x}, expected < 100. It moved toward weak enemy."

def test_tank_body_blocks_healer():
    tank = Tank(1, 0, 0)
    tank.speed = 10
    tank.x = 100
    tank.y = 100
    tank.attack_timer = 0
    tank.personality = "tank"

    # Enemy is far right
    enemy = MockEnemy(100, 100, 300, 100)
    # Healer is somewhat close right
    healer = MockAlly("healer", 100, 100, 150, 100)

    world = MockWorld([enemy], [healer])
    action = Action(tank, world)

    # Exectue defend
    action.execute("defend", 1.0)

    # With body blocking, target_pos_x should be ax + (dx_ea/dist_ea) * min(30, dist_ea*0.5)
    # ax = 150, dx_ea = 300-150 = 150. target_pos_x = 150 + 1 * 30 = 180.
    # Tank starts at 100. Should move right towards 180.
    assert tank.x > 100, f"Tank did not move towards body-blocking pos. x={tank.x}"





def test_tank_uses_target_strong_when_damaged():
    tank = Tank(1, 0, 0)
    tank.hp = 150  # Max is 200
    tank.skill_timer = 0
    tank.first_hit_taken = True
    tank.personality = "tank"
    tank.skill_timer = -1.0

    enemy = MockEnemy(100, 100, 300, 100)
    world = MockWorld([enemy])
    decision = Decision(tank, world)

    perception_data = {
        "danger_level": 0.6,
        "threat_level": 0.5,
        "opportunity_level": 0.0,
        "opportunity_score": 0.0,
        "enemies": [enemy],
        "allies": [],
        "boosters": [],
        "team_messages": []
    }

    action = decision.choose_action(perception_data, "calm")
    assert action in ["use_skill", "defend"]
