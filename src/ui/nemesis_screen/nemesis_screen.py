class NemesisScreen:
    def __init__(self, profile_manager):
        self.profile_manager = profile_manager

    def render_ui(self):
        output = ["--- Nemeses ---"]
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
