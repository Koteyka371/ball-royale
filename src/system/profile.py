import json
from system.leaderboard import LeaderboardManager

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
                if "loadouts" not in data:
                    data["loadouts"] = {}
                if "quests" not in data:
                    data["quests"] = []
                if "cosmetics" not in data:
                    data["cosmetics"] = []
                if "titles" not in data:
                    data["titles"] = []
                if "status_effects" not in data:
                    data["status_effects"] = []
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
                "loadouts": {},
                "prestige_level": 0,
                "prestige_tokens": 0,
                "prestige_upgrades": {},
                "quests": [],
                "cosmetics": [],
                "titles": [],
                "status_effects": []
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

    def are_mutators_unlocked(self):
        return self.data.get("prestige_level", 0) >= 5

    def can_prestige(self):
        unlocked_all_balls = len(self.data.get("unlocked_balls", [])) >= self.TOTAL_BALLS
        maxed_hp = self.data.get("bonuses", {}).get("bonus_hp", 0) >= self.MAX_BONUS_LEVEL
        maxed_speed = self.data.get("bonuses", {}).get("bonus_speed", 0) >= self.MAX_BONUS_LEVEL
        maxed_damage = self.data.get("bonuses", {}).get("bonus_damage", 0) >= self.MAX_BONUS_LEVEL
        return unlocked_all_balls and maxed_hp and maxed_speed and maxed_damage

    def do_prestige(self):
        if self.can_prestige():
            prestige_level = self.data.get("prestige_level", 0) + 1
            # Calculate prestige tokens based on past stats (skill points, current prestige, maxed bonuses)
            tokens_earned = 5 + prestige_level + (self.data.get("skill_points", 0) // 100)
            current_tokens = self.data.get("prestige_tokens", 0)
            current_upgrades = self.data.get("prestige_upgrades", {})

            self.data = {
                "skill_points": 0,
                "unlocked_balls": ["basic"],
                "bonuses": {
                    "bonus_hp": 0,
                    "bonus_speed": 0,
                    "bonus_damage": 0
                },
                "loadouts": self.data.get("loadouts", {}),
                "prestige_level": prestige_level,
                "prestige_tokens": current_tokens + tokens_earned,
                "prestige_upgrades": current_upgrades,
                "quests": [],
                "cosmetics": self.data.get("cosmetics", []),
                "titles": self.data.get("titles", []),
                "status_effects": self.data.get("status_effects", [])
            }
            self.save()
            lm = LeaderboardManager("leaderboard.json", profile_manager=self)
            lm.update_prestige("local_player", prestige_level)
            lm.check_season()
            return True
        return False


    def buy_prestige_upgrade(self, upgrade_name, cost):
        current_tokens = self.data.get("prestige_tokens", 0)
        upgrades = self.data.get("prestige_upgrades", {})

        if current_tokens >= cost:
            self.data["prestige_tokens"] = current_tokens - cost
            upgrades[upgrade_name] = upgrades.get(upgrade_name, 0) + 1
            self.data["prestige_upgrades"] = upgrades
            self.save()
            return True
        return False

    def add_cosmetic(self, cosmetic_name):
        if "cosmetics" not in self.data:
            self.data["cosmetics"] = []
        if cosmetic_name not in self.data["cosmetics"]:
            self.data["cosmetics"].append(cosmetic_name)
            self.save()

    def add_title(self, title_name):
        if "titles" not in self.data:
            self.data["titles"] = []
        if title_name not in self.data["titles"]:
            self.data["titles"].append(title_name)
            self.save()

    def save_loadout(self, loadout_name, ball_type, trap_variant, preferred_bonuses=None, cosmetic=None, title=None):
        if "loadouts" not in self.data:
            self.data["loadouts"] = {}
        if preferred_bonuses is None:
            preferred_bonuses = {}
        self.data["loadouts"][loadout_name] = {
            "ball_type": ball_type,
            "trap_variant": trap_variant,
            "preferred_bonuses": preferred_bonuses,
            "cosmetic": cosmetic,
            "title": title
        }
        self.save()

    def set_default_loadout(self, loadout_name):
        if "loadouts" in self.data and loadout_name in self.data["loadouts"]:
            self.data["default_loadout"] = loadout_name
            self.save()
            return True
        return False

    def get_default_loadout(self):
        return self.data.get("default_loadout")

    def get_loadout(self, loadout_name):
        return self.data.get("loadouts", {}).get(loadout_name)

    def get_all_loadouts(self):
        return self.data.get("loadouts", {})

    def delete_loadout(self, loadout_name):
        if "loadouts" in self.data and loadout_name in self.data["loadouts"]:
            del self.data["loadouts"][loadout_name]
            self.save()
            return True
        return False

    def add_status_effect(self, effect_name):
        if "status_effects" not in self.data:
            self.data["status_effects"] = []
        if effect_name not in self.data["status_effects"]:
            self.data["status_effects"].append(effect_name)
            self.save()
