import pytest
import os
from ui.main_menu import MainMenu
from system.profile import ProfileManager

def test_weekend_mutator_vote():
    # Setup
    menu = MainMenu()
    menu.profile_manager.data["prestige_tokens"] = 5
    menu.profile_manager.save()

    # Force weekend open
    assert menu.active_screen == "main"
    menu.active_screen = "weekend_vote"

    # Vote for 10x_speed
    res = menu.process_input("vote", "10x_speed")
    assert res is True
    assert menu.weekend_votes["10x_speed"] == 1
    assert menu.profile_manager.data["prestige_tokens"] == 4
    assert menu.active_weekend_event == "10x_speed"

    # Vote for lava_floor twice
    menu.process_input("vote", "lava_floor")
    menu.process_input("vote", "lava_floor")

    assert menu.weekend_votes["lava_floor"] == 2
    assert menu.profile_manager.data["prestige_tokens"] == 2
    assert menu.active_weekend_event == "lava_floor"

    # Test not enough tokens
    menu.profile_manager.data["prestige_tokens"] = 0
    res = menu.process_input("vote", "invisible_enemies")
    assert res is False
    assert menu.weekend_votes["invisible_enemies"] == 0

    # Cleanup
    if os.path.exists("profile.json"):
        os.remove("profile.json")
    if os.path.exists("leaderboard.json"):
        os.remove("leaderboard.json")
