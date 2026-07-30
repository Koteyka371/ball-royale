import pytest
import math
from src.ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []

class MockHazard:
    def __init__(self, kind):
        self.active = True
        self.duration = 0.0
        self.damage = 0
        self.kind = kind
        self.x = 0
        self.y = 0
        self.radius = 15.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []
        self.balls = []
        self.next_id = 1000

class MockBall:
    def __init__(self, id, x=0, y=0, team="team_a"):
        self.decoy_timer = 0.0
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.alive = True
        self.hp = 100
        self.max_hp = 100
        self.base_speed = 200
        self.speed = 2.0
        self.base_damage = 10
        self.radius = 10
        self.damage = 10
        self.is_blinded = False
        self.blindness_timer = 0.0
        self._base_speed_set = True
        self.perception_radius = 250.0
        self.is_stunned = False
        self.stun_timer = 0.0
        self.vision_reduction_timer = 0.0
        self.vision_reduction_applied = False
    def __eq__(self, other):
        if not isinstance(other, MockBall):
            return False
        return self.id == other.id

def test_flashbang_booster_pickup():
    world = MockWorld()
    player = MockBall(1)
    world.balls.append(player)

    booster = MockHazard("flashbang_booster")
    booster.x = 0
    booster.y = 0
    world.boosters.append(booster)

    action = Action(player, world)
    action._collect_booster(0.016)

    # Booster removed
    assert len(world.boosters) == 0
    # We no longer spawn decoys on flashbang pickup, it explodes immediately
    assert len(world.balls) == 1

def test_flashbang_booster_explosion_blindness():
    world = MockWorld()

    enemy = MockBall(3, x=50, y=0, team="team_b")
    world.balls.append(enemy)

    player = MockBall(4, x=0, y=0, team="team_a")
    world.balls.append(player)

    booster = MockHazard("flashbang_booster")
    booster.x = 0
    booster.y = 0
    world.boosters.append(booster)

    action = Action(player, world)

    # We must properly mock action._get_enemies() so it returns a new list each time,
    # rather than modifying the same list, or just ensure it returns a list correctly.
    def mock_get_enemies():
        return [enemy]
    action._get_enemies = mock_get_enemies

    action._get_boosters = lambda: [booster]
    action._collect_booster(0.016)

    # Replaced blindness logic with perception radius reduction
    assert enemy.perception_radius == 0.0
    assert enemy.vision_reduction_timer >= 3.0
    assert enemy.is_stunned
    assert enemy.stun_timer >= 3.0

    # Ensure player is not affected by their own booster
    assert not getattr(player, 'is_stunned', False)
    assert getattr(player, 'perception_radius', 250.0) != 0.0
