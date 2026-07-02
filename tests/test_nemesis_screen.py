import pytest
from system.profile import ProfileManager
from ui.nemesis_screen.nemesis_screen import NemesisScreen
import os
import json

def test_nemesis_screen_render():
    if os.path.exists("test_nemesis_profile_ui.json"):
        os.remove("test_nemesis_profile_ui.json")

    pm = ProfileManager("test_nemesis_profile_ui.json")
    pm.data["nemeses"] = {
        "warrior": {"tank": 2, "scout": 1},
        "mage": {"warrior": 5}
    }

    screen = NemesisScreen(pm)
    output = screen.render_ui()

    assert "--- Nemeses ---" in output
    assert "warrior vs tank: 2 kills" in output
    assert "mage vs warrior: 5 kills" in output
    assert "warrior vs scout" not in output

    if os.path.exists("test_nemesis_profile_ui.json"):
        os.remove("test_nemesis_profile_ui.json")

def test_nemesis_screen_empty():
    if os.path.exists("test_nemesis_profile_empty.json"):
        os.remove("test_nemesis_profile_empty.json")

    pm = ProfileManager("test_nemesis_profile_empty.json")

    screen = NemesisScreen(pm)
    output = screen.render_ui()

    assert "--- Nemeses ---" in output
    assert "No nemeses yet." in output

    if os.path.exists("test_nemesis_profile_empty.json"):
        os.remove("test_nemesis_profile_empty.json")
