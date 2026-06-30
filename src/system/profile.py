import json
import datetime
import base64
import zlib
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
                if "nemeses" not in data:
                    data["nemeses"] = {}
                if "login_streak" not in data:
                    data["login_streak"] = 0
                if "last_login_date" not in data:
                    data["last_login_date"] = ""
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
                "status_effects": [],
                "nemeses": {},
                "login_streak": 0,
                "last_login_date": ""
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
                "status_effects": self.data.get("status_effects", []),
                "nemeses": self.data.get("nemeses", {}),
                "login_streak": self.data.get("login_streak", 0),
                "last_login_date": self.data.get("last_login_date", "")
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


    def generate_loadout_code(self, loadout_name):
        loadout = self.get_loadout(loadout_name)
        if not loadout:
            return None
        try:
            json_str = json.dumps(loadout)
            compressed = zlib.compress(json_str.encode('utf-8'))
            b64 = base64.urlsafe_b64encode(compressed).decode('utf-8')
            return b64.rstrip('=')
        except Exception:
            return None

    def import_loadout_code(self, loadout_name, code):
        try:
            padding = '=' * ((4 - len(code) % 4) % 4)
            b64_bytes = base64.urlsafe_b64decode(code + padding)
            decompressed = zlib.decompress(b64_bytes)
            loadout = json.loads(decompressed.decode('utf-8'))

            # Simple validation to ensure it's a valid loadout dict
            if isinstance(loadout, dict) and "ball_type" in loadout and "trap_variant" in loadout:
                if "loadouts" not in self.data:
                    self.data["loadouts"] = {}
                self.data["loadouts"][loadout_name] = loadout
                self.save()
                return True
            return False
        except Exception:
            return False

    def add_status_effect(self, effect_name):
        if "status_effects" not in self.data:
            self.data["status_effects"] = []
        if effect_name not in self.data["status_effects"]:
            self.data["status_effects"].append(effect_name)
            self.save()

    def add_kill(self, killer_type, victim_type):
        if "nemeses" not in self.data:
            self.data["nemeses"] = {}
        if killer_type not in self.data["nemeses"]:
            self.data["nemeses"][killer_type] = {}
        self.data["nemeses"][killer_type][victim_type] = self.data["nemeses"][killer_type].get(victim_type, 0) + 1
        self.save()

    def is_nemesis(self, killer_type, victim_type):
        if "nemeses" not in self.data:
            return False
        return self.data["nemeses"].get(killer_type, {}).get(victim_type, 0) >= 2

    def process_daily_login(self, current_date_str: str):
        last_date_str = self.data.get("last_login_date", "")
        if last_date_str == current_date_str:
            return {}

        streak = self.data.get("login_streak", 0)

        try:
            current_date = datetime.date.fromisoformat(current_date_str)
            if last_date_str:
                last_date = datetime.date.fromisoformat(last_date_str)
                if (current_date - last_date).days == 1:
                    streak += 1
                else:
                    streak = 1
            else:
                streak = 1
        except Exception:
            streak = 1

        self.data["login_streak"] = streak
        self.data["last_login_date"] = current_date_str

        # Rewards
        sp_reward = 10 * min(streak, 10)
        self.add_skill_points(sp_reward)
        rewards = {"skill_points": sp_reward}

        if streak > 0 and streak % 7 == 0:
            self.data["prestige_tokens"] = self.data.get("prestige_tokens", 0) + 1
            rewards["prestige_tokens"] = 1
            cosmetic_name = f"streak_master_{streak}"
            self.add_cosmetic(cosmetic_name)
            rewards["cosmetics"] = cosmetic_name

        self.save()
        return rewards
