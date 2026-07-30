import pytest
from ai.action import Action

class MockBall:
    def __init__(self, x=0, y=0, vx=0, vy=0, team='A'):
        self.id = 1
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = 10.0
        self.stamina = 100.0
        self.max_stamina = 100.0
        self.intangible = False
        self.intangible_timer = 0.0
        self.base_speed = 100.0
        self.base_damage = 10.0
        self.speed_multiplier = 1.0
        self.damage_multiplier = 1.0
        self._base_speed_set = True
        self.team = team
        self.alive = True

class MockBooster:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.active = True
        self.radius = 15.0

class MockArena:
    def __init__(self, hazards):
        self.hazards = hazards
        self.safe_zone_center = (0, 0)
        self.safe_zone_radius = 500.0

class MockWorld:
    def __init__(self, balls, arena, boosters):
        self.balls = balls
        self.arena = arena
        self.boosters = boosters

def test_gravity_well_booster_collection():
    ball = MockBall(0, 0, 0, 0)
    booster = MockBooster(10, 0, "gravity_well_booster")
    world = MockWorld([ball], MockArena([booster]), [booster])
    action = Action(ball, world)

    # Make the AI see the booster
    action._get_boosters = lambda: [booster]
    action._get_enemies = lambda: []

    action._collect_booster(0.016)

    assert getattr(ball, "gravity_well_booster_timer", 0.0) == 5.0
    assert booster not in world.boosters
    assert booster not in world.arena.hazards
    assert not booster.active

def test_gravity_well_pull_logic():
    ball = MockBall(0, 0, 0, 0, 'A')
    ball.gravity_well_booster_timer = 5.0

    enemy = MockBall(100, 0, 0, 0, 'B')
    enemy.id = 2

    hazard = MockBooster(0, 100, "mine")
    hazard.vx = 0
    hazard.vy = 0

    world = MockWorld([ball, enemy], MockArena([hazard]), [])
    action = Action(ball, world)

    # Just run execute, it will decrease timer and apply pull
    action.execute("idle", 1.0) # delta = 1.0

    assert ball.gravity_well_booster_timer == 4.0

    # Enemy is at (100, 0). dx = -100, dy = 0. dist = 100.
    # pull_radius = 200. pull_force = 300.
    # f = 300 * (1 - 100/200) = 150.
    # vx += (-100/100) * 150 = -150
    assert enemy.vx < 0
    assert enemy.vy == 0

    # Hazard is at (0, 100). dx = 0, dy = -100. dist = 100.
    # f = 150.
    # vy += (-100/100) * 150 = -150
    assert hazard.vx == 0
    assert getattr(hazard, 'vy', 0) < 0
