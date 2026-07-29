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
        self.ball_type = "chameleon"
        self.vx = 0.0
        self.vy = 0.0
        self.speed = 100
        self.blend_amount = 0.0
        self.invisible_to_minimap = False
        self.perception_radius = 250.0

class MockWorld:
    def __init__(self):
        self.balls = []
        self.arena = type('MockArena', (), {'hazards': []})
        self.boosters = []
        self.events = []
        self.tick = 0
    def get_nearby_entities(self, ball, radius):
        return {'enemies': [b for b in self.balls if b != ball]}

def test_chameleon_blend_standing_still():
    world = MockWorld()
    chameleon = MockBall(1, 0, 0)
    world.balls.append(chameleon)

    action = Action(chameleon, world)

    # Simulate standing still for 2 seconds
    action.execute("idle", 2.0)

    assert getattr(chameleon, "blend_amount", 0.0) >= 1.0
    assert getattr(chameleon, "invisible_to_minimap", False) is True

def test_chameleon_unblend_moving():
    world = MockWorld()
    chameleon = MockBall(1, 0, 0)
    chameleon.blend_amount = 1.0
    chameleon.vx = 5.0
    world.balls.append(chameleon)

    action = Action(chameleon, world)

    action.execute("idle", 1.0)

    assert getattr(chameleon, "blend_amount", 0.0) == 0.0
    assert getattr(chameleon, "invisible_to_minimap", False) is False

def test_chameleon_perception_reduction():
    world = MockWorld()
    chameleon = MockBall(1, 100, 0)
    chameleon.blend_amount = 1.0

    enemy = MockBall(2, 0, 0)
    enemy.ball_type = "normal"

    world.balls.extend([chameleon, enemy])

    action = Action(enemy, world)
    enemies = action._get_enemies_internal()

    # Distance is 100, normally visible (perception=250), but reduced perception should be 50.
    assert chameleon not in enemies

    # Move enemy closer
    chameleon.x = 40
    enemies2 = action._get_enemies_internal()
    assert chameleon in enemies2
