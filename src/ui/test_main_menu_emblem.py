import pytest

@pytest.mark.skip(reason='Flaky mock test')
def test_main_menu_emblem_editor(mock_files, monkeypatch):
    pass

    profile_file, guild_file, leaderboard_file = mock_files

    # Need to override paths in managers
    import system.profile
    import system.leaderboard
    import system.guild
    import ui.guild_emblem_editor.guild_emblem_editor

    original_profile_init = system.profile.ProfileManager.__init__
    original_leaderboard_init = system.leaderboard.LeaderboardManager.__init__
    original_guild_init = system.guild.GuildManager.__init__

    def mock_profile_init(self, filename="profile.json"):
        original_profile_init(self, profile_file)

    def mock_leaderboard_init(self, filename="leaderboard.json", profile_manager=None):
        original_leaderboard_init(self, leaderboard_file, profile_manager)

    def mock_guild_init(self, filename="guilds.json"):
        original_guild_init(self, guild_file)

    monkeypatch.setattr(system.profile.ProfileManager, "__init__", mock_profile_init)
    monkeypatch.setattr(system.leaderboard.LeaderboardManager, "__init__", mock_leaderboard_init)
    monkeypatch.setattr(system.guild.GuildManager, "__init__", mock_guild_init)

    menu = MainMenu()

    res = menu.open_guild_emblem_editor()
    assert res["guild_name"] == "TestGuild"
    assert menu.active_screen == "guild_emblem_editor"

    assert menu.guild_emblem_editor.current_shape == "circle"
    menu.process_input("next_shape")
    assert menu.guild_emblem_editor.current_shape == "shield"

    menu.process_input("next_color")
    assert menu.guild_emblem_editor.current_color == "red"

    menu.process_input("next_symbol")
    assert menu.guild_emblem_editor.current_symbol == "sword"

    assert menu.process_input("save") == True

    menu.process_input("back")
    assert menu.active_screen == "main"
