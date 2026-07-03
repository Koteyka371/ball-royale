import pytest
import json
import os
from ui.main_menu import MainMenu

def test_main_menu_background_theme():
    # Setup test leaderboard
    leaderboard_data = {
        "current_season": 2,
        "players": {}
    }
    # We need to temporarily point MainMenu to use our test leaderboard if possible
    # Alternatively, ensure we don't overwrite the actual leaderboard.json tracked file
    # We will backup existing leaderboard.json if it exists

    backup = None
    if os.path.exists("leaderboard.json"):
        with open("leaderboard.json", "r") as f:
            backup = f.read()

    with open("leaderboard.json", "w") as f:
        json.dump(leaderboard_data, f)

    menu = MainMenu()
    # Season 2 theme is "Inferno"
    assert menu.background_theme == "Inferno"
    assert menu.background_color == (200, 50, 50)

    # Test season 3 (Frost)
    leaderboard_data["current_season"] = 3
    with open("leaderboard.json", "w") as f:
        json.dump(leaderboard_data, f)

    menu2 = MainMenu()
    try:
        assert menu2.background_theme == "Frost"
        assert menu2.background_color == (50, 150, 200)
    finally:
        if os.path.exists("leaderboard.json"):
            os.remove("leaderboard.json")
        if backup is not None:
            with open("leaderboard.json", "w") as f:
                f.write(backup)
