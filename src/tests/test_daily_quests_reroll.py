import os
import pytest
from system.lobby import PreGameLobby
from system.profile import ProfileManager

@pytest.fixture
def profile_manager():
    # Setup test profile manager
    pm = ProfileManager(filename="test_profile_reroll.json")
    pm.data = pm.load() # Start fresh or load basic
    # Give some mutator tokens
    pm.data["mutator_tokens"] = 2
    # Ensure quests list is empty
    pm.data["quests"] = []

    yield pm

    # Teardown
    if os.path.exists("test_profile_reroll.json"):
        os.remove("test_profile_reroll.json")

def test_reroll_daily_quest_success(profile_manager):
    lobby = PreGameLobby()

    # Assign some quests manually
    lobby.assign_daily_quests_to_profile(profile_manager)
    quests_before = profile_manager.get_quests()

    assert len(quests_before) == 3

    first_quest_desc = quests_before[0]["description"]

    # Reroll the first quest
    assert lobby.reroll_daily_quest(profile_manager, 0) == True

    quests_after = profile_manager.get_quests()

    # Mutator token should be deducted
    assert profile_manager.data["mutator_tokens"] == 1

    # The first quest should be different
    assert quests_after[0]["description"] != first_quest_desc

    # It should not match the other existing quests
    assert quests_after[0]["description"] != quests_after[1]["description"]
    assert quests_after[0]["description"] != quests_after[2]["description"]

def test_reroll_daily_quest_failure_no_tokens(profile_manager):
    lobby = PreGameLobby()

    lobby.assign_daily_quests_to_profile(profile_manager)
    quests_before = profile_manager.get_quests()

    # Remove all tokens
    profile_manager.data["mutator_tokens"] = 0

    first_quest_desc = quests_before[0]["description"]

    # Attempt to reroll
    assert lobby.reroll_daily_quest(profile_manager, 0) == False

    quests_after = profile_manager.get_quests()

    # Ensure quest didn't change
    assert quests_after[0]["description"] == first_quest_desc

def test_reroll_daily_quest_failure_invalid_index(profile_manager):
    lobby = PreGameLobby()

    lobby.assign_daily_quests_to_profile(profile_manager)

    # Attempt to reroll out of bounds index
    assert lobby.reroll_daily_quest(profile_manager, 99) == False
    assert lobby.reroll_daily_quest(profile_manager, -1) == False

    # Mutator tokens should not be deducted
    assert profile_manager.data["mutator_tokens"] == 2
