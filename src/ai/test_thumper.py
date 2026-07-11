import pytest
import math
from ai.action import Action

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.radius = 10
        self.hp = 100
        self.alive = True
        self.team = "team_1"
        self.skill_timer = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.ball_type = 'base'

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

    def clamp_position(self, x, y, r):
        return x, y, False

class MockHazard:
    def __init__(self, id, x, y, radius, kind, damage):
        self.id = id
        self.x = x
        self.y = y
        self.radius = radius
        self.kind = kind
        self.damage = damage
        self.duration = 9999.0

class MockWorld:
    def __init__(self):
        self.balls = []
        self.arena = MockArena()
        self.tick = 1

    def get_nearby_entities(self, ball, radius):
        return {'boosters': [], 'hazards': [], 'enemies': []}

    def _deal_damage(self, source, target, amount=10.0):
        target.hp -= amount
        if target.hp <= 0:
            target.alive = False

def test_thumper_pulse_disables_skills():
    world = MockWorld()

    # Create the thumper hazard
    thumper = MockHazard(1, 100, 100, 20, "thumper", 0)
    setattr(thumper, "team", "team_a")
    # Force pulse timer to fire on first tick
    setattr(thumper, "pulse_timer", 0.0)
    world.arena.hazards.append(thumper)

    # Create enemy ball within range
    enemy_ball = MockBall(2, 150, 100)
    enemy_ball.alive = True
    enemy_ball.team = "team_b"
    enemy_ball.skill_timer = 0.0
    world.balls.append(enemy_ball)

    # Create enemy ball out of range
    enemy_far = MockBall(3, 800, 100)
    enemy_far.alive = True
    enemy_far.team = "team_b"
    enemy_far.skill_timer = 0.0
    world.balls.append(enemy_far)

    # Execute action to trigger hazard logic
    action = Action(enemy_ball, world)
    action.execute("idle", 1.0)

    # Pulse timer should be reset to 3.0
    assert getattr(thumper, "pulse_timer") == 3.0

    # Enemy in range should have skill disabled
    assert enemy_ball.skill_timer >= 4.0 # It gets decremented by delta=1.0 at end of execute, so max(..., 5.0) - 1.0 = 4.0

    # Enemy out of range should remain 0
    assert enemy_far.skill_timer <= 0.0

def test_thumper_draws_tornado():
    world = MockWorld()

    # Create the thumper hazard
    thumper = MockHazard(1, 500, 500, 20, "thumper", 0)
    world.arena.hazards.append(thumper)

    # Create a tornado
    tornado = MockHazard(2, 100, 100, 50, "tornado", 10)
    setattr(tornado, "vx", 0.0)
    setattr(tornado, "vy", 100.0) # Moving vertically initially
    world.arena.hazards.append(tornado)

    # Need a dummy ball to run action
    ball = MockBall(3, 10, 10)
    world.balls = [ball]
    action = Action(ball, world)

    action.execute("idle", 1.0)

    # Tornado velocity should now be pointing toward the thumper (500, 500) from (100, 100)
    # Expected direction is roughly +x, +y
    vx = getattr(tornado, "vx")
    vy = getattr(tornado, "vy")

    assert vx > 0.0
    assert vy > 0.0
