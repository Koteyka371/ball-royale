import json
import os

class GuildWarsBaseBuilding:
    def __init__(self, guild_manager):
        self.guild_manager = guild_manager
        self.active_guild = None
        self.defenses = []
        self.available_defenses = {
            "turret": {"cost": 100, "hp": 500, "damage": 50},
            "wall": {"cost": 50, "hp": 1000, "damage": 0},
            "trap": {"cost": 25, "hp": 100, "damage": 200}
        }

    def set_guild(self, guild_name):
        self.active_guild = guild_name
        self.load_defenses()

    def load_defenses(self):
        if not self.active_guild: return
        guild_data = self.guild_manager.data.get("guilds", {}).get(self.active_guild, {})
        self.defenses = guild_data.get("defenses", [])

    def save_defenses(self):
        if not self.active_guild: return
        if self.active_guild not in self.guild_manager.data.get("guilds", {}):
            return
        self.guild_manager.data["guilds"][self.active_guild]["defenses"] = self.defenses
        self.guild_manager.save()

    def build_defense(self, defense_type, x, y):
        if not self.active_guild: return False
        if defense_type not in self.available_defenses: return False

        cost = self.available_defenses[defense_type]["cost"]
        guild_data = self.guild_manager.data.get("guilds", {}).get(self.active_guild, {})
        resources = guild_data.get("resources", 0)

        if resources >= cost:
            self.guild_manager.data["guilds"][self.active_guild]["resources"] = resources - cost
            new_defense = {
                "type": defense_type,
                "x": x,
                "y": y,
                "hp": self.available_defenses[defense_type]["hp"]
            }
            self.defenses.append(new_defense)
            self.save_defenses()
            return True
        return False

    def remove_defense(self, index):
        if not self.active_guild: return False
        if 0 <= index < len(self.defenses):
            self.defenses.pop(index)
            self.save_defenses()
            return True
        return False
