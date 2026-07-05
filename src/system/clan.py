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
                self.save()
                return True
        return False

    def leave_clan(self, clan_name, player_id):
        if clan_name in self.data["clans"]:
            clan = self.data["clans"][clan_name]
            if player_id in clan["members"]:
                clan["members"].remove(player_id)
                if len(clan["members"]) == 0:
                    del self.data["clans"][clan_name]
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

    def get_clan_leaderboard(self):
        clans = []
        for name, info in self.data["clans"].items():
            clans.append({
                "name": name,
                "points": info.get("points", 0)
            })
        clans.sort(key=lambda x: x["points"], reverse=True)
        return clans
