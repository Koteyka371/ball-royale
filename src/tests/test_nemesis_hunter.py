import pytest
from system.profile import ProfileManager
from ai.action import Action
import os
import math

class MockEntity:
    def __init__(self, id, x, y, ball_type=None, hp=100.0, team=None):
        self.id = id
        self.x = x
        self.y = y
        self.ball_type = ball_type
        self.hp = hp
        self.max_hp = hp
        self.base_speed = 100.0
        self.speed = 100.0
        self.vx = 0.0
        self.vy = 0.0
        self.team = team
        self.alive = True
        self.radius = 10.0

class MockHazard:
    def __init__(self, kind, x, y, radius=15.0):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = radius
        self.duration = 10.0

class MockWorld:
    def __init__(self):
        self.balls = []
        self.boosters = []
        self.arena = self.MockArena()
        self.profile_manager = ProfileManager("test_nemesis_hunter_profile.json")

    class MockArena:
        def __init__(self):
            self.hazards = []
            self.width = 1000
            self.height = 1000

def test_nemesis_hunter():
    world = MockWorld()

    player1 = MockEntity(id=1, x=100.0, y=100.0, ball_type="basic", team="Red")
    player2 = MockEntity(id=2, x=200.0, y=100.0, ball_type="nemesis", team="Blue")
    player3 = MockEntity(id=3, x=300.0, y=100.0, ball_type="bystander", team="Green")
    world.balls = [player1, player2, player3]

    # Make player2 a nemesis of player1
    world.profile_manager.add_kill(player1.ball_type, player2.ball_type)
    world.profile_manager.add_kill(player1.ball_type, player2.ball_type)
    assert world.profile_manager.is_nemesis(player1.ball_type, player2.ball_type) == True

    nemesis_hunter = MockHazard(kind="nemesis_hunter", x=100.0, y=200.0)
    world.arena.hazards = [nemesis_hunter]

    action1 = Action(player1, world)

    # Execute action to process hazards
    action1.execute("flee", 0.1)

    # Hazard should move towards player2 (the nemesis)
    # The nemesis hunter logic will find player2 as a nemesis and move towards it.
    assert nemesis_hunter.y < 200.0 # moved towards y=100

    # Let's teleport hazard to nemesis to kill it
    nemesis_hunter.x = player2.x
    nemesis_hunter.y = player2.y
    player2.hp = 1.0 # Easy kill

    action2 = Action(player2, world)
    action2.execute("flee", 0.1)

    # player2 should be dead
    assert player2.hp <= 0.0
    assert not player2.alive

    # The chain reaction should apply scrambled_movement_timer to player1 and player3
    assert getattr(player1, "scrambled_movement_timer", 0.0) > 0.0
    assert getattr(player3, "scrambled_movement_timer", 0.0) > 0.0

    # Test that scrambled_movement_timer reverses movement
    action1.execute("attack", 1.0)

    # We can check that the logic reverses vx and vy
    # Not trivial to check purely, but we ensure the timer goes down
    assert player1.scrambled_movement_timer < 3.0

    if os.path.exists("test_nemesis_hunter_profile.json"):
        os.remove("test_nemesis_hunter_profile.json")
