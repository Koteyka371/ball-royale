import math
import pytest
from src.ai.action import Action

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.radius = 10.0
        self.hp = 100
        self.speed = 100.0
        self.base_speed = 100.0
        self.vx = 0.0
        self.vy = 0.0

class MockHazard:
    def __init__(self, kind, x, y):
        self.id = 999
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = 15.0
        self.trap_variant = "normal"
        self.owner_id = 998
        self.active = True
        self.duration = 5.0

class MockArena:
    def __init__(self, weather):
        self.weather = weather
        self.hazards = []

    def clamp_position(self, x, y, r):
        return x, y, False

    def update_zone(self, tick, delta):
        pass

class MockWorld:
    def __init__(self, arena):
        self.arena = arena
        self.game_mode = None
        self.events = []
        self.balls = []

def test_trap_weather_variants():
    # Test heatwave
    ball = MockBall(1, 0, 0)
    arena = MockArena("heatwave")
    world = MockWorld(arena)
    world.balls.append(ball)
    hazard = MockHazard("trap", 0, 0)
    arena.hazards.append(hazard)

    action = Action(ball, world)
    action.execute("idle", 0.1)

    assert hazard.kind == "lava_pool", f"Expected lava_pool, got {hazard.kind}"

    # Test rain
    ball = MockBall(1, 0, 0)
    arena = MockArena("rain")
    world = MockWorld(arena)
    world.balls.append(ball)
    hazard = MockHazard("trap", 0, 0)
    arena.hazards.append(hazard)

    action = Action(ball, world)
    action.execute("idle", 0.1)

    assert hazard.kind == "mud_puddle", f"Expected mud_puddle, got {hazard.kind}"

    # Test sandstorm
    ball = MockBall(1, 0, 0)
    arena = MockArena("sandstorm")
    world = MockWorld(arena)
    world.balls.append(ball)
    hazard = MockHazard("trap", 0, 0)
    arena.hazards.append(hazard)

    action = Action(ball, world)
    action.execute("idle", 0.1)

    assert hazard.kind == "quicksand", f"Expected quicksand, got {hazard.kind}"


class MockLeaderboardManager:
    def __init__(self, theme):
        self.data = {"current_season": 2} # Arbitrary
        self.theme = theme

    def get_theme(self, season_num):
        return self.theme

def test_trap_theme_variants():
    # Test Frost Theme
    ball = MockBall(1, 0, 0)
    arena = MockArena("clear") # Weather won't mutate it, theme will
    world = MockWorld(arena)
    world.leaderboard_manager = MockLeaderboardManager("Frost")
    world.balls.append(ball)
    hazard = MockHazard("trap", 0, 0)
    arena.hazards.append(hazard)

    action = Action(ball, world)
    action.execute("idle", 0.1)

    assert hazard.kind == "ice_patch", f"Expected ice_patch (Frost theme), got {hazard.kind}"

    # Test Inferno Theme
    ball = MockBall(1, 0, 0)
    arena = MockArena("clear")
    world = MockWorld(arena)
    world.leaderboard_manager = MockLeaderboardManager("Inferno")
    world.balls.append(ball)
    hazard = MockHazard("trap", 0, 0)
    arena.hazards.append(hazard)

    action = Action(ball, world)
    action.execute("idle", 0.1)

    assert hazard.kind == "lava_pool", f"Expected lava_pool (Inferno theme), got {hazard.kind}"

    # Test Void Theme
    ball = MockBall(1, 0, 0)
    arena = MockArena("clear")
    world = MockWorld(arena)
    world.leaderboard_manager = MockLeaderboardManager("Void")
    world.balls.append(ball)
    hazard = MockHazard("trap", 0, 0)
    arena.hazards.append(hazard)

    action = Action(ball, world)
    action.execute("idle", 0.1)

    assert hazard.kind == "black_hole", f"Expected black_hole (Void theme), got {hazard.kind}"

    # Test Abyssal Theme
    ball = MockBall(1, 0, 0)
    arena = MockArena("clear")
    world = MockWorld(arena)
    world.leaderboard_manager = MockLeaderboardManager("Abyssal")
    world.balls.append(ball)
    hazard = MockHazard("trap", 0, 0)
    arena.hazards.append(hazard)

    action = Action(ball, world)
    action.execute("idle", 0.1)

    assert hazard.kind == "mud_puddle", f"Expected mud_puddle (Abyssal theme), got {hazard.kind}"

if __name__ == "__main__":
    test_trap_theme_variants()
