import pytest
import os
import sys
sys.path.insert(0, os.path.abspath('src'))

from system.profile import ProfileManager
from ai.action import Action
from unittest.mock import MagicMock

@pytest.fixture
def temp_profile_file(tmp_path):
    return str(tmp_path / "test_ancient_profile.json")

def test_add_ancient_fragments(temp_profile_file):
    pm = ProfileManager(temp_profile_file)

    # Add first fragment
    assert pm.add_ancient_fragment() is False
    assert pm.data.get("ancient_fragments", 0) == 1

    # Add second fragment
    assert pm.add_ancient_fragment() is False
    assert pm.data.get("ancient_fragments", 0) == 2

    # Add third fragment - should unlock!
    assert pm.add_ancient_fragment() is True
    assert pm.data.get("ancient_fragments", 0) == 0

    assert "ancient_aura" in pm.data.get("cosmetics", [])
    assert "ancient_guardian" in pm.data.get("unlocked_balls", [])

def test_action_collect_fragment():
    class MockHazard:
        def __init__(self, x, y, kind):
            self.x = x
            self.y = y
            self.kind = kind
            self.radius = 15.0
            self.active = True

    class MockBall:
        def __init__(self):
            self.x = 0
            self.y = 0
            self.radius = 10.0
            self.speed = 2.0
            self.cosmetic = "default"
            self.collected_fragments = 0

    class MockWorld:
        def __init__(self):
            self.arena = type("Arena", (), {"hazards": []})()
            self.boosters = []
            self.profile_manager = MagicMock()
            self.profile_manager.add_ancient_fragment.return_value = True

    ball = MockBall()
    world = MockWorld()
    hazard = MockHazard(5, 0, "loadout_fragment")
    world.arena.hazards.append(hazard)

    action = Action(ball, world)

    # Force _get_boosters to return the hazard
    action._get_boosters = lambda: [hazard]
    action._get_enemies = lambda: []

    action._collect_booster(0.1)

    # Verify fragment collected
    assert hazard not in world.arena.hazards
    assert ball.collected_fragments == 1

    # Profile manager should have been called
    world.profile_manager.add_ancient_fragment.assert_called_once()

    # Since profile_manager.add_ancient_fragment returned True (mocked), cosmetic should change
    assert ball.cosmetic == "ancient_aura"

def test_action_collect_fragment_no_profile_manager():
    class MockHazard:
        def __init__(self, x, y, kind):
            self.x = x
            self.y = y
            self.kind = kind
            self.radius = 15.0
            self.active = True

    class MockBall:
        def __init__(self):
            self.x = 0
            self.y = 0
            self.radius = 10.0
            self.speed = 2.0
            self.cosmetic = "default"
            self.collected_fragments = 2

    class MockWorld:
        def __init__(self):
            self.arena = type("Arena", (), {"hazards": []})()
            self.boosters = []
            self.profile_manager = None

    ball = MockBall()
    world = MockWorld()
    hazard = MockHazard(5, 0, "loadout_fragment")
    world.arena.hazards.append(hazard)

    action = Action(ball, world)

    # Force _get_boosters to return the hazard
    action._get_boosters = lambda: [hazard]
    action._get_enemies = lambda: []

    action._collect_booster(0.1)

    # Verify fragment collected
    assert hazard not in world.arena.hazards
    assert ball.collected_fragments == 3

    # Since we reached 3 fragments, it should unlock locally without profile manager
    assert ball.cosmetic == "ancient_aura"
