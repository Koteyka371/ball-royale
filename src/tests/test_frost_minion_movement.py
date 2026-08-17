import pytest
from ai.action import Action
import math

class MockWorld:
    def __init__(self):
        self.next_id = 1000
        self.balls = []
        self.arena = type('obj', (object,), {'hazards': [], 'width': 1000, 'height': 1000})()
    def get_nearby_entities(self, ball, radius):
        return {"boosters": [], "hazards": []}
    def _deal_damage(self, attacker, target, dmg=None):
        pass

class MockBall:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.radius = 15.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.id = 1
        self.team = "team1"
        self.ball_type = "easy"
        self.speed = 2.5
        self.base_speed = 2.5
        self.attack_timer = 0.0

def test_frost_minion_movement():
    world = MockWorld()
    world.next_id = 1000

    fm = MockBall()
    fm.ball_type = "frost_minion"
    fm.hp = 15
    fm.team = "undead"
    fm.speed = 2.5
    fm.id = 1

    enemy = MockBall()
    enemy.team = "hero"
    enemy.hp = 100
    enemy.id = 2

    world.balls = [fm, enemy]

    action = Action(fm, world)
    action._get_enemies = lambda: [enemy]

    # Test case 1: Too close (dist < 150) -> Should move away
    fm.x = 500.0
    fm.y = 500.0
    enemy.x = 600.0 # dist = 100
    enemy.y = 500.0
    action.execute("idle", 0.016)
    assert fm.x < 500.0 # Moved away (left)

    # Test case 2: Too far (dist > 200) -> Should move closer
    fm.x = 500.0
    fm.y = 500.0
    enemy.x = 800.0 # dist = 300
    enemy.y = 500.0
    action.execute("idle", 0.016)
    assert fm.x > 500.0 # Moved closer (right)

    # Test case 3: Ideal distance (150 <= dist <= 200) -> Should stay still (or only drift slightly from flocking)
    fm.x = 500.0
    fm.y = 500.0
    enemy.x = 675.0
    enemy.y = 500.0
    action.execute("idle", 0.016)
    assert abs(fm.x - 500.0) < 5.0 # Should barely move
