from ui.prestige_shop.prestige_shop import PrestigeShop
from ui.nemesis_screen.nemesis_screen import NemesisScreen
from system.profile import ProfileManager

class MainMenu:
    def __init__(self):
        self.profile_manager = ProfileManager("profile.json")
        self.prestige_shop = PrestigeShop(self.profile_manager)
        self.nemesis_screen = NemesisScreen(self.profile_manager)
        self.active_screen = "main"

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
