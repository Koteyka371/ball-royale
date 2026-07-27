from ui.prestige_shop.prestige_shop import PrestigeShop
from ui.nemesis_screen.nemesis_screen import NemesisScreen
from ui.guild_emblem_editor.guild_emblem_editor import GuildEmblemEditor
from ui.guild_wars_base_building import GuildWarsBaseBuilding
from ui.clan_emissary_quests import ClanEmissary
from system.profile import ProfileManager
from system.leaderboard import LeaderboardManager

class MainMenu:
    def __init__(self):
        self.profile_manager = ProfileManager("profile.json")
        self.leaderboard_manager = LeaderboardManager("leaderboard.json", profile_manager=self.profile_manager)
        self.prestige_shop = PrestigeShop(self.profile_manager)
        self.clan_emissary = ClanEmissary(self.profile_manager)
        self.active_screen = "main"

        season = self.leaderboard_manager.data.get("current_season", 1)
        self.background_theme = self.leaderboard_manager.get_theme(season)
        self.background_color = self._get_theme_color(self.background_theme)


        self.nemesis_screen = NemesisScreen(self.profile_manager, self.background_theme)
        self.guild_emblem_editor = GuildEmblemEditor(self.profile_manager)
        self.guild_wars_base_building = GuildWarsBaseBuilding(self.profile_manager)

        self.weekend_options = ["10x_speed", "invisible_enemies", "lava_floor"]
        self.weekend_votes = {opt: 0 for opt in self.weekend_options}
        self.active_weekend_event = None

    def open_weekend_vote(self):
        self.active_screen = "weekend_vote"
        return True


    def _get_theme_color(self, theme):
        colors = {
            "Genesis": (200, 200, 200),
            "Inferno": (200, 50, 50),
            "Frost": (50, 150, 200),
            "Void": (50, 0, 100),
            "Celestial": (255, 255, 200),
            "Abyssal": (0, 0, 50),
            "Ethereal": (150, 255, 200),
            "Phantom": (100, 100, 150),
            "Eclipse": (50, 50, 50),
            "Radiance": (255, 200, 50)
        }
        return colors.get(theme, (0, 0, 0))




    def open_replay_screen(self):
        self.active_screen = "replay_screen"
        return self.leaderboard_manager.get_available_replays()

    def process_replay_input(self, action, *args):
        if action == "watch" and args:
            player_id = args[0]
            replay = self.leaderboard_manager.get_top_player_replay(player_id)
            if replay:
                # Mock opening replay
                return f"watching {player_id}"
            return "not found"
        elif action == "download" and args:
            player_id = args[0]
            replay = self.leaderboard_manager.get_top_player_replay(player_id)
            if replay:
                # Mock download
                return f"downloaded {player_id}"
            return "not found"
        elif action == "back":
            self.active_screen = "main"
            return True
        return False

    def open_nemesis_screen(self):
        self.active_screen = "nemesis"
        return self.nemesis_screen.render_ui()


    def open_guild_emblem_editor(self):
        self.active_screen = "guild_emblem_editor"
        return self.guild_emblem_editor.refresh_ui()

    def open_prestige_shop(self):
        self.active_screen = "prestige_shop"
        return self.prestige_shop.render_ui()


    def open_guild_wars_base_building(self):
        self.active_screen = "guild_wars_base_building"
        # We need to extract guild name from profile or dummy for now
        guild_name = "TestGuild"
        self.guild_wars_base_building.set_guild(guild_name)
        return True

    def open_clan_emissary(self):
        self.active_screen = "clan_emissary"
        return self.clan_emissary.render_ui()

    def process_input(self, action, *args):

        if self.active_screen == "weekend_vote":
            if action == "vote" and args:
                mode = args[0]
                if mode in self.weekend_options:
                    tokens = self.profile_manager.data.get("prestige_tokens", 0)
                    if tokens > 0:
                        self.profile_manager.data["prestige_tokens"] = tokens - 1
                        self.profile_manager.save()
                        self.weekend_votes[mode] += 1
                        self.active_weekend_event = max(self.weekend_votes.items(), key=lambda x: x[1])[0]
                        return True
                return False
            elif action == "back":
                self.active_screen = "main"
                return True



        if self.active_screen == "replay_screen":
            return self.process_replay_input(action, *args)



        if self.active_screen == "guild_wars_base_building":
            if action == "build" and args:
                defense_type, x, y = args[0], args[1], args[2]
                return self.guild_wars_base_building.build_defense(defense_type, x, y)
            elif action == "remove" and args:
                index = args[0]
                return self.guild_wars_base_building.remove_defense(index)
            elif action == "back":
                self.active_screen = "main"
                return True

        if self.active_screen == "guild_emblem_editor":
            if action == "save":
                return self.guild_emblem_editor.save_emblem()
            elif action == "next_shape":
                idx = self.guild_emblem_editor.available_shapes.index(self.guild_emblem_editor.current_shape)
                self.guild_emblem_editor.current_shape = self.guild_emblem_editor.available_shapes[(idx + 1) % len(self.guild_emblem_editor.available_shapes)]
                return True
            elif action == "next_color":
                idx = self.guild_emblem_editor.available_colors.index(self.guild_emblem_editor.current_color)
                self.guild_emblem_editor.current_color = self.guild_emblem_editor.available_colors[(idx + 1) % len(self.guild_emblem_editor.available_colors)]
                return True
            elif action == "next_symbol":
                idx = self.guild_emblem_editor.available_symbols.index(self.guild_emblem_editor.current_symbol)
                self.guild_emblem_editor.current_symbol = self.guild_emblem_editor.available_symbols[(idx + 1) % len(self.guild_emblem_editor.available_symbols)]
                return True
            elif action == "back":
                self.active_screen = "main"
                return True
            return False

        if self.active_screen == "nemesis":

            if action == "back":
                self.active_screen = "main"
                return True
            return False
        if self.active_screen == "prestige_shop":
            if action == "buy" and args:
                upgrade_name = args[0]
                success = self.prestige_shop.buy_upgrade(upgrade_name)
                return success
            elif action == "back":
                self.active_screen = "main"
                return True
        if self.active_screen == "clan_emissary":
            if action == "complete_quest" and args:
                quest_id = args[0]
                return self.clan_emissary.complete_quest(quest_id)
            elif action == "buy_item" and args:
                item_id = args[0]
                return self.clan_emissary.buy_item(item_id)
            elif action == "back":
                self.active_screen = "main"
                return True
        return False
