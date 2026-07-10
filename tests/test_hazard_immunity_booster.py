import pytest
import math

class MockEntity:
    def __init__(self, id=None, x=0.0, y=0.0, kind=""):
        self.id = id
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = 15.0

class MockArena:
    def __init__(self, hazards=None):
        self.hazards = hazards if hazards is not None else []
        self.safe_zone_radius = float('inf')
        self.safe_zone_center = (0, 0)
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self, arena, balls, boosters=None):
        self.arena = arena
        self.balls = balls
        self.boosters = boosters if boosters is not None else []
        self.tick = 0
        self.events = []

    def _deal_damage(self, attacker, victim, amount):
        if hasattr(victim, "take_damage"):
            victim.take_damage(amount)

    def get_nearby_entities(self, ball, radius):
        return {"balls": self.balls, "boosters": self.boosters, "enemies": [b for b in self.balls if b != ball], "allies": []}

class MockBall(MockEntity):
    def __init__(self, id=1, x=100.0, y=100.0, hp=100.0):
        super().__init__(id, x, y)
        self.hp = hp
        self.alive = True
        self.team = "teamA"
        self.ball_type = "brawler"
        self.radius = 10.0
        self.speed = 100.0
        self.base_speed = 100.0

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False

def test_hazard_immunity_booster_collection():
    from action import Action
    ball = MockBall()
    booster = MockEntity(2, 100.1, 100.1, kind="hazard_immunity_booster")
    arena = MockArena(hazards=[booster])
    world = MockWorld(arena, [ball], boosters=[booster])

    action = Action(ball.id, world)
    action.ball = ball

    # Run a tick to collect the booster
    action.execute("collect booster", 0.1)

    # Booster should be removed
    assert booster not in world.boosters
    assert booster not in arena.hazards

    # Ball should have immunity timer set (15.0 - delta which is 0.1)
    assert getattr(ball, "hazard_immunity_timer", 0.0) == 14.9

def test_hazard_immunity_prevents_damage():
    from action import Action
    ball = MockBall(x=100, y=100, hp=100)
    ball.hazard_immunity_timer = 10.0

    # Damage hazard
    spikes = MockEntity(3, 100, 100, kind="spikes")
    spikes.radius = 20.0
    spikes.damage = 50.0

    arena = MockArena(hazards=[spikes])
    world = MockWorld(arena, [ball])

    action = Action(ball.id, world)
    action.ball = ball

    action.execute("idle", 1.0)

    # HP should remain 100
    assert ball.hp == 100.0

    # Verify ball attacks still work
    ball.take_damage(20)
    assert ball.hp == 80.0
