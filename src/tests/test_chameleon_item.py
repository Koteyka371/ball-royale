import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.action import Action

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.alive = True
        self.team = "blue"
        self.color = "blue"
        self.name = "Player"
        self.label = "Player"
        self.ball_type = "normal"
        self.vx = 0
        self.vy = 0
        self.speed = 100
        self.base_speed = 100
        self.is_bounty = False
        self.high_threat = False
        self.is_bounty_target = False

class MockWorld:
    def __init__(self):
        self.balls = []
        self.arena = type('MockArena', (), {'hazards': []})
        self.boosters = []
        self.events = []
        self.tick = 0

def test_chameleon_item_pickup_hazard():
    world = MockWorld()
    player = MockBall(1, 0, 0)
    world.balls.append(player)

    item = type('Item', (), {'kind': 'chameleon_item', 'x': 5, 'y': 5, 'radius': 15.0, 'active': True})()
    world.boosters.append(item)

    hazard = type('Hazard', (), {'kind': 'spikes', 'x': 50, 'y': 50, 'active': True, 'color_hex': '#ffffff'})()
    world.arena.hazards.append(hazard)

    action = Action(player, world)

    # Overwrite _get_enemies for test isolation
    action._get_enemies = lambda: []
    action._get_boosters = lambda: world.boosters

    action._collect_booster(1.0)

    assert getattr(player, "is_disguised", False) is True
    assert player.team == "spikes"
    assert player.color == "#ffffff"
    assert getattr(player, "disguise_timer", 0.0) > 0.0

    # Test disguise timer countdown
    action.execute("idle", 10.1)

    assert getattr(player, "is_disguised", False) is False
    assert player.team == "blue"
    assert player.color == "blue"

def test_chameleon_item_pickup_enemy():
    world = MockWorld()
    player = MockBall(1, 0, 0)
    world.balls.append(player)

    item = type('Item', (), {'kind': 'chameleon_item', 'x': 5, 'y': 5, 'radius': 15.0, 'active': True})()
    world.boosters.append(item)

    enemy = MockBall(2, 50, 50)
    enemy.name = "Enemy1"
    enemy.team = "red"
    enemy.color = "red"
    enemy.label = "Enemy1"

    world.balls.append(enemy)

    action = Action(player, world)

    # Overwrite _get_enemies for test isolation
    action._get_enemies = lambda: [enemy]
    action._get_boosters = lambda: world.boosters

    action._collect_booster(1.0)

    assert getattr(player, "is_disguised", False) is True
    assert player.team == "red"
    assert player.color == "red"
    assert player.label == "Enemy1"
