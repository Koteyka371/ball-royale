import sys
sys.path.append("src")
from ai.action import Action

class MockBall:
    def __init__(self):
        self.x = 100
        self.y = 100
        self.id = 1
        self.radius = 10
        self.team = "A"

class MockHazard:
    def __init__(self, x, y, kind, radius=20, damage=10):
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = radius
        self.damage = damage

class MockArena:
    def __init__(self, hazards):
        self.hazards = hazards
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self, balls, arena, boosters):
        self.balls = balls
        self.arena = arena
        self.boosters = boosters
        self.game_mode = None
    def add_event(self, kind, data):
        pass

def test_phase_booster_collect():
    ball = MockBall()
    booster = MockHazard(100, 100, "phase_booster", radius=10, damage=0)
    world = MockWorld([ball], MockArena([booster]), [booster])

    action = Action(ball, world)
    action._get_boosters = lambda: [booster]
    action._collect_booster(0.016)

    assert booster not in world.boosters
    assert booster not in world.arena.hazards
    assert getattr(ball, "phase_booster_timer", 0.0) == 10.0

def test_phase_booster_collide():
    ball = MockBall()
    ball.phase_booster_timer = 5.0
    wall = MockHazard(100, 100, "wall", radius=50, damage=0)
    world = MockWorld([ball], MockArena([wall]), [])

    action = Action(ball, world)

    assert action._clamp_position() is False
    assert action._resolve_collisions() is False

def test_phase_booster_decrement():
    ball = MockBall()
    ball.phase_booster_timer = 1.0
    world = MockWorld([ball], MockArena([]), [])

    action = Action(ball, world)
    action._update_skill_timer(0.5)

    assert ball.phase_booster_timer == 0.5

    action._update_skill_timer(0.6)
    assert ball.phase_booster_timer == 0.0
