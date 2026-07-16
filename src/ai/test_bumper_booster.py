import pytest
from ai.action import Action
import math

class MockEntity:
    def __init__(self, id, x, y, kind=None, ball_type=None):
        self.id = id
        self.x = x
        self.y = y
        self.kind = kind
        self.ball_type = ball_type
        self.radius = 15.0
        self.active = True

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []
        self.balls = []

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.radius = 15.0
        self.team = "A"
        self.ball_type = "normal"
        self.alive = True

def test_collect_bumper_booster():
    world = MockWorld()
    ball = MockBall(1, 100.0, 100.0)

    booster = MockEntity(id=99, x=105.0, y=100.0, kind="bumper_booster", ball_type="booster")
    world.boosters = [booster]
    world.arena.hazards = [booster]

    action = Action(ball, world)

    # Fake perception to see booster
    def mock_get_boosters():
        return world.boosters
    action._get_boosters = mock_get_boosters

    # Execute collection
    action.execute("collect_booster", 1.0)

    # Assert timer is set
    assert getattr(ball, "bumper_booster_timer", 0.0) > 0.0

    # Assert booster removed
    assert len(world.boosters) == 0
    assert len(world.arena.hazards) == 0

def test_bumper_booster_aura():
    world = MockWorld()
    ball = MockBall(1, 100.0, 100.0)
    ball.bumper_booster_timer = 5.0

    enemy = MockBall(2, 120.0, 100.0)
    enemy.team = "B"
    enemy.vx = 0.0
    enemy.vy = 0.0

    world.balls = [ball, enemy]

    action = Action(ball, world)

    # Enemy is at 20 units away.
    # Aura radius is b_rad(15) + other_rad(15) + 10 = 40.
    # Since 20 < 40, they should be bumped.
    action._update_skill_timer(1.0)

    # Timer decrements
    assert ball.bumper_booster_timer < 5.0

    # Enemy should be bumped
    # nx = 1.0, ny = 0.0 (roughly, depends on random angle)
    # We can at least assert vx and vy are set to ~2000 in magnitude and x position changed
    assert getattr(enemy, "vx", 0.0) != 0.0 or getattr(enemy, "vy", 0.0) != 0.0
    assert enemy.x != 120.0

def test_bumper_booster_aura_out_of_range():
    world = MockWorld()
    ball = MockBall(1, 100.0, 100.0)
    ball.bumper_booster_timer = 5.0

    enemy = MockBall(2, 200.0, 100.0) # 100 units away, out of range
    enemy.team = "B"
    enemy.vx = 0.0
    enemy.vy = 0.0

    world.balls = [ball, enemy]

    action = Action(ball, world)
    action._update_skill_timer(1.0)

    # Should not be bumped
    assert enemy.x == 200.0
    assert getattr(enemy, "vx", 0.0) == 0.0
    assert getattr(enemy, "vy", 0.0) == 0.0

def test_bumper_booster_void_immunity():
    world = MockWorld()
    ball = MockBall(1, 100.0, 100.0)
    ball.bumper_booster_timer = 5.0

    # Put a void panel under the ball
    void_panel = MockEntity(id=99, x=100.0, y=100.0, kind="void_panel", ball_type="hazard")
    world.arena.hazards = [void_panel]

    action = Action(ball, world)

    action._idle = lambda d: None
    action._chase = lambda d: None
    action._attack = lambda d: None
    action._process_physics = lambda delta: None

    action.execute("idle", 0.1)

    assert ball.alive == True
