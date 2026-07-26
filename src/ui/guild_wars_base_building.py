class GuildWarsBaseBuildingUI:
    """
    UI representation for the Guild Wars Base Building interface.
    Allows players to spend resources to place turrets, walls, and traps.
    """
    def __init__(self):
        self.guild_resources = {
            "gold": 5000,
            "stone": 2000,
            "wood": 3000
        }
        self.costs = {
            "turret": {"gold": 500, "stone": 200},
            "wall": {"stone": 100, "wood": 50},
            "trap": {"gold": 100, "wood": 20}
        }
        self.placed_defenses = []

    def can_afford(self, defense_type):
        cost = self.costs.get(defense_type, {})
        for res, amount in cost.items():
            if self.guild_resources.get(res, 0) < amount:
                return False
        return True

    def place_defense(self, defense_type, x, y):
        if not self.can_afford(defense_type):
            return False

        # Deduct resources
        cost = self.costs.get(defense_type, {})
        for res, amount in cost.items():
            self.guild_resources[res] -= amount

        self.placed_defenses.append({
            "type": defense_type,
            "x": x,
            "y": y
        })
        return True

    def get_layout(self):
        return self.placed_defenses
