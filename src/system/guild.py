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
                for guild in data["guilds"].values():
                    if "hq" not in guild:
                        guild["hq"] = {
                            "statues": [],
                            "banners": [],
                            "training_arena_unlocked": False
                        }
                    if "guild_xp" not in guild:
                        guild["guild_xp"] = 0
                    if "perks" not in guild:
                        guild["perks"] = []
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
            "guild_xp": 0,
            "perks": [],
            "chat_history": [],
            "vault": [],
            "boss_progress": {},
            "hq": {
                "statues": [],
                "banners": [],
                "training_arena_unlocked": False
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
                self.data["guilds"][guild1_name]["guild_xp"] += 50
                self.data["guilds"][guild2_name]["gvg_points"] = max(0, self.data["guilds"][guild2_name]["gvg_points"] - 5)
                self.data["guilds"][guild2_name]["guild_xp"] += 10
            elif winner_name == guild2_name:
                self.data["guilds"][guild2_name]["gvg_points"] += 10
                self.data["guilds"][guild2_name]["guild_xp"] += 50
                self.data["guilds"][guild1_name]["gvg_points"] = max(0, self.data["guilds"][guild1_name]["gvg_points"] - 5)
                self.data["guilds"][guild1_name]["guild_xp"] += 10
            self.save()
            return True
        return False

    def unlock_perk(self, guild_name, perk_name, cost, required_perk=None):
        if guild_name in self.data["guilds"]:
            guild = self.data["guilds"][guild_name]
            if guild["guild_xp"] >= cost:
                if perk_name not in guild.get("perks", []):
                    if required_perk is None or required_perk in guild.get("perks", []):
                        guild["guild_xp"] -= cost
                        guild.setdefault("perks", []).append(perk_name)
                        self.save()
                        return True
        return False

    def get_guild_perks(self, guild_name):
        if guild_name in self.data["guilds"]:
            return self.data["guilds"][guild_name].get("perks", [])
        return []

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

    def record_boss_damage(self, guild_name, damage, week_id):
        if guild_name in self.data["guilds"]:
            guild = self.data["guilds"][guild_name]
            if "boss_progress" not in guild:
                guild["boss_progress"] = {}
            if week_id not in guild["boss_progress"]:
                guild["boss_progress"][week_id] = {"damage_dealt": 0.0, "claimed_by": []}
            guild["boss_progress"][week_id]["damage_dealt"] += damage
            self.save()
            return True
        return False

    def check_boss_defeated(self, guild_name, week_id, required_damage):
        if guild_name in self.data["guilds"]:
            guild = self.data["guilds"][guild_name]
            if "boss_progress" in guild and week_id in guild["boss_progress"]:
                return guild["boss_progress"][week_id]["damage_dealt"] >= required_damage
        return False

    def claim_boss_reward(self, guild_name, player_id, week_id, required_damage):
        if guild_name in self.data["guilds"]:
            guild = self.data["guilds"][guild_name]
            if "boss_progress" in guild and week_id in guild["boss_progress"]:
                progress = guild["boss_progress"][week_id]
                if progress["damage_dealt"] >= required_damage and player_id not in progress["claimed_by"]:
                    progress["claimed_by"].append(player_id)
                    self.save()
                    return True
        return False

    def unlock_hq_feature(self, guild_name, feature_type, feature_id, cost):
        if guild_name in self.data["guilds"]:
            guild = self.data["guilds"][guild_name]
            if guild["resources"] >= cost:
                if feature_type == "training_arena":
                    if not guild.get("hq", {}).get("training_arena_unlocked", False):
                        guild["resources"] -= cost
                        guild.setdefault("hq", {})["training_arena_unlocked"] = True
                        self.save()
                        return True
                elif feature_type in ["statues", "banners"]:
                    if feature_id not in guild.setdefault("hq", {}).setdefault(feature_type, []):
                        guild["resources"] -= cost
                        guild["hq"][feature_type].append(feature_id)
                        self.save()
                        return True
        return False

    def get_hq_status(self, guild_name):
        if guild_name in self.data["guilds"]:
            guild = self.data["guilds"][guild_name]
            return guild.get("hq", {
                "statues": [],
                "banners": [],
                "training_arena_unlocked": False
            })
        return None
