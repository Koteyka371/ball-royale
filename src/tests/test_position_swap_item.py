import pytest
from ai.action import Action

class MockArena:
    def __init__(self, hazards):
        self.hazards = hazards
        self.width = 1000
        self.height = 1000

    def is_point_inside(self, x, y):
        return True

class MockWorld:
    def __init__(self, balls, arena, boosters=None):
        self.balls = balls
        self.entities = balls
        self.arena = arena
        self.boosters = boosters if boosters is not None else []
        self.events = []

    def add_event(self, type, data):
        self.events.append((type, data))

class MockBall:
    def __init__(self, id, x, y, team, inventory=None):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.radius = 10
        self.alive = True
        self.is_decoy = False
        self.team = team
        self.hp = 100
        self.max_hp = 100
        self.inventory = inventory if inventory is not None else []
        self.ball_type = "mock"

    def take_damage(self, amount):
        self.hp -= amount

class MockBooster:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = 10

def test_position_swap_collect():
    booster = MockBooster(10, 10, "position_swap_item")
    ball = MockBall(1, 10, 10, "team1")
    world = MockWorld([ball], MockArena([]), boosters=[booster])
    action = Action(ball, world)

    action._get_boosters = lambda: world.boosters
    action.execute("collect_booster", 0.1)

    assert "position_swap" in ball.inventory
    assert booster not in world.boosters

def test_position_swap_use():
    ball1 = MockBall(1, 10, 10, "team1", inventory=["position_swap"])
    ball2 = MockBall(2, 50, 50, "team2")
    world = MockWorld([ball1, ball2], MockArena([]))
    action = Action(ball1, world)

    action.execute("attack", 0.1)

    assert "position_swap" not in ball1.inventory
    assert abs(ball1.x - 50) < 5
    assert abs(ball1.y - 50) < 5
    assert ball2.x == 10
    assert ball2.y == 10
    assert ball2.hp == 95
    assert getattr(ball2, "slow_timer", 0) > 0

