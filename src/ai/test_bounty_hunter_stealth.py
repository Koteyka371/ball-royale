import pytest
from unittest.mock import MagicMock
from ai.ball_types_bounty_hunter import BountyHunter
from ai.action import Action
from ai.perception import Perception

class MockArena:
    def __init__(self):
        self.is_night = False
        self.hazards = []
        self.is_sandstorming = False

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.boosters = []
        self.items = []
        self.traps = []

    def get_nearby_entities(self, ball, radius):
        return {
            "enemies": [b for b in self.balls if b.id != ball.id],
            "allies": [],
            "boosters": [],
            "traps": []
        }

class MockEntity:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

def test_bounty_hunter_stealth_mechanic():
    hunter = BountyHunter(1, x=0.0, y=0.0)
    assert hunter.out_of_combat_timer == 0.0

    world = MockWorld()
    world.balls.append(hunter)

    action = Action(hunter, world)

    # Tick execution out of combat should increment the timer
    action.execute("idle", 2.0)
    assert hunter.out_of_combat_timer == 2.0

    action.execute("idle", 4.0)
    assert hunter.out_of_combat_timer == 6.0

    # Test Perception logic
    enemy = MockEntity(id=2, x=0.0, y=100.0, team=2, alive=True, ball_type="basic", has_thermal_vision=False)
    world.balls.append(enemy)

    enemy_perception = Perception(enemy, world)
    data = enemy_perception.scan()

    # Bounty Hunter is out of combat > 5.0 and dist 100 (> 40.0), so shouldn't be seen
    assert not any(e.id == hunter.id for e in data["enemies"])

    # Move closer to 30 units
    enemy.y = 30.0
    data = enemy_perception.scan()
    assert any(e.id == hunter.id for e in data["enemies"])

    # If enemy has thermal vision, they can see from far
    enemy.y = 100.0
    enemy.has_thermal_vision = True
    data = enemy_perception.scan()
    assert any(e.id == hunter.id for e in data["enemies"])

    # Reset out_of_combat_timer on damage dealt
    action._attempt_damage_internal(hunter, enemy)
    assert hunter.out_of_combat_timer == 0.0

    # Now they can be seen without thermal from far
    enemy.has_thermal_vision = False
    data = enemy_perception.scan()
    assert any(e.id == hunter.id for e in data["enemies"])
