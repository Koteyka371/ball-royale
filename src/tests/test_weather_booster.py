import pytest
from ai.action import Action

class MockArena:
    def __init__(self, weather="clear"):
        self.weather = weather
        self.hazards = []

class MockWorld:
    def __init__(self, arena, boosters=None):
        self.arena = arena
        self.boosters = boosters if boosters else []
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, x=0, y=0, radius=10):
        self.x = x
        self.y = y
        self.radius = radius
        self.team = "team1"
        self.id = 1
        self.alive = True
        self.intangible = False
        self.intangible_timer = 0.0

class MockBooster:
    def __init__(self, kind="weather_booster", x=10, y=10):
        self.kind = kind
        self.x = x
        self.y = y

def test_weather_booster():
    ball = MockBall(0, 0)
    arena = MockArena("clear")
    booster = MockBooster("weather_booster", 10, 10)
    world = MockWorld(arena, [booster])

    action = Action(ball, world)

    # Mocking perception since we want to trigger _collect_booster directly on the booster
    action._get_boosters = lambda: world.boosters
    action._get_enemies = lambda: []
    action._get_allies = lambda: []

    action._collect_booster(0.1)

    # Booster applied
    assert getattr(ball, "weather_booster_applied", False) == True
    assert getattr(ball, "weather_booster_timer", 0.0) == 10.0
    assert getattr(ball, "previous_weather", None) == "clear"

    # Booster collected
    assert booster not in world.boosters
    assert booster not in world.arena.hazards

    # Weather changed
    assert world.arena.weather != "clear" or any(e[0] == "weather_booster" for e in world.events)

    # Wait for timer to expire
    action.execute("idle", 10.0)

    # Weather returned to normal
    assert getattr(ball, "weather_booster_applied", False) == False
    assert getattr(ball, "weather_booster_timer", 0.0) == 0.0
    assert world.arena.weather == "clear"
    assert any(e[0] == "weather_booster_end" for e in world.events)
