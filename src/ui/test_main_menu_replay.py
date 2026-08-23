import pytest
import os
import json
from ui.main_menu import MainMenu

@pytest.fixture
def mock_files(tmp_path):
    profile_file = tmp_path / "profile.json"
    guild_file = tmp_path / "guilds.json"
    leaderboard_file = tmp_path / "leaderboard.json"

    with open(profile_file, "w") as f:
        json.dump({"username": "player1"}, f)

    with open(guild_file, "w") as f:
        json.dump({
            "guilds": {
                "TestGuild": {
                    "members": ["player1"],
                }
            }
        }, f)

    with open(leaderboard_file, "w") as f:
        json.dump({
            "current_season": 1,
            "top_replays": {
                "player_1": str(tmp_path / "replay_player_1.json")
            }
        }, f)

    with open(tmp_path / "replay_player_1.json", "w") as f:
        json.dump({
            "version": "1.0",
            "frames": [
                {"tick": 1, "entities": [], "events": []},
                {"tick": 2, "entities": [], "events": []}
            ]
        }, f)

    return str(profile_file), str(guild_file), str(leaderboard_file)

def test_main_menu_replay_controls(mock_files, monkeypatch):
    profile_file, guild_file, leaderboard_file = mock_files

    from system import profile
    from system import leaderboard
    from system import guild

    original_profile_init = profile.ProfileManager.__init__
    original_leaderboard_init = leaderboard.LeaderboardManager.__init__
    original_guild_init = guild.GuildManager.__init__

    def mock_profile_init(self, filename="profile.json"):
        original_profile_init(self, profile_file)

    def mock_leaderboard_init(self, filename="leaderboard.json", profile_manager=None):
        original_leaderboard_init(self, leaderboard_file, profile_manager)

    def mock_guild_init(self, filename="guilds.json"):
        original_guild_init(self, guild_file)

    monkeypatch.setattr(profile.ProfileManager, "__init__", mock_profile_init)
    monkeypatch.setattr(leaderboard.LeaderboardManager, "__init__", mock_leaderboard_init)
    monkeypatch.setattr(guild.GuildManager, "__init__", mock_guild_init)

    menu = MainMenu()

    # Open screen
    menu.open_replay_screen()
    assert menu.active_screen == "replay_screen"

    # Watch replay
    res = menu.process_input("watch", "player_1")
    assert res == "watching player_1"
    assert menu.active_replay is not None
    assert menu.active_replay_id == "player_1"
    assert menu.active_replay.playback_speed == 1.0

    # Fast forward
    res = menu.process_input("fast_forward", 2.0)
    assert res is True
    assert menu.active_replay.playback_speed == 2.0

    res = menu.process_input("fast_forward", -4.0)
    assert res is True
    assert menu.active_replay.playback_speed == 4.0 # absolute value

    # Rewind
    res = menu.process_input("rewind", 1.0)
    assert res is True
    assert menu.active_replay.playback_speed == -1.0

    res = menu.process_input("rewind", -3.0)
    assert res is True
    assert menu.active_replay.playback_speed == -3.0 # negative absolute value

    # Set speed
    res = menu.process_input("set_speed", 0.5)
    assert res is True
    assert menu.active_replay.playback_speed == 0.5

    # Take control
    res = menu.process_input("take_control")
    assert isinstance(res, dict)
    assert res["action"] == "resume_from_state"
    assert "state" in res
    assert res["state"]["tick"] == 1
    assert not menu.active_replay.is_playing

    # Back
    res = menu.process_input("back")
    assert res is True
    assert menu.active_screen == "main"
    assert menu.active_replay is None
    assert menu.active_replay_id is None
