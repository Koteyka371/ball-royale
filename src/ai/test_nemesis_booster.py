import pytest
from system.profile import ProfileManager
from ai.action import Action
import os
import math

class MockEntity:
    def __init__(self, id, x, y, kind="", radius=15.0, ball_type=None, hp=100.0, team=None):
        self.id = id
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = radius
        self.ball_type = ball_type
        self.hp = hp
        self.max_hp = hp
        self.speed = 2.0
        self.base_speed = 2.0
        self.vx = 0.0
        self.vy = 0.0
        self.team = team

class MockWorld:
    def __init__(self):
        self.balls = []
        self.boosters = []
        self.arena = self.MockArena()
        self.profile_manager = ProfileManager("test_nemesis_booster_profile.json")

    class MockArena:
        def __init__(self):
            self.hazards = []
            self.width = 1000
            self.height = 1000
            self.items = []

def test_nemesis_booster_collection():
    world = MockWorld()

    ball = MockEntity(id=1, x=100.0, y=100.0, ball_type="basic", team="Red")
    nemesis_enemy = MockEntity(id=2, x=200.0, y=100.0, ball_type="nemesis", team="Blue")
    world.balls = [ball, nemesis_enemy]

    # Make "nemesis" a nemesis of "basic"
    world.profile_manager.add_kill(ball.ball_type, nemesis_enemy.ball_type)
    world.profile_manager.add_kill(ball.ball_type, nemesis_enemy.ball_type)
    assert world.profile_manager.is_nemesis(ball.ball_type, nemesis_enemy.ball_type) == True

    nemesis_booster = MockEntity(id=99, x=105.0, y=100.0, kind="nemesis_booster")
    nemesis_booster.ball_type = "booster"
    nemesis_booster.active = True
    world.boosters = [nemesis_booster]
    world.arena.hazards = [nemesis_booster]

    action = Action(ball, world)

    # 1. Collect booster
    action.execute("collect_booster", 1.0)

    assert hasattr(ball, "nemesis_booster_timer")
    assert ball.nemesis_booster_timer > 0
    assert nemesis_booster not in world.arena.hazards

def test_nemesis_booster_movement():
    world = MockWorld()

    ball = MockEntity(id=1, x=100.0, y=100.0, ball_type="basic", team="Red")
    ball.base_speed = 10.0

    # Target nemesis
    nemesis_enemy = MockEntity(id=2, x=200.0, y=100.0, ball_type="nemesis", team="Blue")

    # Another enemy that is NOT a nemesis
    other_enemy = MockEntity(id=3, x=100.0, y=200.0, ball_type="other", team="Blue")

    world.balls = [ball, nemesis_enemy, other_enemy]

    # Setup nemesis
    world.profile_manager.add_kill(ball.ball_type, nemesis_enemy.ball_type)
    world.profile_manager.add_kill(ball.ball_type, nemesis_enemy.ball_type)

    ball.nemesis_booster_timer = 5.0
    action = Action(ball, world)

    # Without nemesis booster, "flee" would move away from enemies.
    # We will test how the speed boost affects movement.
    # To isolate movement, we can just call execute on a neutral strategy or check the delta.
    old_x = ball.x
    action.execute("defend", 1.0)

    # Since nemesis booster is active, and nemesis is at x=200, we should see an extra +5.0 movement in x direction.
    # defend strategy generally tries to hold position or move towards center.
    # The nemesis booster will add `base_speed * 0.5 * delta` towards the nemesis (x=200).
    # 10.0 * 0.5 * 1.0 = 5.0 extra displacement towards x.

    # Let's verify the timer decreased
    assert ball.nemesis_booster_timer < 5.0
    assert ball.x > old_x + 0.1 # Check displacement towards x=200

    if os.path.exists("test_nemesis_booster_profile.json"):
        os.remove("test_nemesis_booster_profile.json")
