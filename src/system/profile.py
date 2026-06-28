import json

class ProfileManager:
    TOTAL_BALLS = 34
    MAX_BONUS_LEVEL = 10

    def __init__(self, filename="profile.json"):
        self.filename = filename
        self.data = self.load()

    def load(self):
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                if "quests" not in data:
                    data["quests"] = []
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "skill_points": 0,
                "unlocked_balls": ["basic"],
                "bonuses": {
                    "bonus_hp": 0,
                    "bonus_speed": 0,
                    "bonus_damage": 0
                },
                "prestige_level": 0,
                "quests": []
            }

    def add_quest(self, quest_description, reward):
        if "quests" not in self.data:
            self.data["quests"] = []
        self.data["quests"].append({
            "description": quest_description,
            "reward": reward,
            "completed": False
        })
        self.save()

    def get_quests(self):
        return self.data.get("quests", [])

    def complete_quest(self, quest_index):
        if "quests" in self.data and 0 <= quest_index < len(self.data["quests"]):
            quest = self.data["quests"][quest_index]
            if not quest.get("completed", False):
                quest["completed"] = True
                self.add_skill_points(quest["reward"])
                return True
        return False

    def save(self):
        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=4)

    def add_skill_points(self, points):
        self.data["skill_points"] += points
        self.save()

    def unlock_ball(self, ball_name, cost):
        if self.data["skill_points"] >= cost and ball_name not in self.data["unlocked_balls"]:
            self.data["skill_points"] -= cost
            self.data["unlocked_balls"].append(ball_name)
            self.save()
            return True
        return False

    def upgrade_bonus(self, bonus_name, cost):
        if bonus_name in self.data["bonuses"] and self.data["skill_points"] >= cost:
            self.data["skill_points"] -= cost
            self.data["bonuses"][bonus_name] += 1
            self.save()
            return True
        return False

    def can_prestige(self):
        unlocked_all_balls = len(self.data.get("unlocked_balls", [])) >= self.TOTAL_BALLS
        maxed_hp = self.data.get("bonuses", {}).get("bonus_hp", 0) >= self.MAX_BONUS_LEVEL
        maxed_speed = self.data.get("bonuses", {}).get("bonus_speed", 0) >= self.MAX_BONUS_LEVEL
        maxed_damage = self.data.get("bonuses", {}).get("bonus_damage", 0) >= self.MAX_BONUS_LEVEL
        return unlocked_all_balls and maxed_hp and maxed_speed and maxed_damage

    def do_prestige(self):
        if self.can_prestige():
            prestige_level = self.data.get("prestige_level", 0) + 1
            self.data = {
                "skill_points": 0,
                "unlocked_balls": ["basic"],
                "bonuses": {
                    "bonus_hp": 0,
                    "bonus_speed": 0,
                    "bonus_damage": 0
                },
                "prestige_level": prestige_level,
                "quests": []
            }
            self.save()
            return True
        return False