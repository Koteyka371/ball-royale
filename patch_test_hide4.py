# The fallback flee logic or something else is executing! Wait, let's see _hide_behind in src/ai/action.py again.
# "if not best_ally: self._flee(delta); return"
# Does it find best_ally?
# best_ally logic:
# b_type = getattr(ally, "ball_type", "").lower()
# if b_type == "tank": score += 1000.0
# The subject is in allies because _get_allies returns all balls with the same team!
# Yes, subject is team 1. ally_tank is team 1. So allies = [subject, ally_tank].
# dist_sq penalty for ally_tank: (20 - 0)^2 = 400. score = 250 + 1000 - 400 * 0.001 = 1250 - 0.4 = 1249.6
# dist_sq penalty for subject: (0 - 0)^2 = 0. score = 100 - 0 = 100.
# So best_ally is ally_tank!
# Wait! In _get_allies():
# "return [b for b in self.world.balls if b != self.ball and getattr(b, 'team', None) == getattr(self.ball, 'team', None) and getattr(b, 'alive', True)]"
# Oh! "b != self.ball". So subject is NOT in allies!
# That means best_ally = ally_tank.
# target_x = 20 - 30 = -10.
# target_y = 0.
# self.ball.x = 0.
# dx_m = -10. nx_m = -1.
# wait, what else alters self.ball.x?
# action.execute calls: self._resolve_collisions(), self._clamp_position().
# Collisions!
# The subject is at (0, 0), radius 10.
# Ally tank is at (20, 0), radius 10.
# Distance is 20. Radii sum is 20. They are touching!
# In _resolve_collisions, it pushes balls apart.
# If distance <= radii sum, it pushes them.
# The push might move subject to the right or left depending on floating point!
# Ah! Let's put ally_tank at 50 to avoid collisions!

test_content = """
import pytest
from src.ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []
        self.safe_zone_radius = 9999
        self.safe_zone_center = (0, 0)
        self.width = 1000
        self.height = 1000
        self.obstacles = []

class MockWorld:
    def __init__(self):
        self.balls = []
        self.arena = MockArena()
        self.tick = 0

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
        self.current_action = "idle"

def test_hide_behind():
    world = MockWorld()
    subject = MockBall(id=1, x=0.0, y=0.0, team=1)
    ally_tank = MockBall(id=2, x=50.0, y=0.0, team=1, ball_type="tank", max_hp=250.0)
    enemy = MockBall(id=3, x=100.0, y=0.0, team=2, ball_type="warrior", max_hp=150.0)
    world.balls = [subject, ally_tank, enemy]

    action = Action(subject, world)

    # Store old methods to bypass complex boid/obstacle avoid math that could move us unpredictably
    old_avoid = action._apply_obstacle_avoidance
    old_boid = action._apply_boid_rules

    action._apply_obstacle_avoidance = lambda nx, ny, *args, **kwargs: (nx, ny)
    action._apply_boid_rules = lambda nx, ny: (nx, ny)

    action.execute("hide_behind", 1.0/60.0)

    # Restore
    action._apply_obstacle_avoidance = old_avoid
    action._apply_boid_rules = old_boid

    # target is ally(50) - 30 = 20.
    # subject is at 0. So it should move TOWARDS 20.
    # Therefore, subject.x should INCREASE!
    assert subject.x > 0.0

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
