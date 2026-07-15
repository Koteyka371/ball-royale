import pytest
from ai.action import Action

class MockArena:
    def __init__(self, hazards=None):
        self.hazards = hazards if hazards is not None else []

class MockWorld:
    def __init__(self, arena, balls):
        self.arena = arena
        self.balls = balls
        self.entities = balls
        self.boosters = arena.hazards # Use hazards as boosters for testing

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
        if self.hp <= 0:
            self.alive = False

def test_fake_flare_action():
    arena = MockArena()
    player = MockBall(1, 100, 100, team="teamA")
    world = MockWorld(arena, [player])

    action = Action(player, world)
    player.skill = "place_fake_flare"
    action.execute("use_skill", 0.1)

    assert len(world.arena.hazards) == 1
    fake_flare = world.arena.hazards[0]
    assert fake_flare.kind == "fake_flare"
    assert fake_flare.x == 100
    assert fake_flare.y == 100
    assert fake_flare.radius == 15.0
    assert fake_flare.owner_id == 1
    assert fake_flare.active == True

def test_fake_flare_knockback():
    class MockFakeFlare:
        def __init__(self, x, y):
            self.kind = "fake_flare"
            self.x = x
            self.y = y
            self.radius = 15.0
            self.damage = 50.0
            self.stun_duration = 2.0
            self.active = True

    arena = MockArena([MockFakeFlare(0, 0)])
    trickster = MockBall(1, 100, 100, team="teamA") # faraway

    enemy = MockBall(2, 5, 0, team="teamB") # close to booster
    enemy.vx = 0
    enemy.vy = 0

    world = MockWorld(arena, [trickster, enemy])
    action = Action(enemy, world)

    action.execute("collect_booster", 0.016)

    assert enemy.hp < 100
    assert enemy.stun_timer > 0
    # verify knockback
    assert enemy.x != 5 or enemy.y != 0
