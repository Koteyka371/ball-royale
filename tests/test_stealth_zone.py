import pytest
from ai.action import Action

class MockWorld:
    def __init__(self):
        self.balls = []
        self.arena = MockArena()

class MockArena:
    def __init__(self):
        self.hazards = []

class MockHazard:
    def __init__(self, hid, x, y, radius, kind):
        self.id = hid
        self.x = x
        self.y = y
        self.radius = radius
        self.kind = kind
        self.damage = 0

class MockEntity:
    def __init__(self, x, y, btype, alive=True):
        self.x = x
        self.y = y
        self.ball_type = btype
        self.alive = alive
        self.team = btype
        self.is_decoy = False
        self.is_illusion = False
        self.stamina = 100
        self.max_stamina = 100
        self.hp = 100
        self.max_hp = 100
        self.speed = 10
        self.base_speed = 10
        self.is_dashing = False
        self.traits = []

def test_stealth_zone():
    world = MockWorld()
    zone1 = MockHazard(1, 100, 100, 50, "stealth_zone")
    zone2 = MockHazard(2, 300, 300, 50, "stealth_zone")
    world.arena.hazards = [zone1, zone2]

    # my ball in zone 1
    my_ball = MockEntity(100, 100, "warrior")

    # enemy in zone 1
    enemy1 = MockEntity(110, 110, "mage")

    # enemy outside
    enemy2 = MockEntity(200, 200, "mage")

    # enemy in zone 2
    enemy3 = MockEntity(300, 300, "mage")

    world.balls = [my_ball, enemy1, enemy2, enemy3]

    action = Action(my_ball, world)
    enemies = action._get_enemies_internal()

    assert enemy1 in enemies
    assert enemy2 not in enemies
    assert enemy3 not in enemies

    # my ball outside
    my_ball.x, my_ball.y = 200, 200
    enemies2 = action._get_enemies_internal()
    assert enemy1 not in enemies2
    assert enemy2 in enemies2
    assert enemy3 not in enemies2
