import json

class ClanManager:
    def __init__(self, filename="clans.json"):
        self.filename = filename
        self.data = self.load()

    def load(self):
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                if "clans" not in data:
                    data["clans"] = {}
                for clan in data["clans"].values():
                    if "perks" not in clan:
                        clan["perks"] = []
                    if "decorations" not in clan:
                        clan["decorations"] = []
                    if "hub" not in clan:
                        clan["hub"] = []
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            return {"clans": {}}

    def save(self):
        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=4)

    def create_clan(self, clan_name, creator_id):
        if clan_name in self.data["clans"]:
            return False

        self.data["clans"][clan_name] = {
            "members": [creator_id],
            "roles": {creator_id: "leader"},
            "stash": {},
            "quests": [],
            "points": 0,
            "territories": [],
            "perks": [],
            "decorations": [],
            "hub": []
        }
        self.save()
        return True

    def join_clan(self, clan_name, player_id):
        if clan_name in self.data["clans"]:
            clan = self.data["clans"][clan_name]
            if player_id not in clan["members"]:
                clan["members"].append(player_id)
                if "roles" not in clan:
                    clan["roles"] = {}
                clan["roles"][player_id] = "member"
                self.save()
                return True
        return False

    def leave_clan(self, clan_name, player_id):
        if clan_name in self.data["clans"]:
            clan = self.data["clans"][clan_name]
            if player_id in clan["members"]:
                clan["members"].remove(player_id)
                if "roles" in clan and player_id in clan["roles"]:
                    del clan["roles"][player_id]
                if len(clan["members"]) == 0:
                    del self.data["clans"][clan_name]
                self.save()
                return True
        return False

    def set_member_role(self, clan_name, admin_id, target_id, new_role):
        if clan_name in self.data["clans"]:
            clan = self.data["clans"][clan_name]
            if "roles" not in clan:
                clan["roles"] = {m: "member" for m in clan["members"]}
                if clan["members"]:
                    clan["roles"][clan["members"][0]] = "leader"

            admin_role = clan["roles"].get(admin_id, "member")
            if admin_role == "leader" and target_id in clan["members"]:
                clan["roles"][target_id] = new_role
                self.save()
                return True
        return False

    def deposit_to_stash(self, clan_name, player_id, item_name, amount):
        if amount <= 0:
            return False
        if clan_name in self.data["clans"]:
            clan = self.data["clans"][clan_name]
            if player_id in clan["members"]:
                if "stash" not in clan:
                    clan["stash"] = {}
                if item_name not in clan["stash"]:
                    clan["stash"][item_name] = 0
                clan["stash"][item_name] += amount
                self.save()
                return True
        return False

    def withdraw_from_stash(self, clan_name, player_id, item_name, amount):
        if amount <= 0:
            return False
        if clan_name in self.data["clans"]:
            clan = self.data["clans"][clan_name]
            if player_id in clan["members"]:
                if "roles" not in clan:
                    clan["roles"] = {m: "member" for m in clan["members"]}
                    if clan["members"]:
                        clan["roles"][clan["members"][0]] = "leader"

                role = clan["roles"].get(player_id, "member")
                if role in ["leader", "officer"]:
                    if "stash" not in clan:
                        clan["stash"] = {}
                    if clan["stash"].get(item_name, 0) >= amount:
                        clan["stash"][item_name] -= amount
                        if clan["stash"][item_name] == 0:
                            del clan["stash"][item_name]
                        self.save()
                        return True
        return False

    def add_clan_quest(self, clan_name, description, required_progress):
        if clan_name in self.data["clans"]:
            clan = self.data["clans"][clan_name]
            clan["quests"].append({
                "description": description,
                "required": required_progress,
                "current": 0,
                "completed": False
            })
            self.save()
            return True
        return False

    def progress_clan_quest(self, clan_name, quest_index, amount):
        if clan_name in self.data["clans"]:
            clan = self.data["clans"][clan_name]
            if 0 <= quest_index < len(clan["quests"]):
                quest = clan["quests"][quest_index]
                if not quest["completed"]:
                    quest["current"] += amount
                    if quest["current"] >= quest["required"]:
                        quest["current"] = quest["required"]
                        quest["completed"] = True
                        clan["points"] += 10
                    self.save()
                    return True
        return False

    def get_clan_quests(self, clan_name):
        if clan_name in self.data["clans"]:
            return self.data["clans"][clan_name]["quests"]
        return []

    def add_clan_points(self, clan_name, amount):
        if clan_name in self.data["clans"]:
            self.data["clans"][clan_name]["points"] += amount
            self.save()
            return True
        return False

    def unlock_cosmetic(self, clan_name, cosmetic):
        if clan_name in self.data["clans"]:
            if "cosmetics" not in self.data["clans"][clan_name]:
                self.data["clans"][clan_name]["cosmetics"] = []
            if cosmetic not in self.data["clans"][clan_name]["cosmetics"]:
                self.data["clans"][clan_name]["cosmetics"].append(cosmetic)
                self.save()
                return True
        return False


    def unlock_buff(self, clan_name, buff_name):
        if clan_name in self.data["clans"]:
            if "buffs" not in self.data["clans"][clan_name]:
                self.data["clans"][clan_name]["buffs"] = []
            if buff_name not in self.data["clans"][clan_name]["buffs"]:
                self.data["clans"][clan_name]["buffs"].append(buff_name)
                self.save()
                return True
        return False


    def capture_territory(self, clan_name, territory_name):
        if clan_name in self.data["clans"]:
            # Remove territory from old owner if any
            for c_name, c_data in self.data["clans"].items():
                if "territories" in c_data and territory_name in c_data["territories"]:
                    c_data["territories"].remove(territory_name)

            if "territories" not in self.data["clans"][clan_name]:
                self.data["clans"][clan_name]["territories"] = []

            if territory_name not in self.data["clans"][clan_name]["territories"]:
                self.data["clans"][clan_name]["territories"].append(territory_name)
                self.save()
                return True
        return False

    def get_clan_territories(self, clan_name):
        if clan_name in self.data["clans"]:
            return self.data["clans"][clan_name].get("territories", [])
        return []

    def get_territory_owner(self, territory_name):
        for clan_name, clan_data in self.data["clans"].items():
            if territory_name in clan_data.get("territories", []):
                return clan_name
        return None

    def get_clan_leaderboard(self):
        clans = []
        for name, info in self.data["clans"].items():
            clans.append({
                "name": name,
                "points": info.get("points", 0)
            })
        clans.sort(key=lambda x: x["points"], reverse=True)
        return clans

    def unlock_perk(self, clan_name, perk_name, cost, required_perk=None):
        if clan_name in self.data["clans"]:
            clan = self.data["clans"][clan_name]
            if clan.get("points", 0) >= cost:
                if perk_name not in clan.get("perks", []):
                    if required_perk is None or required_perk in clan.get("perks", []):
                        clan["points"] -= cost
                        clan.setdefault("perks", []).append(perk_name)
                        self.save()
                        return True
        return False

    def get_clan_perks(self, clan_name):
        if clan_name in self.data["clans"]:
            return self.data["clans"][clan_name].get("perks", [])
        return []

    def unlock_decoration(self, clan_name, decoration_name):
        if clan_name in self.data["clans"]:
            clan = self.data["clans"][clan_name]
            if "decorations" not in clan:
                clan["decorations"] = []
            if decoration_name not in clan["decorations"]:
                clan["decorations"].append(decoration_name)
                self.save()
                return True
        return False

    def place_decoration(self, clan_name, decoration_name, x, y):
        if clan_name in self.data["clans"]:
            clan = self.data["clans"][clan_name]
            if decoration_name in clan.get("decorations", []):
                if "hub" not in clan:
                    clan["hub"] = []
                # Remove existing at this position
                clan["hub"] = [d for d in clan["hub"] if d.get("x") != x or d.get("y") != y]
                clan["hub"].append({"decoration": decoration_name, "x": x, "y": y})
                self.save()
                return True
        return False

    def remove_decoration(self, clan_name, x, y):
        if clan_name in self.data["clans"]:
            clan = self.data["clans"][clan_name]
            if "hub" in clan:
                initial_len = len(clan["hub"])
                clan["hub"] = [d for d in clan["hub"] if d.get("x") != x or d.get("y") != y]
                if len(clan["hub"]) < initial_len:
                    self.save()
                    return True
        return False

    def get_hub_buffs(self, clan_name):
        buffs = []
        if clan_name in self.data["clans"]:
            clan = self.data["clans"][clan_name]
            for d in clan.get("hub", []):
                dec_name = d.get("decoration", "")
                if dec_name == "Champion_Trophy":
                    buffs.append("Tournament_Champion_Aura")
                elif dec_name == "Speed_Statue":
                    buffs.append("Hub_Speed_Boost")
                elif dec_name == "Health_Fountain":
                    buffs.append("Hub_Health_Regen")
        return list(set(buffs))

    def start_weekly_tournament(self):
        self.data["tournament_active"] = True
        self.data["tournament_scores"] = {clan: 0 for clan in self.data["clans"]}
        self.save()
        return True

    def add_tournament_points(self, clan_name, points):
        if self.data.get("tournament_active", False):
            if "tournament_scores" not in self.data:
                self.data["tournament_scores"] = {}
            if clan_name in self.data["clans"]:
                if clan_name not in self.data["tournament_scores"]:
                    self.data["tournament_scores"][clan_name] = 0
                self.data["tournament_scores"][clan_name] += points
                self.save()
                return True
        return False

    def end_weekly_tournament(self):
        if not self.data.get("tournament_active", False):
            return False

        scores = self.data.get("tournament_scores", {})
        ranked_clans = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        for i, (clan_name, score) in enumerate(ranked_clans):
            if clan_name not in self.data["clans"]:
                continue

            if i == 0:
                self.add_clan_points(clan_name, 5000)
                self.unlock_cosmetic(clan_name, "Weekly_Champion_Aura")
                self.unlock_buff(clan_name, "Currency_Boost_Tier3")
            elif i == 1:
                self.add_clan_points(clan_name, 3000)
                self.unlock_buff(clan_name, "Currency_Boost_Tier2")
            elif i == 2:
                self.add_clan_points(clan_name, 2000)
                self.unlock_buff(clan_name, "Currency_Boost_Tier1")

        self.data["tournament_active"] = False
        self.data["tournament_scores"] = {}
        self.save()
        return True
