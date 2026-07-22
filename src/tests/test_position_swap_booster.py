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

def test_position_swap_booster_collect():
    booster = MockBooster(10, 10, "position_swap_booster")
    ball1 = MockBall(1, 10, 10, "team1")
    ball2 = MockBall(2, 50, 50, "team2") # dist 3200
    ball3 = MockBall(3, 100, 100, "team2") # dist 16200 -> furthest
    world = MockWorld([ball1, ball2, ball3], MockArena([booster]), boosters=[booster])
    action = Action(ball1, world)

    action._get_boosters = lambda: world.boosters
    action.execute("collect_booster", 0.1)

    # Should swap with ball3 (furthest enemy)
    assert booster not in world.boosters
    assert booster not in world.arena.hazards

    # Assert locations swapped
    assert abs(ball1.x - 100) < 5
    assert abs(ball1.y - 100) < 5
    assert ball3.x == 10
    assert ball3.y == 10

    # ball2 stays unchanged
    assert ball2.x == 50
    assert ball2.y == 50
