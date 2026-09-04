import pytest
from ai.action import Action

class DummyBall:
    def __init__(self, x=500, y=500, hp=100.0, cosmetic="", inventory=None):
        self.x = x
        self.y = y
        self.hp = hp
        self.cosmetic = cosmetic
        self.inventory = inventory if inventory is not None else []
        self.stamina = 100.0
        self.vx = 0.0
        self.vy = 0.0
        self.ball_type = "default"
        self.max_stamina = 100.0
        self.is_exhausted = False

class DummyArena:
    def __init__(self):
        self.is_heatwave = True
        self.is_windy = False
        self.is_snowing = False
        self.is_foggy = False
        self.shadow_areas = [{"x": 100, "y": 100, "radius": 50}]
        self.temperature = 20.0
        self.wind_dx = 0.0
        self.wind_dy = 0.0
        self.weather = "heatwave"

class DummyWorld:
    def __init__(self, arena):
        self.arena = arena
        self.game_mode = None

def test_sunburn_outside_shadow():
    ball = DummyBall(x=500, y=500, hp=100.0)
    arena = DummyArena()
    world = DummyWorld(arena)
    action = Action(ball, world)

    action.execute("idle", 1.0)
    assert ball.hp == 98.0

def test_no_sunburn_inside_shadow():
    ball = DummyBall(x=100, y=100, hp=100.0)
    arena = DummyArena()
    world = DummyWorld(arena)
    action = Action(ball, world)

    action.execute("idle", 1.0)
    assert ball.hp == 100.0

def test_no_sunburn_with_thermal_boots():
    ball = DummyBall(x=500, y=500, hp=100.0, inventory=["thermal_boots"])
    arena = DummyArena()
    world = DummyWorld(arena)
    action = Action(ball, world)

    action.execute("idle", 1.0)
    assert ball.hp == 100.0

def test_no_sunburn_with_cooling_cosmetic():
    ball = DummyBall(x=500, y=500, hp=100.0, cosmetic="cooling_fan")
    arena = DummyArena()
    world = DummyWorld(arena)
    action = Action(ball, world)

    action.execute("idle", 1.0)
    assert ball.hp == 100.0
