import pytest
from system.profile import ProfileManager
from ui.bounty_terminal.bounty_terminal import BountyTerminalUI

def test_bounty_terminal_empty():
    pm = ProfileManager("test_bounty_terminal.json")
    pm.data["active_bounties"] = {}

    ui = BountyTerminalUI(pm)
    output = ui.render_ui()

    assert "--- Active High-Value Bounties ---" in output
    assert "No active bounties at this time." in output

def test_bounty_terminal_with_bounties():
    pm = ProfileManager("test_bounty_terminal2.json")
    pm.data["prestige_tokens"] = 100
    pm.data["skill_points"] = 1000

    pm.place_player_bounty("player_A", 5, "prestige_tokens", "local_player")
    pm.place_player_bounty("player_B", 500, "skill_points", "enemy_X")
    pm.place_player_bounty("player_C", 10, "prestige_tokens", "enemy_Y")

    ui = BountyTerminalUI(pm)
    output = ui.render_ui()

    lines = output.split("\n")
    assert lines[0] == "--- Active High-Value Bounties ---"

    # Should be sorted by reward descending
    assert "TARGET: player_B" in lines[1]
    assert "REWARD: " in lines[1]
    assert "PLACED BY: enemy_X" in lines[1]

    assert "TARGET: player_C" in lines[2]
    assert "REWARD: " in lines[2]
    assert "PLACED BY: enemy_Y" in lines[2]

    assert "TARGET: player_A" in lines[3]
    assert "REWARD: " in lines[3]
    assert "PLACED BY: local_player" in lines[3]
