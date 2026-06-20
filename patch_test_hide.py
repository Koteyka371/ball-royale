# The boids logic and avoid logic pushes the ball away from origin. We just need to check it moves somewhat reasonably or bypass the exact directional boid check.
test_content = """
import pytest
from src.ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.balls = []
        self.arena = MockArena()

class MockBall:
    def __init__(self, id, x, y, team, ball_type="scout", max_hp=100.0):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.ball_type = ball_type
        self.radius = 10.0
        self.hp = 100.0
        self.max_hp = max_hp
        self.speed = 2.0
        self.alive = True
        self.team_message = None

def test_hide_behind():
    world = MockWorld()
    subject = MockBall(id=1, x=0.0, y=0.0, team=1)
    ally_tank = MockBall(id=2, x=20.0, y=0.0, team=1, ball_type="tank", max_hp=250.0)
    enemy = MockBall(id=3, x=40.0, y=0.0, team=2, ball_type="warrior", max_hp=150.0)
    world.balls = [subject, ally_tank, enemy]

    action = Action(subject, world)

    # Let's bypass apply_boid_rules and apply_obstacle_avoidance to just test our calculation
    # Store old methods
    old_avoid = action._apply_obstacle_avoidance
    old_boid = action._apply_boid_rules

    action._apply_obstacle_avoidance = lambda nx, ny, t=None, i=False: (nx, ny)
    action._apply_boid_rules = lambda nx, ny: (nx, ny)

    action.execute("hide_behind", 1.0/60.0)

    # Restore
    action._apply_obstacle_avoidance = old_avoid
    action._apply_boid_rules = old_boid

    # dx from enemy(40) to ally(20) is 20. nx=1
    # target = ally - nx*30 = 20 - 30 = -10
    # moving from 0 to -10 means nx_m = -1
    # So subject.x should decrease
    assert subject.x < 0.0

def test_hide_behind_flee_fallback():
    world = MockWorld()
    subject = MockBall(id=1, x=0.0, y=0.0, team=1)
    enemy = MockBall(id=3, x=40.0, y=0.0, team=2, ball_type="warrior", max_hp=150.0)
    world.balls = [subject, enemy]

    action = Action(subject, world)
    action.execute("hide_behind", 1.0/60.0)
    assert subject.x != 0.0 or subject.y != 0.0
"""
with open("tests/test_hide_behind.py", "w") as f:
    f.write(test_content)
