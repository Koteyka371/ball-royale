import pytest
from ai.game_modes import GameMode

class MockProfileManager:
    def __init__(self):
        self.skill_points_added = 0
        self.bounties = {}

    def get_player_bounties(self):
        return self.bounties

    def add_skill_points(self, points):
        self.skill_points_added += points

class MockWorld:
    def __init__(self):
        self.profile_manager = MockProfileManager()
        self.events = []

    def add_event(self, type_, data):
        self.events.append((type_, data))

class MockBall:
    def __init__(self, id, kill_bounty=0):
        self.id = id
        self.kill_bounty = kill_bounty
        self.is_bounty = False
        self.speed_boost_timer = 0.0

def test_kill_streak_bounty():
    mode = GameMode()
    world = MockWorld()

    # Killer has no initial bounty
    killer = MockBall(id="player1")
    # Target has a bounty of 3
    target = MockBall(id="player2", kill_bounty=3)

    # Killer gets a kill
    mode.on_ball_died(world, target, killer=killer)

    # Killer should gain 1 kill bounty and become a bounty target
    assert killer.kill_bounty == 1
    assert killer.is_bounty == True

    # Killer should be rewarded 15 * 3 = 45 skill points
    assert world.profile_manager.skill_points_added == 45

    # Killer should gain a speed boost of 5.0 for killing a bounty target
    assert killer.speed_boost_timer == 5.0

    # Check that event was fired
    assert any(e[0] == "bounty_claimed" and "player1" in e[1]["message"] and "45" in e[1]["message"] and "speed boost" in e[1]["message"] for e in world.events)

    # Killer gets killed by a new player
    new_killer = MockBall(id="player3")
    mode.on_ball_died(world, killer, killer=new_killer)

    # New killer should gain 1 kill bounty
    assert new_killer.kill_bounty == 1

    # New killer should be rewarded 15 * 1 = 15 skill points
    assert world.profile_manager.skill_points_added == 45 + 15

    # New killer should gain a speed boost of 5.0
    assert new_killer.speed_boost_timer == 5.0
