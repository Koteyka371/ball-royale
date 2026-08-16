class BountyTerminalUI:
    def __init__(self, profile_manager):
        self.profile_manager = profile_manager

    def render_ui(self):
        output = ["--- Active High-Value Bounties ---"]

        bounties = self.profile_manager.get_player_bounties()

        has_bounty = False

        # Sort by highest reward first
        sorted_bounties = sorted(bounties.items(), key=lambda item: item[1].get("reward", 0), reverse=True)

        for target, details in sorted_bounties:
            reward = details.get("reward", 0)
            if reward > 0:
                currency = details.get("currency", "tokens")
                placer = details.get("placer", "Unknown")
                output.append(f"TARGET: {target} | REWARD: {reward} {currency} | PLACED BY: {placer}")
                has_bounty = True

        if not has_bounty:
            output.append("No active bounties at this time.")

        return "\n".join(output)
