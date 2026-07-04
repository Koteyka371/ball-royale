import pytest
from ai.action import Action
from ai.ball_types_trickster import Trickster

class MockArena:
    def __init__(self, hazards=None):
        self.hazards = hazards if hazards is not None else []

class MockWorld:
    def __init__(self, arena, balls):
        self.arena = arena
        self.balls = balls
        self.entities = balls
        # Need to put booster in world.hazards / world.boosters
        self.boosters = arena.hazards # using hazards as boosters list for get_boosters

class MockBall:
    def __init__(self, id, x, y, team=""):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.hp = 100
        self.max_hp = 100
        self.alive = True
        self.stun_timer = 0
        self.radius = 10.0
        self.inventory = []
        self.speed = 10.0

    def take_damage(self, dmg):
        self.hp -= dmg

def test_fake_booster_knockback():
    class MockFakeBooster:
        def __init__(self, x, y):
            self.kind = "fake_booster"
            self.x = x
            self.y = y
            self.radius = 15.0
            self.damage = 50.0
            self.stun_duration = 2.0
            self.active = True

    arena = MockArena([MockFakeBooster(0, 0)])
    trickster = Trickster(1, 100, 100) # faraway
    trickster.team = "teamA"

    enemy = MockBall(2, 5, 0, team="teamB") # close to booster
    enemy.vx = 0
    enemy.vy = 0

    world = MockWorld(arena, [trickster, enemy])
    action = Action(enemy, world)

    # Need to simulate collect_booster to make it pick it up
    action.execute("collect_booster", 0.016)

    assert enemy.hp < 100
    assert enemy.stun_timer > 0
    # verify knockback
    assert enemy.x != 5 or enemy.y != 0

def test_trickster_decoy_mirroring():
    # Test that the decoy perfectly mirrors the Trickster's movements in the opposite direction
    owner = Trickster(1, 100, 100)
    owner.id = 1
    owner.team = "teamA"
    owner.prev_x = 90
    owner.prev_y = 110 # Owner moved dx=10, dy=-10

    decoy = MockBall(99, 150, 150)
    decoy.owner_id = 1
    decoy.is_decoy = True
    decoy.decoy_timer = 5.0
    decoy.is_mirroring = True

    arena = MockArena()
    world = MockWorld(arena, [owner, decoy])

    action = Action(decoy, world)

    action.execute("idle", 0.1)

    # Initial distance check
    # dx = 10, dy = -10
    # Decoy should move -10 in x and +10 in y ?
    # Let's verify the exact positions
    # owner moved to (100, 100) from (90, 110)
    # the mirror logic in action.py sets:
    # mirror_center_x = (owner.x + decoy.x)/2
    # mirror_center_y = (owner.y + decoy.y)/2
    # decoy.x = mirror_center_x - (owner.x - mirror_center_x)
    # decoy.y = mirror_center_y - (owner.y - mirror_center_y)

    # Wait, the mirror center is calculated on the first tick!
    # So on tick 1, mirror_center_x = (100 + 150)/2 = 125
    # mirror_center_y = (100 + 150)/2 = 125
    # decoy.x = 125 - (100 - 125) = 150
    # decoy.y = 125 - (100 - 125) = 150
    # Next tick, owner moves to 110, 90.
    owner.x = 110
    owner.y = 90
    action.execute("idle", 0.1)

    assert abs(decoy.x - (125 - (110 - 125))) < 5.0 # 140
    assert abs(decoy.y - (125 - (90 - 125))) < 5.0 # 160
