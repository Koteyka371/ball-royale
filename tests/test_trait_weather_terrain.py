import pytest
from ai.action import Action

class MockBall:
    def __init__(self, x=0, y=0, traits=None):
        self.id = 1
        self.x = x
        self.y = y
        self.traits = traits or []
        self.speed_multiplier = 1.0
        self.damage_multiplier = 1.0
        self.defense_multiplier = 1.0
        self.immune_to_sandstorm = False
        self.speed = 10.0
        self.base_speed = 10.0
        self.alive = True
        self.team = "A"
        self.current_action = "wander"

    def __getattr__(self, name):
        if name in ["suspended_projectiles", "inventory"]: return []
        if name in ["action_timer", "base_damage"]: return 0
        raise AttributeError(f"MockBall has no attribute '{name}'")

class MockArena:
    def __init__(self, weather="", terrain=""):
        self.weather = weather
        self.terrain = terrain
        self.hazards = []
        self.width = 1000
        self.height = 1000
        self.friction = 0.99

    def clamp_position(self, x, y, r):
        return x, y, False

class MockGameMode:
    def __init__(self, weather="", name=""):
        self.weather = weather
        self.name = name

class MockWorld:
    def __init__(self, game_mode=None, arena=None):
        self.game_mode = game_mode
        self.arena = arena
        self.boosters = []
        self.balls = []
        self.time = 0

    def get_nearby_entities(self, b, r):
        return {"boosters": [], "hazards": [], "enemies": []}

def test_fire_trait_heatwave():
    ball = MockBall(traits=["fire"])
    gm = MockGameMode(weather="heatwave")
    world = MockWorld(game_mode=gm)
    act = Action(ball, world)

    try:
        act.execute("wander", 1.0)
    except Exception:
        pass

    assert ball.speed_multiplier == 1.5
    assert ball.damage_multiplier == 1.5

def test_fire_trait_blizzard():
    ball = MockBall(traits=["fire"])
    gm = MockGameMode(weather="blizzard")
    world = MockWorld(game_mode=gm)
    act = Action(ball, world)

    try:
        act.execute("wander", 1.0)
    except Exception:
        pass

    assert ball.speed_multiplier == 0.5
    assert ball.damage_multiplier == 0.5

def test_earth_trait_dirt_sandstorm():
    ball = MockBall(traits=["earth"])
    arena = MockArena(weather="sandstorm", terrain="dirt")
    world = MockWorld(arena=arena)
    act = Action(ball, world)

    try:
        act.execute("wander", 1.0)
    except Exception:
        pass

    assert ball.defense_multiplier == 1.5
    assert ball.immune_to_sandstorm == True
