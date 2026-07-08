import pytest
import math
from ai.action import Action

class MockArena:
    def __init__(self):
        self.items = []
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.boosters = []
        self.tick = 0
        self.width = 1000
        self.height = 1000

    def get_nearby_entities(self, ball, radius):
        return {"enemies": [], "allies": []}

class MockBall:
    def __init__(self):
        self.id = 1
        self.x = 500.0
        self.y = 500.0
        self.radius = 10.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.team = "A"
        self.speed = 0.0
        self.damage = 10.0
        self.base_damage = 10.0
        self._base_speed_set = True
        self.material_magnet_timer = 10.0

class MockHazard:
    def __init__(self, kind, x, y, radius):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = radius

def test_material_magnet_booster_effect():
    world = MockWorld()
    ball = MockBall()
    world.balls.append(ball)
    action = Action(ball, world)

    # 1. Test pulling items
    mat1 = {"id": "mat_1", "x": 600.0, "y": 500.0, "kind": "material", "radius": 15.0}
    world.arena.items.append(mat1)

    mat2 = {"id": "mat_2", "x": 400.0, "y": 500.0, "kind": "material", "radius": 15.0}
    world.arena.items.append(mat2)

    not_mat = {"id": "not_mat", "x": 500.0, "y": 600.0, "kind": "something_else", "radius": 15.0}
    world.arena.items.append(not_mat)

    action._update_skill_timer(0.1)

    # distance is 100, ball is at 500
    # mat1 moves towards 500. nx = (500 - 600)/100 = -1. pull = 200 * 0.1 = 20
    # mat1.x should be 600 - 20 = 580
    assert abs(mat1["x"] - 580.0) < 0.1

    # mat2 moves towards 500. nx = (500 - 400)/100 = 1. pull = 20
    # mat2.x should be 400 + 20 = 420
    assert abs(mat2["x"] - 420.0) < 0.1

    # not_mat should not move
    assert not_mat["y"] == 600.0

    # material_magnet_timer should decrease
    assert abs(ball.material_magnet_timer - 9.9) < 0.01

def test_material_magnet_booster_collection():
    world = MockWorld()
    ball = MockBall()
    ball.material_magnet_timer = 0.0
    world.balls.append(ball)
    action = Action(ball, world)

    # Override get_nearby_entities for collection
    def mock_get_boosters():
        return world.boosters
    action._get_boosters = mock_get_boosters

    booster = MockHazard("material_magnet_booster", 500.0, 500.0, 15.0)
    world.boosters.append(booster)

    # Execute collect booster
    action._collect_booster(0.1)

    assert ball.material_magnet_timer == 10.0
    assert len(world.boosters) == 0
