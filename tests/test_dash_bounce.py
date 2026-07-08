import pytest
from ai.action import Action
import math

class MockArena:
    def __init__(self, width, height):
        self.width = width
        self.height = height

class MockWorld:
    def __init__(self, width, height):
        self.arena = MockArena(width, height)
        self.balls = []
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

    def _deal_damage(self, target, attacker, damage=None):
        pass

    def get_nearby_entities(self, entity, radius):
        return {
            'enemies': [e for e in self.balls if e.team != entity.team],
            'allies': [],
            'hazards': [],
            'boosters': []
        }

class MockBall:
    def __init__(self, id, x, y, radius, skill="dash"):
        self.id = id
        self.x = x
        self.y = y
        self.radius = radius
        self.skill = skill
        self.team = "A"
        self.is_dashing = False
        self.hp = 100.0
        self.alive = True
        self.is_stealth = False

def test_dash_bounce_x_wall():
    world = MockWorld(100, 100)

    # Place ball near right wall
    ball = MockBall(1, 80, 50, 10, "dash")
    world.balls.append(ball)

    # Place enemy to make it dash right
    enemy = MockBall(2, 90, 50, 10, "none")
    enemy.team = "B"
    world.balls.append(enemy)

    action = Action(ball, world)

    # Give it a dash distance of 50
    ball.dash_range_mult = 0.5

    # Start: x=80. Enemy at x=90. It will dash right.
    # Dist to right wall: 100 - 10 (radius) - 80 = 10.
    # It moves 10 right, hitting x=90.
    # Remaining dash dist: 50 - 10 = 40.
    # It reflects and moves 40 left.
    # Final x should be 90 - 40 = 50.

    action._use_skill()

    assert math.isclose(ball.x, 50.0, rel_tol=1e-3)
    assert math.isclose(ball.y, 50.0, rel_tol=1e-3)

def test_dash_bounce_y_wall():
    world = MockWorld(100, 100)

    # Place ball near top wall
    ball = MockBall(1, 50, 20, 10, "dash")
    world.balls.append(ball)

    # Place enemy to make it dash up
    enemy = MockBall(2, 50, 10, 10, "none")
    enemy.team = "B"
    world.balls.append(enemy)

    action = Action(ball, world)

    # Give it a dash distance of 50
    ball.dash_range_mult = 0.5

    # Start: y=20. Enemy at y=10. It will dash up.
    # Dist to top wall: 20 - 10 (radius) = 10.
    # It moves 10 up, hitting y=10.
    # Remaining dash dist: 50 - 10 = 40.
    # It reflects and moves 40 down.
    # Final y should be 10 + 40 = 50.

    action._use_skill()

    assert math.isclose(ball.x, 50.0, rel_tol=1e-3)
    assert math.isclose(ball.y, 50.0, rel_tol=1e-3)

def test_dash_bounce_corner():
    world = MockWorld(100, 100)

    # Place ball near top-right corner
    ball = MockBall(1, 80, 20, 10, "dash")
    world.balls.append(ball)

    # Place enemy to make it dash towards top-right at a 45 degree angle
    enemy = MockBall(2, 90, 10, 10, "none")
    enemy.team = "B"
    world.balls.append(enemy)

    action = Action(ball, world)

    ball.dash_range_mult = 0.5 # dash dist 50

    # Starts at 80, 20. Target is 90, 10.
    # dir is dx=1, dy=-1 normalized: ~0.707, ~-0.707
    # dist to right wall: 100-10-80 = 10 -> 10 / 0.707 = 14.14 dist
    # dist to top wall: 20-10 = 10 -> 10 / 0.707 = 14.14 dist
    # It hits both walls simultaneously, reflects both directions.

    action._use_skill()

    # We don't need exact values, just verify it stayed inside the arena and didn't crash.
    assert ball.x <= 90.0
    assert ball.y >= 10.0
    assert ball.x >= 10.0
    assert ball.y <= 90.0
