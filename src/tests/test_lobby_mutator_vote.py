from system.lobby import PreGameLobby
from system.profile import ProfileManager
import os

def test_mutator_vote_system():
    lobby = PreGameLobby()
    profile = ProfileManager(filename="test_profile_mutator_vote.json")
    profile.data["skill_points"] = 100

    # Test basic vote
    assert lobby.cast_mutator_vote("player1", "low_gravity", profile) is True
    assert lobby.selections["mutator_votes"]["low_gravity"] == 1

    # Test paid vote
    assert lobby.cast_mutator_vote("player2", "double_damage", profile, spend_currency=True) is True
    assert lobby.selections["mutator_votes"]["double_damage"] == 3
    assert profile.data["skill_points"] == 50

    # Test vote with insufficient funds
    assert lobby.cast_mutator_vote("player3", "high_speed", profile, spend_currency=True) is True
    assert lobby.selections["mutator_votes"]["high_speed"] == 3
    assert profile.data["skill_points"] == 0

    assert lobby.cast_mutator_vote("player4", "vampirism", profile, spend_currency=True) is False

    # Get winner
    assert lobby.get_winning_mutator() in ["double_damage", "high_speed"]

    # Add more votes to break tie
    lobby.cast_mutator_vote("player5", "double_damage", profile)
    assert lobby.get_winning_mutator() == "double_damage"

    if os.path.exists("test_profile_mutator_vote.json"):
        os.remove("test_profile_mutator_vote.json")

def test_mutator_vote_system_with_mutator_tokens():
    lobby = PreGameLobby()
    profile = ProfileManager(filename="test_profile_mutator_tokens.json")
    profile.data["skill_points"] = 100
    profile.data["mutator_tokens"] = 2

    # Test vote with mutator token
    assert lobby.cast_mutator_vote("player1", "global_hp", profile, spend_currency=True, currency_type="mutator_tokens") is True
    assert lobby.selections["mutator_votes"]["global_hp"] == 5
    assert profile.data["mutator_tokens"] == 1

    # Test vote with mutator token but insufficient balance
    lobby = PreGameLobby() # reset lobby state
    profile.data["mutator_tokens"] = 0
    assert lobby.cast_mutator_vote("player1", "global_cooldown", profile, spend_currency=True, currency_type="mutator_tokens") is False
    assert "global_cooldown" not in lobby.selections.get("mutator_votes", {})

    # Test fallback
    assert lobby.cast_mutator_vote("player2", "global_cooldown", profile, spend_currency=True, currency_type="invalid_currency") is False

    if os.path.exists("test_profile_mutator_tokens.json"):
        os.remove("test_profile_mutator_tokens.json")

def test_pinball_mutator_combination():
    lobby = PreGameLobby()
    profile = ProfileManager(filename="test_profile_pinball.json")
    profile.data["skill_points"] = 1000

    lobby.cast_mutator_vote("player1", "high_speed", profile, spend_currency=True)
    lobby.cast_mutator_vote("player2", "bouncy_walls", profile, spend_currency=True)
    lobby.cast_mutator_vote("player3", "high_speed", profile)
    lobby.cast_mutator_vote("player4", "low_gravity", profile)

    # Votes: high_speed: 4, bouncy_walls: 3, low_gravity: 1
    # Top 2 are high_speed and bouncy_walls -> should trigger secret mutator
    assert lobby.get_winning_mutator() == "pinball_mutator"

    if os.path.exists("test_profile_pinball.json"):
        os.remove("test_profile_pinball.json")
