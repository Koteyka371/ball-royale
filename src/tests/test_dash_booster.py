from ai.action import Action
import math

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
        self.events = []

class MockBall:
    def __init__(self, x=0, y=0, vx=0, vy=0):
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
        self.alive = True
        self.hp = 100
        self.is_stunned = False
        self.stun_timer = 0.0

class MockBooster:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.active = True
        self.radius = 10.0

def test_dash_booster_collection_and_effect():
    ball = MockBall(0, 0, 100, 0)
    enemy = MockBall(10, 0, 0, 0)
    enemy.id = 2
    booster = MockBooster(10, 0, "dash_booster")
    world = MockWorld([ball, enemy], MockArena([booster]), [booster])
    action = Action(ball, world)

    # Force action to see only the booster
    action._get_boosters = lambda: [booster]
    action._get_enemies = lambda: []

    action._collect_booster(0.016)

    # Ball should have dashed forward (vx=100 -> nx=1.0, ny=0.0) -> +300 units
    # Start was 0, 0. Target was 300, 0.
    assert ball.x > 290.0
    assert ball.y == 0.0
    assert ball.vx == 0.0
    assert ball.vy == 0.0

    # Enemy was at 10,0. Dist from start (0,0) is 10. Shockwave radius is 200.
    # Enemy should be stunned.
    assert enemy.is_stunned == True
    assert enemy.stun_timer == 1.5

    # Event should be added
    assert len(world.events) == 1
    assert world.events[0]['type'] == 'visual_effect'
    assert world.events[0]['data']['type'] == 'massive_shockwave'

    # Booster should be consumed
    assert booster not in world.boosters
