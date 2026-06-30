import pytest
from ai.action import Action
from ai.perception import Perception
from ai.ball_types_spotter import Spotter

class MockEntity:
    def __init__(self, id, x, y, kind="enemy"):
        self.id = id
        self.x = x
        self.y = y
        self.kind = kind
        self.team = "bad"
        self.hp = 100
        self.max_hp = 100
        self.has_stealth_drone = False
        self.shadow_booster_timer = 0.0

    def has_method(self, name):
        return False

class MockHazard:
    def __init__(self, id, x, y, radius, kind):
        self.id = id
        self.x = x
        self.y = y
        self.radius = radius
        self.kind = kind
        self.active = True

class MockArena:
    def __init__(self):
        self.hazards = []
        self.is_night = False
        self.is_foggy = False
        self.is_raining = False

    def is_point_inside(self, x, y, r):
        return True

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.entities = []

def test_spotter_flare_action():
    spotter = Spotter(1, 0, 0)
    world = MockWorld()

    enemy = MockEntity(2, 100, 100)
    world.balls.append(spotter)
    world.balls.append(enemy)
    world.entities = world.balls

    action = Action(spotter, world)
    action._get_enemies = lambda: [enemy]

    action.execute("use_skill", 0.1)

    assert len(world.arena.hazards) == 1
    flare = world.arena.hazards[0]
    assert flare.kind == "flare"
    assert flare.x == 100
    assert flare.y == 100
    assert getattr(flare, 'duration', 0) == 5.0
