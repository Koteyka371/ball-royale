from arena.arena_types import ThickFogArena
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

def test_thick_fog_toggles_and_reduces_perception():
    arena = ThickFogArena()
    assert not arena.is_foggy

    arena.update_zone(0, 10.0)
    assert not arena.is_foggy

    arena.update_zone(0, 11.0) # > 20
    assert arena.is_foggy

    ball = DummyBall()
    world = DummyWorld(arena)
    p = Perception(ball, world)

    passed_radius = []
    def mock_get(b, r):
        passed_radius.append(r)
        return {"enemies": [], "allies": [], "boosters": [], "traps": []}
    world.get_nearby_entities = mock_get

    p.scan()
    assert passed_radius[0] <= 80.0

def test_fog_off():
    arena = ThickFogArena()
    ball = DummyBall()
    world = DummyWorld(arena)
    p = Perception(ball, world)

    passed_radius = []
    def mock_get(b, r):
        passed_radius.append(r)
        return {"enemies": [], "allies": [], "boosters": [], "traps": []}
    world.get_nearby_entities = mock_get

    p.scan()
    assert passed_radius[0] == 500.0
