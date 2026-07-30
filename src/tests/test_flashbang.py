import pytest
from ai.action import Action
class MockEntity:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
class MockWorld:
    def __init__(self, balls=None, boosters=None, arena=None):
        self.balls = balls or []
        self.boosters = boosters or []
        self.arena = arena
        self.events = []
    def get_nearby_entities(self, ball, radius):
        return []

class MockArena:
    def __init__(self, hazards=None):
        self.hazards = hazards or []

def test_flashbang():
    ball = MockEntity(id=1, team="A", x=0, y=0, perception_radius=100)
    enemy = MockEntity(id=2, team="B", x=10, y=10, perception_radius=100, is_stunned=False)
    booster = MockEntity(kind="flashbang_booster", x=5, y=5)
    world = MockWorld([ball, enemy], [booster], MockArena([booster]))
    action = Action(ball, world)

    # Add dummy methods
    action._get_boosters = lambda: [booster]

    # Run loop
    action._collect_booster(1.0)

    # Assert booster was collected
    assert booster not in world.boosters
    assert booster not in world.arena.hazards

    # Assert enemy was affected
    assert getattr(enemy, 'is_stunned', False)
    assert getattr(enemy, 'perception_radius', 100) == 0.0
