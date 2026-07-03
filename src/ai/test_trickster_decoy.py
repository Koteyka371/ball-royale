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
