class NemesisScreen:
    def __init__(self, profile_manager, theme="Genesis"):
        self.profile_manager = profile_manager
        self.theme = theme

    def _get_flourish(self):
        flourishes = {
            "Genesis": "A calm, neutral genesis light illuminates the screen.",
            "Inferno": "Ember particles float across the screen, radiating heat.",
            "Frost": "A gentle snowfall and frost frames the edges of the UI.",
            "Void": "Dark purple energy swirls in the background.",
            "Celestial": "Golden stars twinkle in a bright, heavenly backdrop.",
            "Abyssal": "Deep-sea ambient particle effects bubble upward.",
            "Ethereal": "Ghostly green and blue wisps drift aimlessly.",
            "Phantom": "Shadowy silhouettes fade in and out of the periphery.",
            "Eclipse": "A ring of light is blocked by absolute darkness.",
            "Radiance": "Blinding rays of golden light shine from the center."
        }
        return flourishes.get(self.theme, "")

    def render_ui(self):
        output = ["--- Nemeses ---"]
        flourish = self._get_flourish()
        if flourish:
            output.append(f"[{self.theme} Theme] {flourish}")

        nemeses = self.profile_manager.data.get("nemeses", {})

        has_nemesis = False
        for killer_type, victims in nemeses.items():
            for victim_type, count in victims.items():
                if count >= 2:
                    output.append(f"{killer_type} vs {victim_type}: {count} kills")
                    has_nemesis = True

        enforcers = self.profile_manager.data.get("enforcers", {})
        if enforcers:
            output.append("\n--- Enforcer Pledges ---")
            for player, nemesis in enforcers.items():
                output.append(f"{player} is an Enforcer for {nemesis}")

        if not has_nemesis:
            output.append("No nemeses yet.")

        return "\n".join(output)
