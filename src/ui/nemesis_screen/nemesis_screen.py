class NemesisScreen:
    def __init__(self, profile_manager, leaderboard_manager=None):
        self.profile_manager = profile_manager
        self.leaderboard_manager = leaderboard_manager

    def render_ui(self):
        season_theme = "Genesis"
        if self.leaderboard_manager:
            season = self.leaderboard_manager.data.get("current_season", 1)
            season_theme = self.leaderboard_manager.get_theme(season)

        flourishes = {
            "Genesis": "* A soft, pale light gently pulses *",
            "Inferno": "* Embers drift lazily across the screen *",
            "Frost": "* Light snowflakes fall quietly *",
            "Void": "* Dark energy crackles silently *",
            "Celestial": "* Stars twinkle in the background *",
            "Abyssal": "* Deep-sea ambient particles swirling *",
            "Ethereal": "* Spectral wisps float around *",
            "Phantom": "* Ghostly shadows shift in the corners *",
            "Eclipse": "* The edge of the screen darkens mysteriously *",
            "Radiance": "* A warm, golden aura surrounds the UI *"
        }

        output = [f"--- Nemeses --- [{season_theme} Season]"]
        flourish = flourishes.get(season_theme, "")
        if flourish:
            output.append(flourish)

        nemeses = self.profile_manager.data.get("nemeses", {})

        has_nemesis = False
        for killer_type, victims in nemeses.items():
            for victim_type, count in victims.items():
                if count >= 2:
                    output.append(f"{killer_type} vs {victim_type}: {count} kills")
                    has_nemesis = True

        if not has_nemesis:
            output.append("No nemeses yet.")

        return "\n".join(output)
