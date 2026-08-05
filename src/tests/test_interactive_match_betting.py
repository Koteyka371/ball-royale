import pytest
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from system.crowd_system import CrowdSystem

class MockProfileManager:
    def __init__(self):
        self.data = {"skill_points": 1000, "prestige_tokens": 10}

    def save(self):
        pass

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.events = []
        self.arena = MockArena()
        self.profile_manager = MockProfileManager()

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, id, team):
        self.id = id
        self.team = team
        self.alive = True
        self.ball_type = "player"

def test_interactive_match_betting():
    world = MockWorld()
    system = CrowdSystem(world)

    b1 = MockBall(1, "A")
    b2 = MockBall(2, "B")
    b3 = MockBall(3, "B")
    b4 = MockBall(4, "B")
    balls = [b1, b2, b3, b4]

    # Initialize match to set underdog
    system.tick(balls, [], 0)
    assert system.underdog_team == "A"

    # Bet on b1 with SP (Underdog)
    system.queue_external_command("viewer1", "!bet 1 100sp")
    system.tick(balls, [], 1)

    assert world.profile_manager.data["skill_points"] == 900
    assert len(system.active_bets) == 1
    assert system.active_bets[0]["currency"] == "skill_points"

    # Bet on b2 with PT (Normal team)
    system.queue_external_command("viewer2", "!bet 2 2pt")
    system.tick(balls, [], 2)

    assert world.profile_manager.data["prestige_tokens"] == 8
    assert len(system.active_bets) == 2

    # Make team B win (Normal multiplier 1.5x)
    b1.alive = False
    system.tick(balls, [], 3)

    assert system.match_ended == True
    # Viewer 2 won 2 * 1.5 = 3 PT -> 8 + 3 = 11
    # Plus, the team that wins isn't the underdog, wait, if the team isn't underdog does the winner team get any base prestige?
    # Ah, the crowd system gives 10 prestige tokens if UNDERDOG wins. Here team B won, so no bonus 10.
    assert world.profile_manager.data["prestige_tokens"] == 11
    # Viewer 1 lost 100 SP, stays at 900
    assert world.profile_manager.data["skill_points"] == 900

    # Test Underdog multiplier (3.0x)
    world = MockWorld()
    system = CrowdSystem(world)

    b1 = MockBall(1, "A")
    b2 = MockBall(2, "B")
    b3 = MockBall(3, "B")
    balls = [b1, b2, b3]

    system.tick(balls, [], 0)
    assert system.underdog_team == "A"

    system.queue_external_command("viewer1", "!bet 1 100")
    system.tick(balls, [], 1)

    # Defaults to skill_points
    assert world.profile_manager.data["skill_points"] == 900

    b2.alive = False
    b3.alive = False
    system.tick(balls, [], 2)

    assert system.match_ended == True
    # Won 100 * 3.0 = 300 SP -> 900 + 300 = 1200
    assert world.profile_manager.data["skill_points"] == 1200
    # And because underdog won, profile manager gets +10 prestige tokens
    assert world.profile_manager.data["prestige_tokens"] == 20
