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
        self.boosters = arena.hazards

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
        self.vx = 0
        self.vy = 0

def test_dummy_item_placement():
    ball = MockBall(1, 100, 100)
    arena = MockArena()
    world = MockWorld(arena, [ball])

    action = Action(ball, world)
    ball.skill = "place_dummy_item"
    action.execute("use_skill", 0.016)

    assert len(arena.hazards) == 1
    assert arena.hazards[0].kind == "dummy_item"
    assert ball.skill_timer > 0
