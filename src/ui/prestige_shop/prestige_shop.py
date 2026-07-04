class PrestigeShop:
    def __init__(self, profile_manager):
        self.profile_manager = profile_manager

    def get_available_upgrades(self):
        return {
            "permanent_hp": {"cost": 5, "description": "Increases max HP permanently"},
            "permanent_speed": {"cost": 5, "description": "Increases base speed permanently"},
            "permanent_damage": {"cost": 5, "description": "Increases base damage permanently"},
            "mutator_unlocked": {"cost": 15, "description": "Unlocks custom match mutators (run mutators)"},
            "starting_artifact_shield": {"cost": 10, "description": "Start matches with a shield artifact"},
            "starting_artifact_dash": {"cost": 10, "description": "Start matches with a dash artifact"},
            "unlock_time_mage": {"cost": 25, "description": "Unlocks the Time-Mage ball archetype"},
            "shield_capacity_up": {"cost": 10, "description": "Increases reflect shield capacity by 20"},
            "shield_duration_up": {"cost": 10, "description": "Increases reflect shield duration by 1s"}
        }

    def buy_upgrade(self, upgrade_name):
        upgrades = self.get_available_upgrades()
        if upgrade_name not in upgrades:
            return False
        cost = upgrades[upgrade_name]["cost"]
        return self.profile_manager.buy_prestige_upgrade(upgrade_name, cost)

    def render_ui(self):
        # A simple terminal/text-based UI representation for the python mock environment
        output = ["--- Prestige Shop ---"]
        upgrades = self.get_available_upgrades()
        current_tokens = self.profile_manager.data.get("prestige_tokens", 0)
        output.append(f"Tokens available: {current_tokens}")

        for name, data in upgrades.items():
            output.append(f"{name} - {data['description']} (Cost: {data['cost']})")
        return "\n".join(output)
