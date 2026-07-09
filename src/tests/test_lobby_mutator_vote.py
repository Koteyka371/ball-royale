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
