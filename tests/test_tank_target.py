import sys
sys.path.insert(0, 'src')
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
    def __init__(self, enemies):
        self.enemies = enemies
        self.width = 1000
        self.height = 1000

    def get_nearby_entities(self, ball, radius):
        return {"enemies": self.enemies, "allies": []}

    def _deal_damage(self, attacker, target):
        pass

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
