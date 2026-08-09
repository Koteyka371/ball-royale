import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from system.lobby import PreGameLobby
from system.profile import ProfileManager
import datetime

def test_weekend_quest_assignment():
    lobby = PreGameLobby()

    # Test weekday (e.g. Wednesday 2023-11-01)
    quests_weekday = lobby.get_daily_quests("2023-11-01")
    weekend_quest_found = any(q["description"] == "Win a match with the active mutator" for q in quests_weekday)
    assert not weekend_quest_found, "Weekend quest should not be assigned on a weekday"

    # Test weekend (e.g. Saturday 2023-11-04)
    quests_weekend = lobby.get_daily_quests("2023-11-04")
    weekend_quest_found = any(q["description"] == "Win a match with the active mutator" for q in quests_weekend)
    assert weekend_quest_found, "Weekend quest should be assigned on a weekend"

    # Ensure reward is correct
    weekend_quest = next(q for q in quests_weekend if q["description"] == "Win a match with the active mutator")
    assert weekend_quest["reward"] == {"mutator_tokens": 5}

def test_assign_quests_to_profile_weekend():
    lobby = PreGameLobby()
    import tempfile; import os; profile = ProfileManager(os.path.join(tempfile.gettempdir(), "test_user"))
    profile.data["quests"] = []

    # Simulate assigning on a weekend
    lobby.assign_daily_quests_to_profile(profile, "2023-11-05")  # Sunday

    quests = profile.get_quests()
    assert any(q["description"] == "Win a match with the active mutator" for q in quests)
