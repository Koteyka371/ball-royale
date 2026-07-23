import pytest
from src.ai.game_modes import GAME_MODES
from src.ai.action import Action
import math

class MockProfileManager:
    def __init__(self):
        self.nemesis_map = {}

    def is_nemesis(self, t1, t2):
        return (t1, t2) in self.nemesis_map or (t2, t1) in self.nemesis_map

class MockGameMode:
    def __init__(self):
        self.name = "Nemesis Hunter"

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.profile_manager = MockProfileManager()
        self.game_mode = MockGameMode()
        self.arena = MockArena()
        self.balls = []
        self.events = []

    def add_event(self, event_type, event_data):
        self.events.append({"type": event_type, "data": event_data})

    def _deal_damage(self, attacker, target):
        if hasattr(target, 'hp') and hasattr(attacker, 'damage'): target.hp -= attacker.damage

class MockBall:
    def __init__(self, ball_id, ball_type, team, x, y):
        self.id = ball_id
        self.ball_type = ball_type
        self.team = team
        self.x = x
        self.y = y
        self.hp = 100.0
        self.max_hp = 100.0
        self.damage = 10.0
        self.alive = True
        self.vx = 0.0
        self.vy = 0.0

    def take_damage(self, amount):
        self.hp -= amount

def test_nemesis_hunter_mode_heals_attacker():
    world = MockWorld()

    attacker = MockBall(1, "fire", "team1", 0, 0)
    attacker.hp = 50.0  # Set low HP to see healing

    target = MockBall(2, "water", "team2", 10, 10)

    world.balls = [attacker, target]

    # Not nemesis yet
    action = Action(attacker, world)

    # Emulate _attempt_damage directly
    # Wait, action doesn't have _attempt_damage exposed properly if we don't call it correctly
    # Action's _attempt_damage handles damage processing.
    # For testing, we can simulate an attack

    # Store old HP for comparison
    target.hp = 100.0
    action._attempt_damage(attacker, target)

    assert target.hp == 90.0, "Target should take 10 damage"
    assert attacker.hp == 50.0, "Attacker should NOT be healed because not nemesis"

    # Now set them as nemesis
    world.profile_manager.nemesis_map[("fire", "water")] = True

    action._attempt_damage(attacker, target)
    assert target.hp == 80.0, "Target takes another 10 damage"
    assert attacker.hp == 60.0, "Attacker SHOULD be healed by 10 (100% of damage dealt)"

    # Try with max_hp cap
    attacker.hp = 95.0
    action._attempt_damage(attacker, target)
    assert target.hp == 70.0, "Target takes another 10 damage"
    assert attacker.hp == 100.0, "Attacker heal should be capped at max_hp"

def test_nemesis_hunter_mode_existence():
    assert "nemesis_hunter" in GAME_MODES
    mode = GAME_MODES["nemesis_hunter"]
    assert mode.name == "Nemesis Hunter"
    assert "heals you instead" in mode.description
