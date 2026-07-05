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
            "points": 0
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

    def get_clan_leaderboard(self):
        clans = []
        for name, info in self.data["clans"].items():
            clans.append({
                "name": name,
                "points": info.get("points", 0)
            })
        clans.sort(key=lambda x: x["points"], reverse=True)
        return clans
