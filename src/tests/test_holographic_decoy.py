import math
from ai.action import Action
from ai.game_modes import GAME_MODES

class MockBooster:
    def __init__(self, kind, x, y):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = 10

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 5000
        self.height = 5000
        self.safe_zone_center = (500, 500)
        self.safe_zone_radius = 5000

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.team = "blue"
        self.speed = 100.0
        self.hp = 100
        self.max_hp = 100
        self.damage = 10
        self.alive = True
        self.radius = 10

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []
        self.balls = []
        self.events = []
        self.next_id = 9999

def test_holographic_decoy_module():
    world = MockWorld()
    b = MockBooster("holographic_decoy_module", 100, 100)
    world.boosters.append(b)

    ball = MockBall(1, 100, 100)
    world.balls.append(ball)

    action = Action(ball, world)
    action._get_boosters = lambda: [b]
    action._collect_booster(0.016)

    assert getattr(ball, "holographic_decoy_timer", 0.0) > 0

    # Wait for the clone to spawn
    ball.holographic_decoy_spawn_timer = 0
    action.execute("idle", 0.1)

    clones = [b for b in world.balls if getattr(b, "is_holographic_clone", False)]
    assert len(clones) == 1

    clone = clones[0]
    assert clone.hp == 1.0
    assert clone.damage == 0.0

    # Check if they mimic attacks
    action2 = Action(clone, world)
    action2.execute("attack", 0.1)

    assert getattr(clone, "mimic_attack", False) == True


def test_holographic_decoy_explosion():
    world = MockWorld()
    b = MockBooster("holographic_decoy_module", 100, 100)
    world.boosters.append(b)

    ball = MockBall(1, 100, 100)
    enemy = MockBall(2, 120, 120)
    enemy.team = "red"

    world.balls.append(ball)
    world.balls.append(enemy)

    action = Action(ball, world)
    action._get_boosters = lambda: [b]
    action._collect_booster(0.016)

    # Wait for the clone to spawn
    ball.holographic_decoy_spawn_timer = 0
    action.execute("idle", 0.1)

    clones = [c for c in world.balls if getattr(c, "is_holographic_clone", False)]
    clone = clones[0]

    # Damage clone
    clone.hp = 0

    # Check explosion blind effect
    action2 = Action(clone, world)
    action2.execute("idle", 0.1)

    assert getattr(enemy, "is_blinded", False) == True
    assert getattr(enemy, "confusion_timer", 0.0) > 0
