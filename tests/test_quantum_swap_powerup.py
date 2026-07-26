import pytest
from ai.action import Action

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.id = 1
        self.radius = 10.0
        self.speed = 100000.0 # Make it fast enough to reach the booster in one tick
        self.alive = True
        self.team = "player"
        self.intangible = False
        self.intangible_timer = 0.0

class MockEnemy:
    def __init__(self, x, y, id_val):
        self.x = x
        self.y = y
        self.id = id_val
        self.alive = True
        self.radius = 10.0
        self.team = "enemy"
        self.stun_timer = 0.0
        self.confusion_timer = 0.0

class MockBooster:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.active = True
        self.radius = 10.0

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.balls = []
        self.boosters = []
        self.arena = MockArena()
        self.events = []

def test_quantum_swap_powerup_logic():
    player = MockBall(0, 0)
    enemy1 = MockEnemy(100, 100, 2)
    enemy2 = MockEnemy(600, 600, 3) # Too far (>500 dist)

    booster = MockBooster(10, 10, "quantum_swap_powerup")

    world = MockWorld()
    world.balls = [player, enemy1, enemy2]
    world.boosters = [booster]
    world.arena.hazards = [booster]

    action = Action(player, world)

    action._get_boosters = lambda: [booster]
    action._get_enemies = lambda: [enemy1, enemy2]

    # Move player directly onto the booster
    player.x = 10
    player.y = 10

    action._collect_booster(0.1)

    assert booster not in world.boosters
    assert player.intangible == True
    assert player.intangible_timer > 0.0

    # One enemy should be swapped to (10, 10), and player swapped to (100, 100)
    assert player.x == 100 and player.y == 100
    assert enemy1.x == 10 and enemy1.y == 10
    assert enemy1.stun_timer > 0.0
    assert enemy1.confusion_timer > 0.0

    # Enemy 2 should be untouched
    assert enemy2.x == 600 and enemy2.y == 600
