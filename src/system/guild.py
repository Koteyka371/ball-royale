import json

class GuildManager:
    def __init__(self, filename="guilds.json"):
        self.filename = filename
        self.data = self.load()

    def load(self):
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                if "guilds" not in data:
                    data["guilds"] = {}
                if "territories" not in data:
                    data["territories"] = {}
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            return {"guilds": {}, "territories": {}}

    def save(self):
        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=4)

    def create_guild(self, guild_name, creator_id):
        if guild_name in self.data["guilds"]:
            return False

        self.data["guilds"][guild_name] = {
            "members": [creator_id],
            "resources": 0,
            "buffs": {
                "bonus_hp": 0,
                "bonus_speed": 0,
                "bonus_damage": 0
            },
            "gvg_points": 0,
            "chat_history": [],
            "vault": [],
            "hq": {
                "statues": [],
                "banners": [],
                "arena": "basic"
            }
        }
        self.save()
        return True

    def join_guild(self, guild_name, player_id):
        if guild_name in self.data["guilds"]:
            guild = self.data["guilds"][guild_name]
            if player_id not in guild["members"]:
                guild["members"].append(player_id)
                self.save()
                return True
        return False

    def leave_guild(self, guild_name, player_id):
        if guild_name in self.data["guilds"]:
            guild = self.data["guilds"][guild_name]
            if player_id in guild["members"]:
                guild["members"].remove(player_id)
                if len(guild["members"]) == 0:
                    del self.data["guilds"][guild_name]
                self.save()
                return True
        return False

    def donate_resources(self, guild_name, amount):
        if guild_name in self.data["guilds"]:
            self.data["guilds"][guild_name]["resources"] += amount
            self.save()
            return True
        return False

    def unlock_buff(self, guild_name, buff_name, cost):
        if guild_name in self.data["guilds"]:
            guild = self.data["guilds"][guild_name]
            if guild["resources"] >= cost and buff_name in guild["buffs"]:
                guild["resources"] -= cost
                guild["buffs"][buff_name] += 1
                self.save()
                return True
        return False

    def get_guild_buffs(self, guild_name):
        if guild_name in self.data["guilds"]:
            return self.data["guilds"][guild_name]["buffs"]
        return {"bonus_hp": 0, "bonus_speed": 0, "bonus_damage": 0}

    def record_gvg_match(self, guild1_name, guild2_name, winner_name):
        if guild1_name in self.data["guilds"] and guild2_name in self.data["guilds"]:
            if winner_name == guild1_name:
                self.data["guilds"][guild1_name]["gvg_points"] += 10
                self.data["guilds"][guild2_name]["gvg_points"] = max(0, self.data["guilds"][guild2_name]["gvg_points"] - 5)
            elif winner_name == guild2_name:
                self.data["guilds"][guild2_name]["gvg_points"] += 10
                self.data["guilds"][guild1_name]["gvg_points"] = max(0, self.data["guilds"][guild1_name]["gvg_points"] - 5)
            self.save()
            return True
        return False

    def get_guild(self, guild_name):
        return self.data["guilds"].get(guild_name)

    def send_chat_message(self, guild_name, sender_id, message):
        if guild_name in self.data["guilds"]:
            self.data["guilds"][guild_name].setdefault("chat_history", []).append({
                "sender": sender_id,
                "message": message
            })
            self.save()
            return True
        return False

    def get_chat_history(self, guild_name):
        if guild_name in self.data["guilds"]:
            return self.data["guilds"][guild_name].get("chat_history", [])
        return []

    def get_guild_leaderboard(self):
        guilds = []
        for name, info in self.data["guilds"].items():
            guilds.append({
                "name": name,
                "gvg_points": info.get("gvg_points", 0)
            })
        guilds.sort(key=lambda x: x["gvg_points"], reverse=True)
        return guilds

    def deposit_item(self, guild_name, item):
        if guild_name in self.data["guilds"]:
            self.data["guilds"][guild_name].setdefault("vault", []).append(item)
            self.save()
            return True
        return False

    def withdraw_item(self, guild_name, item):
        if guild_name in self.data["guilds"]:
            vault = self.data["guilds"][guild_name].setdefault("vault", [])
            if item in vault:
                vault.remove(item)
                self.save()
                return True
        return False

    def capture_territory(self, guild_name, territory_name):
        if guild_name in self.data["guilds"]:
            if "territories" not in self.data:
                self.data["territories"] = {}
            self.data["territories"][territory_name] = guild_name
            self.save()
            return True
        return False

    def get_territories(self, guild_name):
        if "territories" not in self.data:
            return []
        return [t for t, owner in self.data["territories"].items() if owner == guild_name]

    def collect_passive_resources(self):
        if "territories" not in self.data:
            return
        # Each territory grants 5 resources to its owner
        for territory, owner in self.data["territories"].items():
            if owner in self.data["guilds"]:
                self.data["guilds"][owner]["resources"] += 5
        self.save()

    def unlock_hq_item(self, guild_name, category, item_name, cost):
        if guild_name in self.data["guilds"]:
            guild = self.data["guilds"][guild_name]
            if "hq" not in guild:
                guild["hq"] = {"statues": [], "banners": [], "arena": "basic"}
            if guild["resources"] >= cost:
                if category in ["statues", "banners"]:
                    if item_name not in guild["hq"][category]:
                        guild["resources"] -= cost
                        guild["hq"][category].append(item_name)
                        self.save()
                        return True
                elif category == "arena":
                    if guild["hq"]["arena"] != item_name:
                        guild["resources"] -= cost
                        guild["hq"]["arena"] = item_name
                        self.save()
                        return True
        return False

    def get_hq_details(self, guild_name):
        if guild_name in self.data["guilds"]:
            return self.data["guilds"][guild_name].get("hq", {"statues": [], "banners": [], "arena": "basic"})
        return {"statues": [], "banners": [], "arena": "basic"}
