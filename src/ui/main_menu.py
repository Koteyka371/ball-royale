from ui.prestige_shop.prestige_shop import PrestigeShop
from ui.nemesis_screen.nemesis_screen import NemesisScreen
from system.profile import ProfileManager
from system.leaderboard import LeaderboardManager

class MainMenu:
    def __init__(self):
        self.profile_manager = ProfileManager("profile.json")
        self.leaderboard_manager = LeaderboardManager("leaderboard.json", profile_manager=self.profile_manager)
        self.prestige_shop = PrestigeShop(self.profile_manager)
        self.nemesis_screen = NemesisScreen(self.profile_manager)
        self.active_screen = "main"

        season = self.leaderboard_manager.data.get("current_season", 1)
        self.background_theme = self.leaderboard_manager.get_theme(season)
        self.background_color = self._get_theme_color(self.background_theme)

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

    def open_nemesis_screen(self):
        self.active_screen = "nemesis"
        return self.nemesis_screen.render_ui()

    def open_prestige_shop(self):
        self.active_screen = "prestige_shop"
        return self.prestige_shop.render_ui()

    def process_input(self, action, *args):
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
        return False
