from ai.action import Action
import pytest

class MockBooster:
    def __init__(self, x=0, y=0, kind="heroism_booster"):
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = 15.0
        self.active = True

class MockArena:
    def __init__(self, hazards):
        self.hazards = hazards

class MockWorld:
    def __init__(self, balls, arena, boosters):
        self.balls = balls
        self.arena = arena
        self.boosters = boosters

class MockBall:
    def __init__(self, id, team, x=0, y=0):
        self.id = id
        self.team = team
        self.x = x
        self.y = y
        self.radius = 15.0
        self.hp = 50.0
        self.max_hp = 100.0
        self.speed = 100.0
        self.vx = 0.0
        self.vy = 0.0
        self.alive = True
        self.ball_type = "test"
        self.emotion = "neutral"
        self.heroism_booster_timer = 0.0
        self.is_glowing = False

def test_heroism_booster_collection():
    ball = MockBall(1, "red", 100, 100)
    booster = MockBooster(105, 100, "heroism_booster")
    world = MockWorld([ball], MockArena([booster]), [booster])

    action = Action(ball, world)
    action._get_boosters = lambda: world.boosters
    action._collect_booster(0.016)

    assert ball.heroism_booster_timer > 0.0
    assert ball.emotion == "heroism"
    assert ball.is_glowing == True
    assert booster not in world.boosters
    assert booster not in world.arena.hazards

def test_heroism_booster_tick():
    ball = MockBall(1, "red", 100, 100)
    world = MockWorld([ball], MockArena([]), [])
    ball.heroism_booster_timer = 5.0
    ball.emotion = "heroism"
    ball.is_glowing = True
    ball.hp = 50.0

    action = Action(ball, world)
    action.execute("idle", 1.0)

    assert ball.hp == 70.0  # 50 + 20*1.0
    assert ball.heroism_booster_timer == 4.0

def test_heroism_booster_expiration():
    ball = MockBall(1, "red", 100, 100)
    world = MockWorld([ball], MockArena([]), [])
    ball.heroism_booster_timer = 0.5
    ball.emotion = "heroism"
    ball.is_glowing = True

    action = Action(ball, world)
    action.execute("idle", 1.0)

    assert ball.heroism_booster_timer == 0.0
    assert ball.emotion == "neutral"
    assert ball.is_glowing == False

def test_heroism_booster_aggro():
    ball = MockBall(1, "red", 0, 0)

    enemy_normal = MockBall(2, "blue", 100, 0)
    enemy_hero = MockBall(3, "blue", 200, 0)
    enemy_hero.emotion = "heroism"

    world = MockWorld([ball, enemy_normal, enemy_hero], MockArena([]), [])
    action = Action(ball, world)

    target = action._get_target([enemy_normal, enemy_hero])
    assert target.id == 3  # Should prioritize hero even if further
