import pytest
from arena.arena_types import DynamicWeatherArena
from ai.perception import Perception

class DummyWorld:
    def __init__(self, arena):
        self.arena = arena
        self.coach_strategy = None
    def get_nearby_entities(self, ball, radius):
        return {"enemies": [], "allies": [], "boosters": [], "traps": []}

class DummyBall:
    def __init__(self):
        self.perception_radius = 500.0

def test_dynamic_weather_arena_cycles():
    arena = DynamicWeatherArena()

    assert arena.is_foggy == False
    assert arena.is_raining == False
    assert arena.is_snowing == False

    # After 10s: Foggy
    arena.update_zone(0, 10.0)
    assert arena.is_foggy == True
    assert arena.is_raining == False
    assert arena.is_snowing == False

    # After 10s more: Raining
    arena.update_zone(0, 10.0)
    assert arena.is_foggy == False
    assert arena.is_raining == True
    assert arena.is_snowing == False

    # After 10s more: Snowing
    arena.update_zone(0, 10.0)
    assert arena.is_foggy == False
    assert arena.is_raining == False
    assert arena.is_snowing == True

    # After 10s more: Clear
    arena.update_zone(0, 10.0)
    assert arena.is_foggy == False
    assert arena.is_raining == False
    assert arena.is_snowing == False

def test_snow_perception_reduction():
    arena = DynamicWeatherArena()

    # Fast forward to snow
    arena.update_zone(0, 10.0)
    arena.update_zone(0, 10.0)
    arena.update_zone(0, 10.0)
    assert arena.is_snowing == True

    ball = DummyBall()
    world = DummyWorld(arena)
    p = Perception(ball, world)

    passed_radius = []
    def mock_get(b, r):
        passed_radius.append(r)
        return {"enemies": [], "allies": [], "boosters": [], "traps": []}
    world.get_nearby_entities = mock_get

    p.scan()
    assert passed_radius[0] == 500.0 * 0.6
