import pytest
import math
import os
from system.profile import ProfileManager
from ai.action import Action

class MockWorld:
    def __init__(self):
        self.balls = []
        self.profile_manager = ProfileManager("test_nemesis_pull_profile.json")
        self.arena = self.MockArena()

    class MockArena:
        def __init__(self):
            self.hazards = []

class MockEntity:
    def __init__(self, id, ball_type, x, y, hp=100.0, speed=2.0):
        self.id = id
        self.ball_type = ball_type
        self.x = x
        self.y = y
        self.hp = hp
        self.speed = speed
        self.alive = True
        self.team = "team_" + str(id)
        self.radius = 10.0
        self.skill = "nemesis_pull"
        self.skill_timer = 0.0
        self.skill_cooldown = 8.0
        self.slow_timer = 0.0
        self.base_speed = speed
        self.vx = 0.0
        self.vy = 0.0
        self.charge_level = 0.0
        self.damage = 10.0
        self._base_speed_set = True

def test_nemesis_pull_activation():
    world = MockWorld()

    # User of the skill
    player = MockEntity(1, "player", 100.0, 100.0)

    # Enemy that has killed player multiple times (Nemesis)
    nemesis = MockEntity(2, "nemesis", 200.0, 100.0)

    # Regular enemy
    regular = MockEntity(3, "regular", 100.0, 200.0)

    world.balls = [player, nemesis, regular]

    # Make nemesis the nemesis of player
    world.profile_manager.add_kill(nemesis.ball_type, player.ball_type)
    world.profile_manager.add_kill(nemesis.ball_type, player.ball_type)
    assert world.profile_manager.is_nemesis(nemesis.ball_type, player.ball_type)

    action = Action(player, world)

    # Execute nemesis_pull skill
    action.execute("use_skill", 1.0)

    # Check that nemesis was targeted
    assert getattr(nemesis, "nemesis_pull_source", None) == player
    assert getattr(nemesis, "nemesis_pull_timer", 0.0) == 5.0

    # Check that regular was NOT targeted
    assert getattr(regular, "nemesis_pull_source", None) is None
    assert getattr(regular, "nemesis_pull_timer", 0.0) == 0.0

    if os.path.exists("test_nemesis_pull_profile.json"):
        os.remove("test_nemesis_pull_profile.json")

def test_nemesis_pull_effect():
    world = MockWorld()

    player = MockEntity(1, "player", 100.0, 100.0)
    nemesis = MockEntity(2, "nemesis", 200.0, 100.0)

    # Simulate nemesis being pulled by player
    nemesis.nemesis_pull_source = player
    nemesis.nemesis_pull_timer = 3.0
    nemesis.speed = 10000.0

    world.balls = [player, nemesis]

    action = Action(nemesis, world)

    initial_x = nemesis.x
    action.execute("none", 1.0) # 0.1 seconds delta

    # Check pull movement. Delta is 0.1. Pull speed is 1.5 * 10.0 = 15.0
    # Movement is towards player. Nemesis is at 200, player at 100.
    # dx = 100 - 200 = -100. Movement is negative.
    # Expected displacement: 15.0 * 0.1 = 1.5. So new x should be 198.5

    assert nemesis.x < initial_x
    assert nemesis.x < 199.5

    # Check slow timer
    assert nemesis.slow_timer == 0.5
    assert nemesis.nemesis_pull_timer == 2.0

    if os.path.exists("test_nemesis_pull_profile.json"):
        os.remove("test_nemesis_pull_profile.json")
