# If it's returning negative, maybe I'm calculating the expected move incorrectly!
# dx = target_enemy.x - best_ally.x = 100 - 50 = 50.
# dist = 50. nx = 1.
# target_x = best_ally.x - nx * 30.0 = 50 - 30 = 20.
# dx_m = target_x - self.ball.x = 20 - 0 = 20.
# dist_m = 20. nx_m = 20 / 20 = 1.
# wait! So nx_m is 1! It SHOULD increase x.
# Why does subject.x decrease?
# Maybe _clamp_position or _resolve_collisions?
# In action._resolve_collisions(), it pushes balls apart if they overlap.
# Let's print the actual dx, dy inside test:

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
    # put the ally behind the subject initially so it has to move further
    ally_tank = MockBall(id=2, x=-100.0, y=0.0, team=1, ball_type="tank", max_hp=250.0)
    enemy = MockBall(id=3, x=100.0, y=0.0, team=2, ball_type="warrior", max_hp=150.0)
    world.balls = [subject, ally_tank, enemy]

    action = Action(subject, world)

    action.execute("hide_behind", 1.0/60.0)

    # target_x = ally_x - nx*30 = -100 - (1)*30 = -130
    # moving from 0 to -130 means nx_m = -1
    # Subject should move left!
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
